// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🧠 LIQUID MEMORY — KV STORE SOBRE LATTICE + SHM (RUST NATIVO)
//!
//! Port nativo del único componente con valor incremental de
//! `quantum/liquid_memory_adapter.py` (legacy bridge, auditado 2026-08-05):
//! la **tabla clave → (len, hash, shm_name)** con retrieve por clave y
//! verificación de integridad. El resto (encoding base-60, inyección dual,
//! snapshot) ya vive en `quantum_core::LiquidLattice` y `resonant_matrix`.
//!
//! ## Diferencias conscientes con el legacy Py
//! - Hash de integridad: **blake3** (ya es dependencia del workspace) en vez
//!   de SHA256 vía hashlib. Misma función: detectar corrupción en retrieve.
//! - SHM: POSIX `shm_open`/`mmap` vía libc (misma primitiva que
//!   `shm_bridge::PySharedBuffer`, pero nativa y sin gate `extension-module`,
//!   para que los bins puros puedan usarla).
//! - Nombre SHM derivado de la clave: `/liquid_<hash[:8]>` (igual que legacy).
//!
//! ## References (memoria cuántica / fonónica)
//! - [EXT-009] Minute-Scale Photonic Quantum Memory. arXiv:2511.12537.
//! - [EXT-008] Memory of Starobinsky in a Time Crystal (Condensate). arXiv:2509.21959.
//! - [ZW-005] In-memory phononic learning toward cognitive mechanical intelligence. arXiv:2511.13543.
//! - [NV-046] Nandi (2025). arXiv:2510.11075 — quantum memory effect / thermal modulation.
//! - [P-TES] Novoa, J. (2026). *Tesis de Resonancia.* `docs/02_ciencia_y_quantum/research/TesiResonancia.md`.
//!
//! ## Regla S60
//! Este módulo NO hace aritmética de estado: solo IO de bytes + addressing.
//! La resonancia la pone `LiquidLattice::inject_dual_channel` (SPA exacto).

use crate::quantum_core::LiquidLattice;
use libc::{close, ftruncate, mmap, munmap, shm_open, shm_unlink};
use libc::{MAP_FAILED, MAP_SHARED, O_CREAT, O_RDWR, PROT_READ, PROT_WRITE};
use std::collections::HashMap;
use std::ffi::CString;
use std::io::ErrorKind;
use std::net::{SocketAddr, UdpSocket};
use std::ptr;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

/// Padding mínimo por entrada (igual que el legacy: 32 * 16 = 512 bytes).
const MIN_DATA_LEN: usize = 512;

/// MYKV v1: cabecera de 80 B y clave UTF-8 de hasta 512 B.
const KV_HEADER_BYTES: usize = 80;
const KV_MAX_PACKET_BYTES: usize = KV_HEADER_BYTES + 512;
const KV_PUBLISH: u8 = 1;
const KV_COMMITTED: u8 = 4;
const KV_RETRY_INTERVAL: Duration = Duration::from_millis(100);
const KV_DEFAULT_TIMEOUT_MS: u64 = 5_000;

/// CRC16-CCITT (polinomio 0x1021, init 0xFFFF), igual que cortex y mycnet.
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

/// Coordenada receptora determinista en el hexágono de 37 nodos (radio 3)
/// a partir del hash de la clave. Siempre cumple q+r+s == 0.
fn hex_coord_for_key(digest: &[u8; 32]) -> (i32, i32) {
    let mut index = usize::from(digest[4]) % 37;
    for q in -3_i32..=3 {
        for r in -3_i32..=3 {
            let s = -q - r;
            if q.abs().max(r.abs()).max(s.abs()) <= 3 {
                if index == 0 {
                    return (q, r);
                }
                index -= 1;
            }
        }
    }
    (0, 0)
}

