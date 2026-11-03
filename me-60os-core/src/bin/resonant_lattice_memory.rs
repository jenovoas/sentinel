// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! RESONANT LATTICE MEMORY — dos lanes y exportación opcional (S60).
//!
//! Memoria de dos mallas (Lane A / Lane B) en heap, con exportación opcional a
//! memoria compartida POSIX y un snapshot gzip de amplitudes raw S60.
//!
//! El snapshot recupera las amplitudes de ambas lanes; no incluye fases,
//! contextos ni metadatos del oscilador. /dev/shm no es almacenamiento durable.
//!
//! La rutina de demostración puede inyectar la semilla "Yo Soy" en mallas nuevas;
//! una malla restaurada no se bombea ni recibe esa semilla otra vez.
//! - QHC: bombeo 10;5,6,5 + Salto-17 sincroniza ambas mallas cada tick.

use libc::{
    ftruncate, mmap, munmap, shm_open, shm_unlink, MAP_FAILED, MAP_SHARED, O_CREAT, O_RDWR,
    PROT_READ, PROT_WRITE,
};
use me60os_core::qhc::QhcTensor;
use me60os_core::resonant_matrix::ResonantMatrix;
use me60os_core::spa::SPA;
use std::ffi::CString;
use std::ptr;

const N_NODES: usize = 5000; // por lane; escalable según RAM/SHM libre.

