// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.

use me60os_core::isochronous_oscillator::IsochronousOscillator;
use me60os_core::liquid_memory::LiquidMemory;
use me60os_core::qhc::QhcTensor;
use me60os_core::quantum_core::IsochronousClock;
use me60os_core::quantum_core::S60PID;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::shm_bridge::PySharedBuffer;
use me60os_core::spa::SPA;
use serde::{Deserialize, Serialize};
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Write};
use std::os::fd::AsRawFd;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

const SNAPSHOT_VERSION: u32 = 2;
const LEGACY_SNAPSHOT_VERSION: u32 = 1;
const PID_HISTORY_TICKS: usize = 68;
const LANE_A_SHM: &str = "/me60os_lattice";
const LANE_B_SHM: &str = "/me60os_lattice_b";
const FRACTAL_SEEDS_SHM: &str = "/me60os_fractal_seeds";
const DTC_CLOCK_SHM: &str = "/me60os_dtc_clock";
const DTC_CLOCK_SHM_BYTES: usize = 24;
const DTC_CLOCK_MAGIC: u32 = 0x4D45_3643;
const DTC_CLOCK_VERSION: u32 = 1;
const FRACTAL_SEEDS_CAPACITY: usize = 1024;
const FRACTAL_HEADER_BYTES: usize = 64;
const FRACTAL_SEED_BYTES: usize = 32;
pub const DTC_TICK_INTERVAL_NS: u64 = 23_939_835;

#[derive(Clone, Serialize)]
pub struct CrystalRuntimeStatus {
    pub active: bool,
    pub node_count_per_lane: usize,
    pub lane_a: &'static str,
    pub lane_b: &'static str,
    pub shm_active: bool,
    pub lane_a_shm: &'static str,
    pub lane_b_shm: &'static str,
    pub shm_bytes_per_lane: usize,
    pub shm_sync_count: u64,
    pub last_shm_sync_unix_ms: u64,
    pub yhwh_qhc_active: bool,
    pub qhc_tick: u64,
    pub qhc_phase_modulation: u8,
    pub qhc_last_drift_correction_ns: u64,
    pub dtc_frequency_millihz: u64,
    pub non_markovian_kernel_active: bool,
    pub non_markovian_history_capacity_ticks: usize,
    pub checkpoint_active: bool,
    pub liquid_memory_active: bool,
    pub liquid_memory_shm_key: &'static str,
    pub liquid_memory_checkpoint_bytes: usize,
    pub liquid_memory_sync_count: u64,
    pub fractal_seed_shm_active: bool,
    pub fractal_seed_capacity: usize,
    pub fractal_seeds_published: u64,
    pub dtc_oscillator_active: bool,
    pub dtc_ticks: u64,
    pub dtc_tick_interval_ns: u64,
}

#[derive(Serialize, Deserialize)]
struct CrystalSnapshot {
    version: u32,
    node_count: usize,
    qhc_tick: u64,
    lane_a: Vec<CrystalNodeState>,
    lane_b: Vec<CrystalNodeState>,
    pid_a: S60PID,
    pid_b: S60PID,
}

#[derive(Serialize, Deserialize)]
struct CrystalNodeState {
    index: usize,
    amplitude_raw: i64,
    phase_raw: i64,
}

#[derive(Deserialize)]
struct LegacyCrystalSnapshot {
    version: u32,
    #[serde(rename = "node_count")]
    _node_count: usize,
    qhc_tick: u64,
    lane_a: ResonantMatrix,
    lane_b: ResonantMatrix,
    pid_a: S60PID,
    pid_b: S60PID,
}

#[derive(Deserialize)]
struct SnapshotHeader {
    version: u32,
    node_count: usize,
}