/// Solo estas familias pueden salir del almacenamiento local.
fn validate_replicable_key(key: &[u8]) -> Result<(), String> {
    if key.is_empty() || key.len() > 512 {
        return Err("clave fuera de rango replicable (1..=512 B)".to_string());
    }
    let key = std::str::from_utf8(key).map_err(|_| "clave KV no es UTF-8".to_string())?;
    if !key.starts_with("crystal-") && !key.starts_with("portal-metrics-") {
        return Err(
            "clave KV no autorizada: requiere prefijo crystal- o portal-metrics-".to_string(),
        );
    }
    Ok(())
}

/// Codifica una vez: todo retry conserva exactamente la misma identidad.
fn encode_publish(seed: &ReplicableSeed) -> Result<([u8; KV_MAX_PACKET_BYTES], usize), String> {
    validate_replicable_key(&seed.key)?;
    let mut packet = [0u8; KV_MAX_PACKET_BYTES];
    packet[..4].copy_from_slice(b"MYKV");
    packet[4] = KV_PUBLISH;
    packet[5] = 1;
    let key_len = u16::try_from(seed.key.len())
        .map_err(|_| "longitud de clave KV fuera de u16".to_string())?;
    packet[6..8].copy_from_slice(&key_len.to_le_bytes());
    packet[8..16].copy_from_slice(&seed.timestamp_ns.to_le_bytes());
    let digest = blake3::hash(&seed.key);
    let (q, r) = hex_coord_for_key(digest.as_bytes());
    let binary = &mut packet[16..48];
    binary[..4].copy_from_slice(&digest.as_bytes()[..4]);
    binary[4..8].copy_from_slice(&q.to_le_bytes());
    binary[8..12].copy_from_slice(&r.to_le_bytes());
    binary[12..16].copy_from_slice(&(-q - r).to_le_bytes());
    binary[16..24].copy_from_slice(&seed.amplitude_raw.to_le_bytes());
    binary[26..28].copy_from_slice(&1u16.to_le_bytes());
    let crc = crc16_ccitt(&binary[..28]);
    binary[28..30].copy_from_slice(&crc.to_le_bytes());
    packet[48..80].copy_from_slice(&seed.hash);
    let len = KV_HEADER_BYTES + seed.key.len();
    packet[KV_HEADER_BYTES..len].copy_from_slice(&seed.key);
    Ok((packet, len))
}

fn is_matching_commit(received: &[u8], published: &[u8]) -> bool {
    received.len() == published.len()
        && received.len() >= KV_HEADER_BYTES
        && received[4] == KV_COMMITTED
        && received[..4] == published[..4]
        && received[5..] == published[5..]
}