/// Ancla un buffer a /dev/shm (POSIX shared memory) sin pyo3.
/// Devuelve (ptr, fd). El llamador debe munmap+close al terminar.
unsafe fn anchor_shm(name: &str, size: usize) -> (*mut u8, i32) {
    let c_name = CString::new(name).expect("nombre shm inválido");
    let fd = shm_open(c_name.as_ptr(), O_CREAT | O_RDWR, 0o666);
    if fd == -1 {
        panic!("shm_open falló");
    }
    if ftruncate(fd, size as i64) == -1 {
        panic!("ftruncate falló");
    }
    let ptr = mmap(
        ptr::null_mut(),
        size,
        PROT_READ | PROT_WRITE,
        MAP_SHARED,
        fd,
        0,
    );
    if ptr == MAP_FAILED {
        panic!("mmap falló");
    }
    (ptr as *mut u8, fd)
}
/// Publica la semilla del cristal central al ring /me60os_fractal_seeds.
/// Layout idéntico a CrystalRuntime::publish_fractal_seed:
/// header 64 B (firma 0x53465231 + versión + head/tail) + 1024 slots × 30 B.
/// mycnetd lo lee vía SentinelFractalBridge sin cambios.
fn publish_seed_to_ring(lane: &me60os_core::resonant_matrix::ResonantMatrix) {
    use std::ffi::CString;
    const RING_NAME: &str = "/me60os_fractal_seeds";
    const HEADER: usize = 64;
    const SLOTS: usize = 1024;
    const SLOT: usize = 32; // HolographicSeedBinary completo, igual que CrystalRuntime
    let size = HEADER + SLOTS * SLOT;
    unsafe {
        let c = CString::new(RING_NAME).expect("nombre shm");
        let fd = libc::shm_open(c.as_ptr(), libc::O_CREAT | libc::O_RDWR, 0o600);
        if fd == -1 {
            return;
        }
        if libc::ftruncate(fd, size as i64) == -1 {
            libc::close(fd);
            return;
        }
        let ptr = libc::mmap(
            ptr::null_mut(),
            size,
            libc::PROT_READ | libc::PROT_WRITE,
            libc::MAP_SHARED,
            fd,
            0,
        );
        if ptr == libc::MAP_FAILED {
            libc::close(fd);
            return;
        }
        let base = ptr as *mut u8;
        // Header: firma + versión si es nuevo (head se preserva si existe).
        let sig = std::ptr::read_unaligned(base as *const u32);
        if sig != 0x5346_5231 {
            std::ptr::write_unaligned(base as *mut u32, 0x5346_5231u32);
            std::ptr::write_unaligned(base.add(4) as *mut u32, 1u32);
            std::ptr::write_unaligned(base.add(8) as *mut u64, 0u64);
        }
        let head = std::ptr::read_unaligned(base.add(8) as *const u64);
        // Semilla del cristal central: amplitud real del lattice local.
        let center = lane.size() / 2;
        let amp = lane.get_amplitudes().get(center).map(|a| a.to_raw()).unwrap_or(0);
        let slot = (head as usize) % SLOTS;
        let off = HEADER + slot * SLOT;
        let token = (head as u32).wrapping_add(center as u32);
        // Mapeo al hexágono receptor radio 3 (idéntico a CrystalRuntime::mycnet_hex_coordinate).
        // Sin esto, q/r caen fuera del LiquidLattice de mycnetd y la semilla se descarta.
        let mut offset = center % 37;
        let (q, r) = {
            let mut found = (0, 0);
            'outer: for qq in -3i32..=3 {
                let r_min = (-3i32).max(-qq - 3);
                let r_max = 3i32.min(-qq + 3);
                for rr in r_min..=r_max {
                    if offset == 0 { found = (qq, rr); break 'outer; }
                    offset -= 1;
                }
            }
            found
        };
        // Slot 32 B = HolographicSeedBinary (ver s60.rs: token, q, r, s,
        // amplitude, phase_sector, yhwh_pulse, flags, crc).
        let mut bytes = [0u8; 32];
        bytes[0..4].copy_from_slice(&token.to_le_bytes());
        bytes[4..8].copy_from_slice(&q.to_le_bytes());
        bytes[8..12].copy_from_slice(&r.to_le_bytes());
        bytes[12..16].copy_from_slice(&(-q - r).to_le_bytes());
        bytes[16..24].copy_from_slice(&amp.to_le_bytes());
        bytes[24] = (amp % 60) as u8; // phase_sector
        bytes[25] = 10; // yhwh_pulse = QHC YHWH[0]
        bytes[26..28].copy_from_slice(&1u16.to_le_bytes()); // flags
        // CRC16-CCITT idéntico a CrystalRuntime::crc16_ccitt y s60::compute_crc16.
        let mut crc = 0xffffu16;
        for &b in &bytes[..28] {
            crc ^= (b as u16) << 8;
            for _ in 0..8 {
                crc = if crc & 0x8000 != 0 { (crc << 1) ^ 0x1021 } else { crc << 1 };
            }
        }
        bytes[28..30].copy_from_slice(&crc.to_le_bytes());
        bytes[30..32].copy_from_slice(&0u16.to_le_bytes()); // padding/reserva
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), base.add(off), SLOT);
        std::ptr::write_unaligned(base.add(8) as *mut u64, head.saturating_add(1));
        libc::munmap(ptr, size);
        libc::close(fd);
    }
}
/// Serializes both lanes' raw S60 amplitudes to gzip+JSON.
fn build_snapshot(
    lane_a: &me60os_core::resonant_matrix::ResonantMatrix,
    lane_b: &me60os_core::resonant_matrix::ResonantMatrix,
) -> Result<Vec<u8>, String> {
    use flate2::write::GzEncoder;
    use flate2::Compression;
    use std::io::Write;
    if lane_a.size() != lane_b.size() {
        return Err("lane sizes differ".to_string());
    }
    let amplitudes = |lane: &me60os_core::resonant_matrix::ResonantMatrix| {
        lane.get_amplitudes().iter().map(|a| a.to_raw()).collect::<Vec<_>>()
    };
    let json = serde_json::json!({
        "lane_a_amplitudes": amplitudes(lane_a),
        "lane_b_amplitudes": amplitudes(lane_b),
    });
    let mut enc = GzEncoder::new(Vec::new(), Compression::default());
    enc.write_all(serde_json::to_string(&json).map_err(|e| e.to_string())?.as_bytes())
        .map_err(|e| e.to_string())?;
    enc.finish().map_err(|e| e.to_string())
}
/// Atomically replaces the gzip snapshot only after its contents reach disk.
fn save_snapshot_atomic(path: &std::path::Path, bytes: &[u8]) -> Result<(), String> {
    use std::fs::{self, File, OpenOptions};
    use std::io::Write;
    use std::time::{SystemTime, UNIX_EPOCH};

    let parent = path
        .parent()
        .filter(|parent| !parent.as_os_str().is_empty())
        .unwrap_or_else(|| std::path::Path::new("."));
    fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    let file_name = path.file_name().ok_or("snapshot path has no file name")?.to_string_lossy();
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_nanos();
    let temp = parent.join(format!(".{file_name}.{}.{}.tmp", std::process::id(), nonce));
    let result = (|| {
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temp)
            .map_err(|e| e.to_string())?;
        file.write_all(bytes).map_err(|e| e.to_string())?;
        file.sync_all().map_err(|e| e.to_string())?;
        drop(file);
        fs::rename(&temp, path).map_err(|e| e.to_string())?;
        File::open(parent)
            .and_then(|directory| directory.sync_all())
            .map_err(|e| e.to_string())
    })();
    if result.is_err() {
        let _ = fs::remove_file(&temp);
    }
    result
}