/// Long-lived dual crystal runtime. Lane A is the security/eBPF lane and is
/// exported at MycNet's established SHM path. Lane B is the observability lane.
pub struct CrystalRuntime {
    lane_a: ResonantMatrix,
    lane_b: ResonantMatrix,
    pid_a: S60PID,
    pid_b: S60PID,
    qhc: QhcTensor,
    liquid_memory: LiquidMemory,
    liquid_memory_checkpoint_bytes: usize,
    liquid_memory_sync_count: u64,
    dtc_clock: IsochronousClock,
    qhc_tick: u64,
    last_phase_modulation: u8,
    last_drift_correction_ns: u64,
    last_tick_interval_ns: u64,
    shm_a: Option<PySharedBuffer>,
    shm_b: Option<PySharedBuffer>,
    fractal_seeds_shm: Option<PySharedBuffer>,
    fractal_seed_head: u64,
    fractal_seeds_published: u64,
    _shm_lock: Option<File>,
    shm_sync_count: u64,
    last_shm_sync_unix_ms: u64,
    snapshot_path: PathBuf,
}

impl CrystalRuntime {
    pub fn new(nodes: usize) -> Result<Self, String> {
        Self::build(nodes, true)
    }

    pub fn in_memory(nodes: usize) -> Self {
        Self::build(nodes, false).expect("in-memory crystal runtime initialization")
    }

    fn build(nodes: usize, create_shm: bool) -> Result<Self, String> {
        if nodes == 0 {
            return Err("crystal runtime requires at least one node per lane".into());
        }

        let snapshot_path = snapshot_path(nodes)?;
        let shm_lock = if create_shm {
            Some(acquire_shm_writer_lock()?)
        } else {
            None
        };
        let (lane_a, lane_b, pid_a, pid_b, qhc_tick) = load_snapshot(&snapshot_path, nodes)
            .unwrap_or_else(|| {
                (
                    ResonantMatrix::new(nodes),
                    ResonantMatrix::new(nodes),
                    new_pid(),
                    new_pid(),
                    0,
                )
            });

        let shm_bytes = nodes
            .checked_mul(std::mem::size_of::<IsochronousOscillator>())
            .ok_or_else(|| "crystal SHM size overflow".to_string())?;
        let (shm_a, shm_b, fractal_seeds_shm, fractal_seed_head) = if create_shm {
            let a = PySharedBuffer::new(LANE_A_SHM.to_string(), shm_bytes, true)
                .map_err(|e| format!("create {LANE_A_SHM}: {e}"))?;
            let b = PySharedBuffer::new(LANE_B_SHM.to_string(), shm_bytes, true)
                .map_err(|e| format!("create {LANE_B_SHM}: {e}"))?;
            let seed_bytes = FRACTAL_HEADER_BYTES + FRACTAL_SEEDS_CAPACITY * FRACTAL_SEED_BYTES;
            let seeds = PySharedBuffer::new(FRACTAL_SEEDS_SHM.to_string(), seed_bytes, true)
                .map_err(|e| format!("create {FRACTAL_SEEDS_SHM}: {e}"))?;
            let head = initialize_fractal_ring(&seeds)?;
            (Some(a), Some(b), Some(seeds), head)
        } else {
            (None, None, None, 0)
        };

        let mut runtime = Self {
            lane_a,
            lane_b,
            pid_a,
            pid_b,
            qhc: QhcTensor::new(),
            liquid_memory: LiquidMemory::new(1024),
            liquid_memory_checkpoint_bytes: 0,
            liquid_memory_sync_count: 0,
            dtc_clock: IsochronousClock::new_internal(),
            qhc_tick,
            last_phase_modulation: 0,
            last_drift_correction_ns: 0,
            last_tick_interval_ns: DTC_TICK_INTERVAL_NS,
            shm_a,
            shm_b,
            fractal_seeds_shm,
            fractal_seed_head,
            fractal_seeds_published: 0,
            _shm_lock: shm_lock,
            shm_sync_count: 0,
            last_shm_sync_unix_ms: 0,
            snapshot_path,
        };
        runtime.sync_shm()?;
        Ok(runtime)
    }