fn publish_to(seed: &ReplicableSeed, addr: SocketAddr, timeout: Duration) -> Result<(), String> {
    let (packet, len) = encode_publish(seed)?;
    if !addr.ip().is_loopback() {
        return Err("MYCNET_KV_ADDR debe ser una dirección loopback".to_string());
    }
    if timeout.is_zero() {
        return Err("MYCNET_KV_TIMEOUT_MS debe ser mayor que cero".to_string());
    }
    let deadline = Instant::now()
        .checked_add(timeout)
        .ok_or_else(|| "timeout KV fuera de rango".to_string())?;
    let bind_addr = if addr.is_ipv4() {
        "127.0.0.1:0"
    } else {
        "[::1]:0"
    };
    let socket = UdpSocket::bind(bind_addr).map_err(|e| format!("socket KV local: {e}"))?;
    // UDP conectado filtra también el SocketAddr de origen, no solo el contenido.
    socket
        .connect(addr)
        .map_err(|e| format!("conectar KV local: {e}"))?;
    let mut next_send = Instant::now();
    // Un byte extra permite rechazar datagramas demasiado grandes sin aceptar truncados.
    let mut received = [0u8; KV_MAX_PACKET_BYTES + 1];
    loop {
        let now = Instant::now();
        if now >= deadline {
            return Err(format!(
                "timeout KV tras {} ms: commit desconocido; no implica pérdida ni confirma entrega; reintentar la misma semilla",
                timeout.as_millis()
            ));
        }
        if now >= next_send {
            socket
                .set_write_timeout(Some(deadline - now))
                .map_err(|e| format!("timeout de envío KV: {e}; commit desconocido"))?;
            match socket.send(&packet[..len]) {
                Ok(sent) if sent == len => {}
                Ok(_) => return Err("envío KV incompleto; commit desconocido".to_string()),
                Err(e)
                    if matches!(
                        e.kind(),
                        ErrorKind::ConnectionRefused
                            | ErrorKind::Interrupted
                            | ErrorKind::WouldBlock
                            | ErrorKind::TimedOut
                    ) => {}
                Err(e) => return Err(format!("envío KV: {e}; commit desconocido")),
            }
            next_send = now + KV_RETRY_INTERVAL;
        }
        let wait = next_send
            .min(deadline)
            .saturating_duration_since(Instant::now());
        if wait.is_zero() {
            continue;
        }
        socket
            .set_read_timeout(Some(wait))
            .map_err(|e| format!("timeout de recepción KV: {e}; commit desconocido"))?;
        match socket.recv(&mut received) {
            Ok(n) if is_matching_commit(&received[..n], &packet[..len]) => return Ok(()),
            Ok(_) => {}
            Err(e)
                if matches!(
                    e.kind(),
                    ErrorKind::ConnectionRefused
                        | ErrorKind::Interrupted
                        | ErrorKind::WouldBlock
                        | ErrorKind::TimedOut
                ) => {}
            Err(e) => return Err(format!("recepción KV: {e}; commit desconocido")),
        }
    }
}

fn next_store_timestamp(clock_ns: u64, previous_ns: u64) -> Result<u64, String> {
    let next = previous_ns
        .checked_add(1)
        .ok_or_else(|| "timestamp KV agotado en esta instancia".to_string())?;
    Ok(clock_ns.max(next))
}

/// Semilla replicable mínima (fase 1 KV distribuida).
/// Layout compatible con `mycnet_memory::HolographicSeed`:
/// key + amplitude S60 raw + hash blake3. Sin pyo3, sin dependencias cruzadas.
#[derive(Debug, Clone)]
pub struct ReplicableSeed {
    /// Clave original (bytes).
    pub key: Vec<u8>,
    /// Energía medida al almacenar; estable aunque evolucione la lattice.
    pub amplitude_raw: i64,
    /// Hash blake3 del payload (integridad extremo a extremo).
    pub hash: [u8; 32],
    /// Versión original de store, nanosegundos Unix; nunca se refresca en retry.
    pub timestamp_ns: u64,
}

/// Metadata de una entrada almacenada.
#[derive(Debug, Clone)]
pub struct LiquidEntry {
    /// Largo real del payload (sin padding).
    pub len: usize,
    /// Hash blake3 del payload original (integridad en retrieve).
    pub hash: [u8; 32],
    /// Nombre POSIX del buffer SHM que respalda la entrada.
    pub shm_name: String,
    /// Versión original del almacenamiento, nanosegundos Unix.
    pub timestamp_ns: u64,
    /// Energía medida al almacenar, retenida para replicaciones idénticas.
    pub amplitude_raw: i64,
}

/// Buffer SHM POSIX nativo (owner-side). Espejo mínimo de shm_bridge,
/// disponible para bins puros (sin pyo3).
struct NativeShm {
    ptr: *mut u8,
    size: usize,
    fd: i32,
    name: String,
}