/// Restores both lanes exactly as represented by the snapshot.
fn recover_snapshot(
    data: &[u8],
    lane_a: &mut me60os_core::resonant_matrix::ResonantMatrix,
    lane_b: &mut me60os_core::resonant_matrix::ResonantMatrix,
) -> Result<String, String> {
    use flate2::read::GzDecoder;
    use std::io::Read;
    let mut dec = GzDecoder::new(data);
    let mut buf = String::new();
    dec.read_to_string(&mut buf).map_err(|e| e.to_string())?;
    let val: serde_json::Value = serde_json::from_str(&buf).map_err(|e| e.to_string())?;
    let (amps_a, amps_b): (Vec<i64>, Vec<i64>) =
        if let (Some(amps_a), Some(amps_b)) =
            (val.get("lane_a_amplitudes"), val.get("lane_b_amplitudes"))
        {
            (
                serde_json::from_value(amps_a.clone()).map_err(|e| e.to_string())?,
                serde_json::from_value(amps_b.clone()).map_err(|e| e.to_string())?,
            )
        } else if val.get("lane_a_amplitudes").is_none()
            && val.get("lane_b_amplitudes").is_none()
        {
            let legacy: Vec<i64> =
                serde_json::from_value(val["amplitudes"].clone()).map_err(|e| e.to_string())?;
            (legacy.clone(), legacy)
        } else {
            return Err("snapshot must contain both lane amplitudes".to_string());
        };
    if amps_a.len() != lane_a.size() || amps_b.len() != lane_b.size() {
        return Err("snapshot node count does not match lattice".to_string());
    }
    if lane_a.size() != lane_b.size() {
        return Err("lane sizes differ".to_string());
    }
    for (i, raw) in amps_a.iter().enumerate() {
        lane_a.crystals[i].amplitude = me60os_core::spa::SPA::from_raw(*raw);
    }
    for (i, raw) in amps_b.iter().enumerate() {
        lane_b.crystals[i].amplitude = me60os_core::spa::SPA::from_raw(*raw);
    }
    Ok(format!("{} amplitudes por lane restauradas", amps_a.len()))
}