    pub fn node_count(&self) -> usize {
        self.lane_a.count_nodes()
    }

    /// Advances the shared DTC/QHC pulse. The Tokio scheduler owns the pulse
    /// deadline; this method advances the logical DTC counter without sleeping.
    pub fn tick_dtc(&mut self) -> Result<u64, String> {
        self.dtc_clock.ticks = self.dtc_clock.ticks.saturating_add(1);
        self.qhc_tick = self.qhc_tick.saturating_add(1);
        self.last_phase_modulation = self.qhc.get_phase_modulation(self.qhc_tick);
        self.last_drift_correction_ns = self.qhc.calculate_drift_correction(self.qhc_tick);
        self.last_tick_interval_ns = self.qhc.get_tick_interval_ns(self.qhc_tick);

        let qhc = &self.qhc;
        let tick = self.qhc_tick;
        for crystal in self.lane_a.crystals.iter_mut() {
            crystal.phase = qhc.apply_modulation(crystal.phase, tick);
        }
        for crystal in self.lane_b.crystals.iter_mut() {
            crystal.phase = qhc.apply_modulation(crystal.phase, tick);
        }

        // Publish each YHWH phase through MycNet's existing SHM ring. At the
        // 68-tick correction boundary, publish both lanes and their corrected
        // shared-memory snapshot as one QHC synchronization pulse.
        let center = self.node_count() / 2;
        self.publish_fractal_seed(true, center);
        if self.last_drift_correction_ns > 0 {
            self.publish_fractal_seed(false, center);
            self.sync_shm()?;
        }

        Ok(self.last_tick_interval_ns)
    }

    pub fn inject_security_spa(&mut self, index: usize, amplitude: SPA) {
        self.lane_a.inject_spa(index, amplitude);
        self.publish_fractal_seed(true, index);
    }