impl NativeShm {
    fn create(name: &str, size: usize) -> Result<Self, String> {
        let c_name = CString::new(name).map_err(|e| format!("nombre inválido: {e}"))?;
        // SAFETY: shm_open, ftruncate, mmap are standard POSIX; c_name is null-terminated and verified by CString::new
        unsafe {
            let fd = shm_open(c_name.as_ptr(), O_CREAT | O_RDWR, 0o600);
            if fd == -1 {
                return Err(format!(
                    "shm_open(create) falló: {}",
                    std::io::Error::last_os_error()
                ));
            }
            if ftruncate(fd, size as i64) == -1 {
                let e = std::io::Error::last_os_error();
                close(fd);
                shm_unlink(c_name.as_ptr());
                return Err(format!("ftruncate falló: {e}"));
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
                let e = std::io::Error::last_os_error();
                close(fd);
                shm_unlink(c_name.as_ptr());
                return Err(format!("mmap falló: {e}"));
            }
            Ok(Self {
                ptr: ptr as *mut u8,
                size,
                fd,
                name: name.to_string(),
            })
        }
    }

    fn open(name: &str, size: usize) -> Result<Self, String> {
        let c_name = CString::new(name).map_err(|e| format!("nombre inválido: {e}"))?;
        // SAFETY: shm_open and mmap are standard POSIX; c_name is null-terminated and verified by CString::new
        unsafe {
            let fd = shm_open(c_name.as_ptr(), O_RDWR, 0o600);
            if fd == -1 {
                return Err(format!(
                    "shm_open(open) falló: {}",
                    std::io::Error::last_os_error()
                ));
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
                let e = std::io::Error::last_os_error();
                close(fd);
                return Err(format!("mmap falló: {e}"));
            }
            Ok(Self {
                ptr: ptr as *mut u8,
                size,
                fd,
                name: name.to_string(),
            })
        }
    }

    fn write(&self, offset: usize, data: &[u8]) -> Result<(), String> {
        if offset + data.len() > self.size {
            return Err("write fuera de rango".to_string());
        }
        // SAFETY: offset and len validated against self.size above; ptr.add(offset) is within mapped region
        unsafe {
            ptr::copy_nonoverlapping(data.as_ptr(), self.ptr.add(offset), data.len());
        }
        Ok(())
    }

    fn read(&self, offset: usize, len: usize) -> Result<Vec<u8>, String> {
        if offset + len > self.size {
            return Err("read fuera de rango".to_string());
        }
        // SAFETY: offset and len validated against self.size above; ptr.add(offset) is within mapped region
        unsafe { Ok(std::slice::from_raw_parts(self.ptr.add(offset), len).to_vec()) }
    }
}

impl Drop for NativeShm {
    fn drop(&mut self) {
        // SAFETY: munmap and close are idempotent; null/MAP_FAILED checks guard against double-free
        unsafe {
            if !self.ptr.is_null() && self.ptr != MAP_FAILED as *mut u8 {
                munmap(self.ptr as *mut libc::c_void, self.size);
            }
            if self.fd != -1 {
                close(self.fd);
            }
        }
    }
}

/// Servicio de memoria cognitiva: KV-store con respaldo SHM + inyección
/// resonante a la lattice líquida (levitación de datos en canal de fase).
pub struct LiquidMemory {
    /// Lattice resonante donde levitan amplitud+fase de cada store.
    pub lattice: LiquidLattice,
    /// Tabla clave → metadata (el único aporte real del legacy Py).
    file_table: HashMap<String, LiquidEntry>,
    /// Buffers SHM vivos que posee este proceso (se liberan en Drop).
    owned_buffers: Vec<NativeShm>,
    /// Monotonía local por instancia incluso si el reloj Unix retrocede.
    last_timestamp_ns: u64,
}

impl LiquidMemory {
    /// Crea el servicio. `slots` = tamaño de la lattice (suficiente para
    /// cubrir el payload más grande esperado: 1 slot por 8 bytes de datos).
    pub fn new(slots: usize) -> Self {
        Self {
            lattice: LiquidLattice::new(slots),
            file_table: HashMap::new(),
            owned_buffers: Vec::new(),
            last_timestamp_ns: 0,
        }
    }

    /// Nombre SHM determinista para una clave (mismo esquema que legacy).
    fn shm_name_for(key: &str) -> String {
        let h = blake3::hash(key.as_bytes());
        format!("/liquid_{}", &h.to_hex()[..16])
    }