fn main() {
    let keep = std::env::args().any(|arg| arg == "--keep");
    // --keep retains named SHM objects and enables the disk snapshot.
    // This process still unmaps and closes its own mappings on exit.
    // DOBLE MALLA — una por lane, cada una anclada a su SHM.
    let mut lane_a = ResonantMatrix::new(N_NODES);
    let mut lane_b = ResonantMatrix::new(N_NODES);
    let qhc = QhcTensor::new();

    let crystal_size = if lane_a.count_nodes() > 0 {
        lane_a.active_memory_usage() / lane_a.count_nodes()
    } else {
        std::mem::size_of::<SPA>() * 5 // fallback aproximado
    };
    let total = crystal_size * N_NODES;

    // Create shared regions; copy data only after attempting restoration.
    let (ptr_a, fd_a) = unsafe { anchor_shm("/me60os_lattice", total) };
    let (ptr_b, fd_b) = unsafe { anchor_shm("/me60os_lattice_b", total) };

    println!("💎 RESONANT LATTICE MEMORY — two lanes + optional SHM + amplitude snapshot.");
    println!(
        "   Nodos/lane: {} | bytes/lane: {} | bytes/nodo: {}",
        N_NODES, total, crystal_size
    );
    println!("   Dos lanes independientes; esta demo no implementa un mecanismo de portal.");
    println!("{:-<72}", "");

    let data = "Yo Soy";
    const SNAP_PATH: &str = "/var/lib/sentinel-lattice/snapshot.crystal.gz";
    let snapshot_restored = if keep {
        match std::fs::read(SNAP_PATH) {
            Ok(snapshot) => match recover_snapshot(&snapshot, &mut lane_a, &mut lane_b) {
                Ok(message) => {
                    println!("📂 Snapshot recuperado: {}", message);
                    true
                }
                Err(error) => {
                    eprintln!("⚠️ Snapshot inválido; no se considera restaurado: {error}");
                    false
                }
            },
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => false,
            Err(error) => {
                eprintln!("⚠️ Snapshot no pudo leerse: {error}");
                false
            }
        }
    } else {
        false
    };

    if !snapshot_restored {
        // Bombeo QHC y calentamiento se usan solo para una malla nueva.
        let warmup_cycles = 60u64;
        for step in 0..warmup_cycles {
            let phase_shift = qhc.apply_modulation(SPA::zero(), step);
            lane_a.apply_phase_shift(phase_shift);
            lane_b.apply_phase_shift(phase_shift);
            let pump_node = (step as usize) % lane_a.size();
            lane_a.inject_spa(pump_node, phase_shift);
            lane_b.inject_spa(pump_node, phase_shift);
            lane_a.step();
            lane_b.step();
        }
        println!("🔮 Resonando el lattice (bombeo QHC fase+amplitud + difusión fractal)...");
    }

    // Capturar el estado resonante de cada lane antes de sumar la semilla.
    // El decoder resta esta base y lee únicamente la amplitud inyectada.
    let base_amps_a = lane_a.get_amplitudes();
    let base_amps_b = lane_b.get_amplitudes();

    if !snapshot_restored {
        println!("📝 Inyectando semilla '{}' (compresión fractal: pocos nodos, malla propaga)", data);
        for (i, ch) in data.chars().enumerate() {
            let phase_deg = ((i as i64) * 360) / (data.len().max(1) as i64);
            lane_a.inject_dual(i, ch as i64, 1, phase_deg);
            lane_b.inject_dual(i, ch as i64, 1, phase_deg);
        }
    }

    if snapshot_restored {
        println!("📖 Snapshot de amplitudes restaurado para ambas lanes.");
    } else {
        // Lectura local de la semilla inyectada en una malla recién inicializada.
        let amps_a = lane_a.get_amplitudes();
        let amps_b = lane_b.get_amplitudes();
        let mut recovered = String::new();
        let mut convergen = true;
        for i in 0..data.len() {
            let raw_a = (amps_a[i] - base_amps_a[i]).to_raw();
            let raw_b = (amps_b[i] - base_amps_b[i]).to_raw();
            if raw_a.abs_diff(raw_b) > (SPA::SCALE_0 / 50) as u64 {
                convergen = false;
            }
            let ch_val = raw_a / SPA::SCALE_0;
            if let Ok(ch) = u8::try_from(ch_val) {
                if ch.is_ascii() && ch != 0 {
                    recovered.push(char::from(ch));
                }
            }
        }
        if convergen {
            println!("📖 Lectura local de semilla: '{}'", recovered);
        } else {
            println!("📖 Lectura local parcial: '{}'", recovered);
        }
    }

    // Copia los cristales actuales a la región SHM; esto no es persistencia durable.

    // Exportar a SHM ocurre después de aplicar una restauración válida.
    unsafe {
        ptr::copy_nonoverlapping(lane_a.crystals.as_ptr() as *const u8, ptr_a, total);
        ptr::copy_nonoverlapping(lane_b.crystals.as_ptr() as *const u8, ptr_b, total);
        println!("💾 Mallas ancladas a /dev/shm (/me60os_lattice, /me60os_lattice_b).");
        println!(
            "   RAM extendida por cristal: {} bytes/lane fuera del heap del proceso.",
            total
        );

        // Limpieza solo en modo demo. Con --keep el SHM queda para mycnetd.
        munmap(ptr_a as *mut libc::c_void, total);
        munmap(ptr_b as *mut libc::c_void, total);
        libc::close(fd_a);
        libc::close(fd_b);
        if !keep {
            let _ = shm_unlink(CString::new("/me60os_lattice").unwrap().as_ptr());
            let _ = shm_unlink(CString::new("/me60os_lattice_b").unwrap().as_ptr());
        } else {
            println!("   --keep: conserva los nombres SHM; este proceso ya cerró sus mappings.");
        }
    }
    // RING DE SEMILLAS (multi-nodo): publica una semilla PAI al ring que lee mycnetd.
    // Layout idéntico a CrystalRuntime: header 64 B + 1024×32 B.
    // Solo en --keep: en modo demo no se deja rastro.
    if keep && !snapshot_restored {
        publish_seed_to_ring(&lane_a);
    }
    // Snapshot guards both lanes' raw S60 amplitudes, replacing atomically.
    if keep {
        match build_snapshot(&lane_a, &lane_b)
            .and_then(|bytes| save_snapshot_atomic(std::path::Path::new(SNAP_PATH), &bytes).map(|()| bytes))
        {
            Ok(bytes) => println!("💾 Snapshot guardado: {} ({} B gzip)", SNAP_PATH, bytes.len()),
            Err(error) => eprintln!("⚠️ Snapshot no guardado: {error}"),
        }
    }



    println!("{:-<72}", "");
    println!("🏁 Two-lane amplitude memory; SHM is volatile and snapshots omit oscillator state.");
}
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn snapshot_round_trip_preserves_each_lane_amplitudes() {
        let mut original_a = ResonantMatrix::new(2);
        let mut original_b = ResonantMatrix::new(2);
        original_a.inject_spa(0, SPA::from_raw(123));
        original_a.inject_spa(1, SPA::from_raw(456));
        original_b.inject_spa(0, SPA::from_raw(789));
        original_b.inject_spa(1, SPA::from_raw(987));
        let snapshot = build_snapshot(&original_a, &original_b).unwrap();
        let mut restored_a = ResonantMatrix::new(2);
        let mut restored_b = ResonantMatrix::new(2);
        restored_a.inject_spa(0, SPA::from_raw(-55));
        restored_a.inject_spa(1, SPA::from_raw(-66));
        restored_b.inject_spa(0, SPA::from_raw(-77));
        restored_b.inject_spa(1, SPA::from_raw(-88));
        recover_snapshot(&snapshot, &mut restored_a, &mut restored_b).unwrap();
        assert_eq!(restored_a.get_amplitudes(), original_a.get_amplitudes());
        assert_eq!(restored_b.get_amplitudes(), original_b.get_amplitudes());
    }

    #[test]
    fn snapshot_rejects_wrong_node_count_without_partial_restore() {
        let mut source_a = ResonantMatrix::new(1);
        let source_b = ResonantMatrix::new(1);
        source_a.inject_spa(0, SPA::from_raw(123));
        let snapshot = build_snapshot(&source_a, &source_b).unwrap();
        let mut target_a = ResonantMatrix::new(2);
        let mut target_b = ResonantMatrix::new(2);
        assert!(recover_snapshot(&snapshot, &mut target_a, &mut target_b).is_err());
        assert_eq!(target_a.get_amplitudes()[0].to_raw(), 0);
        assert_eq!(target_b.get_amplitudes()[0].to_raw(), 0);
    }

    #[test]
    fn snapshot_rejects_corrupt_input() {
        let mut lane_a = ResonantMatrix::new(1);
        let mut lane_b = ResonantMatrix::new(1);
        assert!(recover_snapshot(b"not gzip", &mut lane_a, &mut lane_b).is_err());
    }
    #[test]
    fn legacy_single_lane_snapshot_restores_into_both_lanes() {
        use flate2::write::GzEncoder;
        use std::io::Write;

        let mut encoder = GzEncoder::new(Vec::new(), flate2::Compression::default());
        encoder
            .write_all(br#"{"amplitudes":[123,456]}"#)
            .unwrap();
        let legacy = encoder.finish().unwrap();
        let mut lane_a = ResonantMatrix::new(2);
        let mut lane_b = ResonantMatrix::new(2);
        lane_a.inject_spa(0, SPA::from_raw(-1));
        lane_b.inject_spa(1, SPA::from_raw(-1));
        recover_snapshot(&legacy, &mut lane_a, &mut lane_b).unwrap();
        assert_eq!(lane_a.get_amplitudes(), lane_b.get_amplitudes());
        assert_eq!(lane_a.get_amplitudes()[0].to_raw(), 123);
        assert_eq!(lane_a.get_amplitudes()[1].to_raw(), 456);
    }

    #[test]
    fn atomic_snapshot_save_replaces_file_in_isolated_temp_directory() {
        let dir = std::env::temp_dir().join(format!(
            "sentinel-snapshot-test-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("snapshot.gz");
        std::fs::write(&path, b"old").unwrap();
        save_snapshot_atomic(&path, b"new").unwrap();
        assert_eq!(std::fs::read(&path).unwrap(), b"new");
        std::fs::remove_dir_all(dir).unwrap();
    }
}