    /// Import remote drive without immediately echoing it into MyCNet's SHM ring.
    /// Periodic snapshots still export the resulting crystal state.
    pub fn inject_remote_security_spa(&mut self, index: usize, amplitude: SPA) -> Result<i64, &'static str> {
        let crystal = self.lane_a.crystals.get_mut(index).ok_or("crystal index out of range")?;
        let raw = crystal.amplitude.to_raw().checked_add(amplitude.to_raw())
            .ok_or("SPA amplitude overflow")?;
        crystal.amplitude = SPA::from_raw(raw);
        Ok(raw)
    }

    pub fn inject_security(&mut self, index: usize, pressure: i64) {
        self.lane_a.inject(index, pressure);
    }

    pub fn inject_security_pai(&mut self, index: usize, value: i64, denominator: u32) {
        self.lane_a.inject_pai(index, value, denominator);
    }

    pub fn inject_observability_spa(&mut self, index: usize, amplitude: SPA) {
        self.lane_b.inject_spa(index, amplitude);
        self.publish_fractal_seed(false, index);
    }

    pub fn inject_observability(&mut self, index: usize, pressure: i64) {
        self.lane_b.inject(index, pressure);
        self.publish_fractal_seed(false, index);
    }

    pub fn inject_observability_pai(&mut self, index: usize, value: i64, denominator: u32) {
        self.lane_b.inject_pai(index, value, denominator);
        self.publish_fractal_seed(false, index);
    }

    fn publish_fractal_seed(&mut self, security_lane: bool, index: usize) {
        let Some(buffer) = self.fractal_seeds_shm.as_ref() else {
            return;
        };
        let lane = if security_lane {
            &self.lane_a
        } else {
            &self.lane_b
        };
        let Some(crystal) = lane.crystals.get(index) else {
            return;
        };
        let token_id = (self.fractal_seed_head as u32).wrapping_add(index as u32);
        // MycNet runs a three-ring, 37-node hex lattice. Map every Sentinel
        // crystal deterministically into that receiver's valid coordinate set.
        let (q, r) = mycnet_hex_coordinate(index);
        let s = -q - r;
        let mut bytes = [0_u8; FRACTAL_SEED_BYTES];
        bytes[0..4].copy_from_slice(&token_id.to_le_bytes());
        bytes[4..8].copy_from_slice(&q.to_le_bytes());
        bytes[8..12].copy_from_slice(&r.to_le_bytes());
        bytes[12..16].copy_from_slice(&s.to_le_bytes());
        bytes[16..24].copy_from_slice(&crystal.amplitude.to_raw().to_le_bytes());
        bytes[24] = crystal.phase.components[1].rem_euclid(60) as u8;
        bytes[25] = self.last_phase_modulation;
        bytes[26..28].copy_from_slice(&1_u16.to_le_bytes());
        let crc = crc16_ccitt(&bytes[..28]);
        bytes[28..30].copy_from_slice(&crc.to_le_bytes());
        let slot = (self.fractal_seed_head as usize) % FRACTAL_SEEDS_CAPACITY;
        let offset = FRACTAL_HEADER_BYTES + slot * FRACTAL_SEED_BYTES;
        if let Err(error) = buffer.write_native(offset, &bytes) {
            tracing::error!(%error, "Failed to publish MycNet fractal seed");
            return;
        }
        self.fractal_seed_head = self.fractal_seed_head.saturating_add(1);
        if let Err(error) = buffer.store_u64_release(8, self.fractal_seed_head) {
            tracing::error!(%error, "Failed to advance MycNet fractal seed ring");
            return;
        }
        self.fractal_seeds_published = self.fractal_seeds_published.saturating_add(1);
    }

    /// Applies the S60PID non-Markovian cross-lane correction, advances both
    /// crystal meshes, then publishes both exact repr(C) arrays to POSIX SHM.
    pub fn step(&mut self) -> Result<(), String> {
        let amplitudes_a = self.lane_a.get_amplitudes();
        let amplitudes_b = self.lane_b.get_amplitudes();
        let energy_a = self.lane_a.total_energy().to_raw();
        let energy_b = self.lane_b.total_energy().to_raw();

        let mut errors_a = Vec::with_capacity(PID_HISTORY_TICKS);
        let mut errors_b = Vec::with_capacity(PID_HISTORY_TICKS);
        let stride = (self.node_count() / PID_HISTORY_TICKS).max(1);
        for index in (0..self.node_count())
            .step_by(stride)
            .take(PID_HISTORY_TICKS)
        {
            let delta = amplitudes_b[index]
                .to_raw()
                .saturating_sub(amplitudes_a[index].to_raw());
            errors_a.push(delta);
            errors_b.push(delta.saturating_neg());
        }

        let dt_raw = SPA::new(0, 30, 0, 0, 0).to_raw(); // exact half-second control step
        self.pid_a.setpoint = SPA::from_raw(energy_b);
        self.pid_b.setpoint = SPA::from_raw(energy_a);
        let control_a = self
            .pid_a
            .update_with_history_internal(energy_a, dt_raw, errors_a);
        let control_b = self
            .pid_b
            .update_with_history_internal(energy_b, dt_raw, errors_b);
        let divisor = (self.node_count() as i128 * 60).max(1);
        let correction_a = (control_a as i128 / divisor) as i64;
        let correction_b = (control_b as i128 / divisor) as i64;
        let center = self.node_count() / 2;
        self.lane_a.inject_spa(center, SPA::from_raw(correction_a));
        self.lane_b.inject_spa(center, SPA::from_raw(correction_b));

        self.lane_a.step();
        self.lane_b.step();
        self.sync_shm()
    }

    fn sync_shm(&mut self) -> Result<(), String> {
        if let Some(buffer) = self.shm_a.as_mut() {
            self.lane_a.sync_to_shm(buffer)?;
        }
        if let Some(buffer) = self.shm_b.as_mut() {
            self.lane_b.sync_to_shm(buffer)?;
        }
        if self.shm_a.is_some() && self.shm_b.is_some() {
            self.shm_sync_count = self.shm_sync_count.saturating_add(1);
            self.last_shm_sync_unix_ms = now_unix_ms();
        }
        Ok(())
    }

    pub fn persist(&mut self) -> Result<(), String> {
        let snapshot = CrystalSnapshot {
            version: SNAPSHOT_VERSION,
            node_count: self.node_count(),
            qhc_tick: self.qhc_tick,
            lane_a: sparse_lane_state(&self.lane_a),
            lane_b: sparse_lane_state(&self.lane_b),
            pid_a: self.pid_a.clone(),
            pid_b: self.pid_b.clone(),
        };
        let bytes =
            serde_json::to_vec(&snapshot).map_err(|e| format!("serialize crystal state: {e}"))?;
        let mut encoder = flate2::write::GzEncoder::new(Vec::new(), flate2::Compression::fast());
        encoder
            .write_all(&bytes)
            .map_err(|e| format!("compress crystal checkpoint: {e}"))?;
        let compressed = encoder
            .finish()
            .map_err(|e| format!("finish crystal checkpoint: {e}"))?;
        self.liquid_memory
            .store("crystal-runtime-checkpoint", &compressed)?;
        let cached = self
            .liquid_memory
            .retrieve("crystal-runtime-checkpoint")?
            .ok_or_else(|| "liquid memory did not retain the crystal checkpoint".to_string())?;
        if cached != compressed {
            return Err("liquid memory checkpoint integrity mismatch".into());
        }
        self.liquid_memory_checkpoint_bytes = compressed.len();
        self.liquid_memory_sync_count = self.liquid_memory_sync_count.saturating_add(1);
        let next_path = self.snapshot_path.with_extension("gz.next");
        fs::write(&next_path, compressed).map_err(|e| format!("write crystal checkpoint: {e}"))?;
        fs::rename(&next_path, &self.snapshot_path)
            .map_err(|e| format!("publish crystal checkpoint: {e}"))
    }

    pub fn status(&self) -> CrystalRuntimeStatus {
        let nodes = self.node_count();
        CrystalRuntimeStatus {
            active: true,
            node_count_per_lane: nodes,
            lane_a: "security",
            lane_b: "observability",
            shm_active: self.shm_a.is_some() && self.shm_b.is_some(),
            lane_a_shm: LANE_A_SHM,
            lane_b_shm: LANE_B_SHM,
            shm_bytes_per_lane: nodes * std::mem::size_of::<IsochronousOscillator>(),
            shm_sync_count: self.shm_sync_count,
            last_shm_sync_unix_ms: self.last_shm_sync_unix_ms,
            yhwh_qhc_active: true,
            qhc_tick: self.qhc_tick,
            qhc_phase_modulation: self.last_phase_modulation,
            qhc_last_drift_correction_ns: self.last_drift_correction_ns,
            non_markovian_kernel_active: true,
            non_markovian_history_capacity_ticks: PID_HISTORY_TICKS,
            checkpoint_active: true,
            liquid_memory_active: true,
            liquid_memory_shm_key: "crystal-runtime-checkpoint",
            liquid_memory_checkpoint_bytes: self.liquid_memory_checkpoint_bytes,
            liquid_memory_sync_count: self.liquid_memory_sync_count,
            fractal_seed_shm_active: self.fractal_seeds_shm.is_some(),
            fractal_seed_capacity: FRACTAL_SEEDS_CAPACITY,
            fractal_seeds_published: self.fractal_seeds_published,
            dtc_oscillator_active: true,
            dtc_ticks: self.dtc_clock.ticks,
            dtc_tick_interval_ns: self.last_tick_interval_ns,
            dtc_frequency_millihz: 1_000_000_000_000_u64 / self.last_tick_interval_ns,
        }
    }

    pub fn total_energy_raw(&self) -> i64 {
        self.lane_a.total_energy().to_raw()
    }

    pub fn lane_b_energy_raw(&self) -> i64 {
        self.lane_b.total_energy().to_raw()
    }

    pub fn amplitudes_raw(&self) -> Vec<i64> {
        self.lane_a
            .get_amplitudes()
            .iter()
            .map(|v| v.to_raw())
            .collect()
    }

    pub fn phases_raw(&self) -> Vec<i64> {
        self.lane_a
            .get_phases()
            .iter()
            .map(|v| v.to_raw())
            .collect()
    }

    pub fn reset(&mut self) {
        self.lane_a.reset();
        self.lane_b.reset();
        self.pid_a.reset_internal();
        self.pid_b.reset_internal();
        self.qhc_tick = 0;
        let _ = self.sync_shm();
    }
}