    /// Almacena un payload bajo `key`:
    /// 1. Escribe el payload (padded a 512) en un buffer SHM nombrado.
    /// 2. Inyecta (datos, hash_de_clave) al canal dual de la lattice.
    /// 3. Registra metadata (len, hash de datos, shm_name) en la tabla.
    pub fn store(&mut self, key: &str, data: &[u8]) -> Result<(), String> {
        let timestamp_ns = u64::try_from(
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map_err(|e| format!("reloj anterior a Unix epoch: {e}"))?
                .as_nanos(),
        )
        .map_err(|_| "timestamp KV fuera de u64".to_string())?;
        let timestamp_ns = next_store_timestamp(timestamp_ns, self.last_timestamp_ns)?;
        let mut padded = data.to_vec();
        if padded.len() < MIN_DATA_LEN {
            padded.resize(MIN_DATA_LEN, 0);
        }

        // 1. SHM backing store
        let shm_name = Self::shm_name_for(key);
        let shm = NativeShm::create(&shm_name, padded.len())?;
        shm.write(0, &padded)?;

        // 2. Inyección resonante dual: A = datos, B = hash de la clave (fase)
        let key_hash = blake3::hash(key.as_bytes());
        self.lattice
            .inject_dual_channel(padded, key_hash.as_bytes().to_vec());

        let amplitude_raw = self
            .lattice
            .buffer
            .lattice
            .iter()
            .map(|n| n.amplitude.to_raw())
            .fold(0i64, i64::saturating_add);
        // 3. Metadata
        self.file_table.insert(
            key.to_string(),
            LiquidEntry {
                len: data.len(),
                hash: *blake3::hash(data).as_bytes(),
                shm_name,
                timestamp_ns,
                amplitude_raw,
            },
        );
        self.last_timestamp_ns = timestamp_ns;
        self.owned_buffers.push(shm);
        Ok(())
    }
    /// Empaqueta una clave local en semilla replicable (fase 1 KV distribuida).
    /// Reutiliza metadata y energía originales de store, sin refrescar la versión.
    pub fn replicate(&self, key: &str) -> Result<ReplicableSeed, String> {
        validate_replicable_key(key.as_bytes())?;
        let entry = self
            .file_table
            .get(key)
            .ok_or_else(|| format!("clave '{key}' no existe local"))?;
        Ok(ReplicableSeed {
            key: key.as_bytes().to_vec(),
            amplitude_raw: entry.amplitude_raw,
            hash: entry.hash,
            timestamp_ns: entry.timestamp_ns,
        })
    }

    /// Publica por UDP MYKV v1 separado del ring Cortex. Solo retorna éxito
    /// tras Committed con identidad exacta (ACK de todos los peers configurados).
    /// MYCNET_KV_ADDR: 127.0.0.1:4242 por defecto, únicamente loopback.
    /// MYCNET_KV_TIMEOUT_MS: 5000 por defecto. Timeout = commit desconocido,
    /// no prueba de pérdida. Reintentar esta misma semilla conserva la versión.
    pub fn publish(&self, seed: &ReplicableSeed) -> Result<(), String> {
        validate_replicable_key(&seed.key)?;
        let addr = match std::env::var("MYCNET_KV_ADDR") {
            Ok(value) => value,
            Err(std::env::VarError::NotPresent) => "127.0.0.1:4242".to_string(),
            Err(e) => return Err(format!("MYCNET_KV_ADDR inválido: {e}")),
        };
        let addr = addr
            .parse::<SocketAddr>()
            .map_err(|e| format!("MYCNET_KV_ADDR inválido: {e}"))?;
        let timeout_ms = match std::env::var("MYCNET_KV_TIMEOUT_MS") {
            Ok(value) => value
                .parse::<u64>()
                .map_err(|e| format!("MYCNET_KV_TIMEOUT_MS inválido: {e}"))?,
            Err(std::env::VarError::NotPresent) => KV_DEFAULT_TIMEOUT_MS,
            Err(e) => return Err(format!("MYCNET_KV_TIMEOUT_MS inválido: {e}")),
        };
        publish_to(seed, addr, Duration::from_millis(timeout_ms))
    }