fn new_pid() -> S60PID {
    S60PID::new(
        SPA::new(0, 30, 0, 0, 0).to_raw(),
        SPA::new(0, 10, 0, 0, 0).to_raw(),
        SPA::new(0, 5, 0, 0, 0).to_raw(),
        0,
    )
}

fn crc16_ccitt(bytes: &[u8]) -> u16 {
    let mut crc = 0xffff_u16;
    for byte in bytes {
        crc ^= (*byte as u16) << 8;
        for _ in 0..8 {
            crc = if crc & 0x8000 != 0 {
                (crc << 1) ^ 0x1021
            } else {
                crc << 1
            };
        }
    }
    crc
}

fn mycnet_hex_coordinate(index: usize) -> (i32, i32) {
    let mut offset = index % 37;
    for q in -3_i32..=3 {
        let r_min = (-3_i32).max(-q - 3);
        let r_max = 3_i32.min(-q + 3);
        for r in r_min..=r_max {
            if offset == 0 {
                return (q, r);
            }
            offset -= 1;
        }
    }
    (0, 0)
}

fn sparse_lane_state(matrix: &ResonantMatrix) -> Vec<CrystalNodeState> {
    matrix
        .crystals
        .iter()
        .enumerate()
        .filter(|(_, crystal)| crystal.amplitude != SPA::zero() || crystal.phase != SPA::zero())
        .map(|(index, crystal)| CrystalNodeState {
            index,
            amplitude_raw: crystal.amplitude.to_raw(),
            phase_raw: crystal.phase.to_raw(),
        })
        .collect()
}

fn restore_sparse_lane(nodes: usize, states: Vec<CrystalNodeState>) -> Option<ResonantMatrix> {
    let mut matrix = ResonantMatrix::new(nodes);
    for state in states {
        let crystal = matrix.crystals.get_mut(state.index)?;
        crystal.amplitude = SPA::from_raw(state.amplitude_raw);
        crystal.phase = SPA::from_raw(state.phase_raw);
    }
    Some(matrix)
}

fn snapshot_path(nodes: usize) -> Result<PathBuf, String> {
    let state_dir = std::env::var_os("SENTINEL_CRYSTAL_STATE_DIR")
        .map(PathBuf::from)
        .or_else(|| {
            std::env::var_os("HOME")
                .map(PathBuf::from)
                .map(|home| home.join(".local/state/sentinel"))
        })
        .ok_or_else(|| "neither SENTINEL_CRYSTAL_STATE_DIR nor HOME is set".to_string())?;
    fs::create_dir_all(&state_dir).map_err(|e| format!("create crystal state directory: {e}"))?;
    Ok(state_dir.join(format!("crystal-runtime-{nodes}.json.gz")))
}

fn load_snapshot(
    path: &Path,
    nodes: usize,
) -> Option<(ResonantMatrix, ResonantMatrix, S60PID, S60PID, u64)> {
    let bytes = fs::read(path)
        .or_else(|_| fs::read(path.with_extension("json")))
        .ok()?;
    let bytes = if bytes.starts_with(&[0x1f, 0x8b]) {
        let mut decoded = Vec::new();
        flate2::read::GzDecoder::new(bytes.as_slice())
            .read_to_end(&mut decoded)
            .ok()?;
        decoded
    } else {
        bytes
    };
    let header: SnapshotHeader = match serde_json::from_slice(&bytes) {
        Ok(header) => header,
        Err(error) => {
            tracing::error!(path = %path.display(), %error, "Crystal checkpoint is invalid; preserving it and starting fresh");
            return None;
        }
    };
    if header.node_count != nodes {
        tracing::warn!(path = %path.display(), snapshot_nodes = header.node_count, requested_nodes = nodes, "Crystal checkpoint does not match runtime size; starting fresh");
        return None;
    }
    let restored = match header.version {
        SNAPSHOT_VERSION => {
            let snapshot: CrystalSnapshot = serde_json::from_slice(&bytes).ok()?;
            let lane_a = restore_sparse_lane(nodes, snapshot.lane_a)?;
            let lane_b = restore_sparse_lane(nodes, snapshot.lane_b)?;
            (
                lane_a,
                lane_b,
                snapshot.pid_a,
                snapshot.pid_b,
                snapshot.qhc_tick,
            )
        }
        LEGACY_SNAPSHOT_VERSION => {
            let snapshot: LegacyCrystalSnapshot = serde_json::from_slice(&bytes).ok()?;
            if snapshot.version != LEGACY_SNAPSHOT_VERSION
                || snapshot.lane_a.count_nodes() != nodes
                || snapshot.lane_b.count_nodes() != nodes
            {
                tracing::warn!(path = %path.display(), nodes, "Legacy crystal checkpoint has invalid lane sizes; starting fresh");
                return None;
            }
            (
                snapshot.lane_a,
                snapshot.lane_b,
                snapshot.pid_a,
                snapshot.pid_b,
                snapshot.qhc_tick,
            )
        }
        version => {
            tracing::warn!(path = %path.display(), version, "Unsupported crystal checkpoint version; starting fresh");
            return None;
        }
    };
    tracing::info!(path = %path.display(), nodes, tick = restored.4, "Restored dual crystal checkpoint");
    Some(restored)
}