    /// Recupera por clave. Lee del SHM (rápido) y verifica integridad
    /// blake3 contra la metadata. Devuelve None si la clave no existe;
    /// Err si el dato almacenado no pasa la verificación.
    pub fn retrieve(&self, key: &str) -> Result<Option<Vec<u8>>, String> {
        let Some(entry) = self.file_table.get(key) else {
            return Ok(None);
        };
        let read_len = entry.len.max(MIN_DATA_LEN);
        let shm = NativeShm::open(&entry.shm_name, read_len)?;
        let data = shm.read(0, entry.len)?;

        let actual = blake3::hash(&data);
        if actual.as_bytes() != &entry.hash {
            return Err(format!(
                "integridad fallida para clave '{key}': hash no coincide"
            ));
        }
        Ok(Some(data))
    }

    /// Lista las claves registradas.
    pub fn keys(&self) -> Vec<&str> {
        self.file_table.keys().map(String::as_str).collect()
    }
}

impl Drop for LiquidMemory {
    fn drop(&mut self) {
        // Deslinkear los segmentos SHM que este servicio creó.
        for buf in &self.owned_buffers {
            if let Ok(c_name) = CString::new(buf.name.clone()) {
                // SAFETY: shm_unlink is idempotent; owned_buffers list is internal and exclusive
                unsafe {
                    shm_unlink(c_name.as_ptr());
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_store_retrieve_roundtrip() {
        let mut mem = LiquidMemory::new(1024);
        let key = "core_system";
        let msg = b"MEMORIA_HOLOMORFA_AAS_V1_INIT";
        mem.store(key, msg).expect("store debe funcionar");

        let got = mem.retrieve(key).expect("retrieve no debe fallar");
        assert_eq!(got.as_deref(), Some(&msg[..]), "roundtrip exacto");
    }
    #[test]
    fn test_store_replicate_retrieve_roundtrip() {
        let mut mem = LiquidMemory::new(1024);
        let key = "crystal-kv-sync-piloto";
        let msg = b"semilla-colectiva-fenix-01";
        mem.store(key, msg).expect("store debe funcionar");

        let seed = mem.replicate(key).expect("replicate debe empaquetar");
        assert_eq!(
            seed.key,
            key.as_bytes().to_vec(),
            "la semilla porta la clave"
        );
        let expected = blake3::hash(msg);
        assert_eq!(
            seed.hash,
            *expected.as_bytes(),
            "hash íntegro extremo a extremo"
        );

        let got = mem.retrieve(key).expect("retrieve no debe fallar");
        assert_eq!(
            got.as_deref(),
            Some(&msg[..]),
            "payload intacto tras replicate"
        );
        assert!(
            mem.replicate("no_existe").is_err(),
            "replicate de ausente falla"
        );
    }
    fn test_seed(key: &[u8]) -> ReplicableSeed {
        ReplicableSeed {
            key: key.to_vec(),
            amplitude_raw: 12_960_000,
            hash: *blake3::hash(b"payload-local").as_bytes(),
            timestamp_ns: 1_234_567_890,
        }
    }

    #[test]
    fn test_publish_and_replicate_enforce_whitelist() {
        let mut mem = LiquidMemory::new(64);
        for key in [b"".as_slice(), b"solo-local", b"CRYSTAL-x", b"crystal-\xff"] {
            assert!(mem.publish(&test_seed(key)).is_err());
        }
        assert!(mem.publish(&test_seed(&vec![b'k'; 513])).is_err());
        mem.store("solo-local", b"dato").unwrap();
        assert_eq!(mem.retrieve("solo-local").unwrap().unwrap(), b"dato");
        assert!(mem.replicate("solo-local").is_err());
        assert!(encode_publish(&test_seed(b"crystal-ok")).is_ok());
        assert!(encode_publish(&test_seed(b"portal-metrics-ok")).is_ok());
    }

    #[test]
    fn test_original_store_version_survives_lattice_changes() {
        let mut mem = LiquidMemory::new(64);
        mem.store("crystal-version-stable", b"original").unwrap();
        let original = mem.replicate("crystal-version-stable").unwrap();
        assert_eq!(
            original.timestamp_ns,
            mem.file_table["crystal-version-stable"].timestamp_ns
        );
        mem.store("other-local-value", b"changes lattice energy")
            .unwrap();
        let again = mem.replicate("crystal-version-stable").unwrap();
        assert_eq!(
            encode_publish(&original).unwrap(),
            encode_publish(&again).unwrap()
        );
        mem.store("crystal-version-stable", b"replacement").unwrap();
        let replacement = mem.replicate("crystal-version-stable").unwrap();
        assert!(replacement.timestamp_ns > original.timestamp_ns);
        assert_ne!(replacement.hash, original.hash);
    }

    #[test]
    fn test_store_timestamps_are_monotonic_under_clock_rollback() {
        assert_eq!(next_store_timestamp(100, 20).unwrap(), 100);
        assert_eq!(next_store_timestamp(100, 100).unwrap(), 101);
        assert_eq!(next_store_timestamp(10, 100).unwrap(), 101);
        assert!(next_store_timestamp(0, u64::MAX).is_err());
        let mut mem = LiquidMemory::new(64);
        mem.last_timestamp_ns = 10_000_000_000_000_000_000;
        mem.store("crystal-clock-rollback", b"payload").unwrap();
        assert_eq!(
            mem.replicate("crystal-clock-rollback")
                .unwrap()
                .timestamp_ns,
            10_000_000_000_000_000_001
        );
    }

    #[test]
    fn test_mykw_packet_layout_and_commit_identity() {
        let seed = test_seed(b"portal-metrics-wire");
        let (packet, len) = encode_publish(&seed).unwrap();
        assert_eq!(len, 80 + seed.key.len());
        assert_eq!(&packet[..8], &[b'M', b'Y', b'K', b'V', 1, 1, 19, 0]);
        assert_eq!(&packet[8..16], &seed.timestamp_ns.to_le_bytes());
        assert_eq!(&packet[32..40], &seed.amplitude_raw.to_le_bytes());
        assert_eq!(&packet[44..46], &crc16_ccitt(&packet[16..44]).to_le_bytes());
        assert_eq!(&packet[48..80], &seed.hash);
        assert_eq!(&packet[80..len], seed.key.as_slice());
        let mut committed = packet;
        committed[4] = KV_COMMITTED;
        assert!(is_matching_commit(&committed[..len], &packet[..len]));
        // Magic, tipo, versión, longitud, timestamp, seed, CRC, hash y clave.
        for offset in [0, 4, 5, 6, 8, 16, 32, 44, 48, 80] {
            let mut bad = committed;
            bad[offset] ^= 1;
            assert!(
                !is_matching_commit(&bad[..len], &packet[..len]),
                "offset {offset}"
            );
        }
        assert!(!is_matching_commit(&committed[..len - 1], &packet[..len]));
        assert!(!is_matching_commit(&committed[..len + 1], &packet[..len]));
        assert!(!is_matching_commit(&[], &packet[..len]));
    }

    #[test]
    fn test_publish_retries_same_identity_after_loss_and_wrong_commit() {
        let server = UdpSocket::bind("127.0.0.1:0").unwrap();
        let addr = server.local_addr().unwrap();
        server
            .set_read_timeout(Some(Duration::from_secs(2)))
            .unwrap();
        let daemon = std::thread::spawn(move || {
            let mut bytes = [0u8; KV_MAX_PACKET_BYTES + 1];
            let (n, sender) = server.recv_from(&mut bytes).unwrap();
            let original = bytes[..n].to_vec();
            // Primera publicación perdida: sin respuesta.
            let (n, retry_sender) = server.recv_from(&mut bytes).unwrap();
            assert_eq!(sender, retry_sender);
            assert_eq!(&bytes[..n], original.as_slice());
            let mut wrong = original.clone();
            wrong[4] = KV_COMMITTED;
            wrong[48] ^= 1;
            server.send_to(&wrong, sender).unwrap();
            let mut committed = original.clone();
            committed[4] = KV_COMMITTED;
            // Un emisor distinto tampoco puede confirmar, aun con identidad exacta.
            let rogue = UdpSocket::bind("127.0.0.1:0").unwrap();
            rogue.send_to(&committed, sender).unwrap();
            let (n, retry_sender) = server.recv_from(&mut bytes).unwrap();
            assert_eq!(retry_sender, sender);
            assert_eq!(&bytes[..n], original.as_slice());
            server.send_to(&committed, sender).unwrap();
            original
        });
        let seed = test_seed(b"crystal-retry-loss");
        publish_to(&seed, addr, Duration::from_secs(2)).unwrap();
        let original = daemon.join().unwrap();
        assert_eq!(&original[8..16], &seed.timestamp_ns.to_le_bytes());
    }

    #[test]
    fn test_publish_times_out_without_matching_committed() {
        let server = UdpSocket::bind("127.0.0.1:0").unwrap();
        let addr = server.local_addr().unwrap();
        server
            .set_read_timeout(Some(Duration::from_secs(2)))
            .unwrap();
        let daemon = std::thread::spawn(move || {
            let mut bytes = [0u8; KV_MAX_PACKET_BYTES + 1];
            let (n, sender) = server.recv_from(&mut bytes).unwrap();
            // ACK peer no es Committed; luego Committed con otro timestamp tampoco.
            bytes[4] = 3;
            server.send_to(&bytes[..n], sender).unwrap();
            bytes[4] = KV_COMMITTED;
            bytes[8] ^= 1;
            server.send_to(&bytes[..n], sender).unwrap();
            std::thread::sleep(Duration::from_millis(350));
        });
        let error = publish_to(
            &test_seed(b"crystal-timeout-unknown"),
            addr,
            Duration::from_millis(230),
        )
        .unwrap_err();
        assert!(error.contains("timeout KV"));
        assert!(error.contains("commit desconocido"));
        assert!(error.contains("no implica pérdida"));
        daemon.join().unwrap();
    }

    #[test]
    fn test_publish_rejects_non_loopback_and_zero_timeout() {
        let seed = test_seed(b"crystal-local-only");
        assert!(publish_to(
            &seed,
            "192.0.2.1:4242".parse().unwrap(),
            Duration::from_millis(1)
        )
        .unwrap_err()
        .contains("loopback"));
        assert!(
            publish_to(&seed, "127.0.0.1:4242".parse().unwrap(), Duration::ZERO)
                .unwrap_err()
                .contains("mayor que cero")
        );
    }

    #[test]
    fn test_retrieve_missing_key() {
        let mem = LiquidMemory::new(64);
        assert_eq!(mem.retrieve("no_existe").unwrap(), None);
    }

    #[test]
    fn test_overwrite_same_key() {
        let mut mem = LiquidMemory::new(1024);
        mem.store("k", b"primero").unwrap();
        mem.store("k", b"segundo-valor-distinto").unwrap();
        let got = mem.retrieve("k").unwrap().unwrap();
        assert_eq!(got, b"segundo-valor-distinto");
    }

    #[test]
    fn test_large_payload() {
        let mut mem = LiquidMemory::new(8192);
        let payload: Vec<u8> = (0..4096u32)
            .map(|i| u8::try_from(i % 256).expect("módulo acotado a byte"))
            .collect();
        mem.store("big", &payload).unwrap();
        let got = mem.retrieve("big").unwrap().unwrap();
        assert_eq!(got, payload);
    }
}