/// Called only while holding the exclusive CrystalRuntime writer lock.
/// The POSIX object survives process exit, so readers keep the same mapping.
fn initialize_fractal_ring(seeds: &PySharedBuffer) -> Result<u64, String> {
    const SIGNATURE: u64 = (1_u64 << 32) | 0x5346_5231;
    let signature = seeds.load_u64_acquire(0)?;
    if signature == SIGNATURE {
        return seeds.load_u64_acquire(8);
    }
    if signature != 0 {
        return Err("unsupported fractal ring header; refusing to reset published head".into());
    }
    seeds.write_native(0, &0x5346_5231_u32.to_le_bytes())?;
    seeds.write_native(4, &1_u32.to_le_bytes())?;
    seeds.store_u64_release(8, 0)?;
    seeds.store_u64_release(16, 0)?;
    seeds.write_native(24, &[0_u8; 40])?;
    Ok(0)
}

fn now_unix_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_millis().min(u128::from(u64::MAX)) as u64)
        .unwrap_or(0)
}

fn acquire_shm_writer_lock() -> Result<File, String> {
    let lock_path = Path::new("/dev/shm/me60os_crystal_runtime.lock");
    let lock = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(&lock_path)
        .map_err(|error| {
            format!(
                "open crystal SHM writer lock {}: {error}",
                lock_path.display()
            )
        })?;
    let result = unsafe { libc::flock(lock.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) };
    if result == -1 {
        return Err(format!(
            "another CrystalRuntime owns the shared memory: {}",
            std::io::Error::last_os_error()
        ));
    }
    Ok(lock)
}

#[cfg(test)]
mod tests {
    use super::*;

    struct TestFractalRing {
        name: String,
        buffer: PySharedBuffer,
    }

    impl TestFractalRing {
        fn new() -> Self {
            static NEXT: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
            let id = NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
            let name = format!("/sentinel-fractal-test-{}-{id}", std::process::id());
            let buffer = PySharedBuffer::new(name.clone(),
                FRACTAL_HEADER_BYTES + FRACTAL_SEEDS_CAPACITY * FRACTAL_SEED_BYTES, true).unwrap();
            Self { name, buffer }
        }
    }

    impl Drop for TestFractalRing {
        fn drop(&mut self) {
            self.buffer.unlink();
        }
    }

    #[test]
    fn closed_ring_rejects_reads_without_dereferencing_unmapped_memory() {
        let mut ring = TestFractalRing::new();
        ring.buffer.close();
        assert!(initialize_fractal_ring(&ring.buffer).is_err());
    }

    #[test]
    fn restarting_producer_preserves_head_seen_by_existing_mapping() {
        let ring = TestFractalRing::new();
        assert_eq!(initialize_fractal_ring(&ring.buffer), Ok(0));
        ring.buffer.store_u64_release(8, 123_456).unwrap();
        let restarted = PySharedBuffer::new(ring.name.clone(),
            FRACTAL_HEADER_BYTES + FRACTAL_SEEDS_CAPACITY * FRACTAL_SEED_BYTES, true).unwrap();
        let head = initialize_fractal_ring(&restarted).unwrap();
        assert_eq!(head, 123_456);
        restarted.store_u64_release(8, head + 1).unwrap();
        assert_eq!(ring.buffer.load_u64_acquire(8), Ok(123_457));
    }

    #[test]
    fn unknown_ring_header_does_not_reset_published_head() {
        let ring = TestFractalRing::new();
        ring.buffer.store_u64_release(0, 2_u64 << 32).unwrap();
        ring.buffer.store_u64_release(8, 123_456).unwrap();
        assert!(initialize_fractal_ring(&ring.buffer).is_err());
        assert_eq!(ring.buffer.load_u64_acquire(8), Ok(123_456));
    }

    #[test]
    fn remote_security_preserves_raw_scale_and_only_changes_lane_a() {
        let mut runtime = CrystalRuntime::in_memory(3);
        let before = runtime.lane_a.crystals[1].amplitude.to_raw();
        let lane_b_before = runtime.lane_b.crystals[1].amplitude.to_raw();
        assert_eq!(
            runtime.inject_remote_security_spa(1, SPA::from_raw(17)),
            Ok(before + 17)
        );
        assert_eq!(runtime.lane_b.crystals[1].amplitude.to_raw(), lane_b_before);
        assert_eq!(runtime.inject_remote_security_spa(3, SPA::from_raw(17)), Err("crystal index out of range"));
        assert_eq!(
            runtime.inject_remote_security_spa(1, SPA::from_raw(0)),
            Ok(before + 17)
        );
        runtime.lane_a.crystals[1].amplitude = SPA::from_raw(i64::MAX);
        assert_eq!(
            runtime.inject_remote_security_spa(1, SPA::from_raw(1)),
            Err("SPA amplitude overflow")
        );
    }

    #[test]
    fn in_memory_runtime_advances_dtc_and_non_markovian_step() {
        let mut runtime = CrystalRuntime::in_memory(3);
        let interval_ns = runtime.tick_dtc().unwrap();
        runtime.step().unwrap();

        let status = runtime.status();
        assert_eq!(status.dtc_ticks, 1);
        assert_eq!(status.qhc_tick, 1);
        assert!(interval_ns > 0);
        assert!(status.non_markovian_kernel_active);
        assert_eq!(
            status.non_markovian_history_capacity_ticks,
            PID_HISTORY_TICKS
        );
        assert!(!status.shm_active);
    }
}
