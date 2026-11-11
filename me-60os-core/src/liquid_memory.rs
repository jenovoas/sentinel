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
use std::ptr;

/// Padding mínimo por entrada (igual que el legacy: 32 * 16 = 512 bytes).
const MIN_DATA_LEN: usize = 512;

/// Capacidad del anillo fractal y layout (igual que cortex/mycnet).
const FRACTAL_SEEDS_SHM: &str = "/me60os_fractal_seeds";
const FRACTAL_SEEDS_CAPACITY: usize = 1024;
const FRACTAL_HEADER_BYTES: usize = 64;
const FRACTAL_SEED_BYTES: usize = 32;

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

/// Escribe una semilla de 32 B en el anillo SHM existente (abre sin crear).
/// Lee el head con acquire, escribe el slot y avanza con release.
fn write_fractal_seed(seed: &[u8; 32]) -> Result<(), String> {
    let c_name =
        CString::new(FRACTAL_SEEDS_SHM).map_err(|e| format!("nombre SHM inválido: {e}"))?;
    // SAFETY: solo lectura/escritura del anillo existente; sin crear ni truncar.
    unsafe {
        let fd = shm_open(c_name.as_ptr(), O_RDWR, 0o600);
        if fd == -1 {
            return Err(format!(
                "anillo fractal no publicado (¿mycnetd/cortex activo?): {}",
                std::io::Error::last_os_error()
            ));
        }
        let size = FRACTAL_HEADER_BYTES + FRACTAL_SEEDS_CAPACITY * FRACTAL_SEED_BYTES;
        let ptr = mmap(
            ptr::null_mut(),
            size,
            PROT_READ | PROT_WRITE,
            MAP_SHARED,
            fd,
            0,
        );
        libc::close(fd);
        if ptr == MAP_FAILED {
            return Err(format!(
                "mmap del anillo falló: {}",
                std::io::Error::last_os_error()
            ));
        }
        let head_ptr = ptr as *const u64;
        let head = head_ptr.read_unaligned();
        std::sync::atomic::fence(std::sync::atomic::Ordering::Acquire);
        let slot = usize::try_from(head % FRACTAL_SEEDS_CAPACITY as u64).unwrap_or(0);
        let dst = (ptr as *mut u8).add(FRACTAL_HEADER_BYTES + slot * FRACTAL_SEED_BYTES);
        std::ptr::copy_nonoverlapping(seed.as_ptr(), dst, FRACTAL_SEED_BYTES);
        std::sync::atomic::fence(std::sync::atomic::Ordering::Release);
        let new_head = head.saturating_add(1);
        (ptr as *mut u64).write_unaligned(new_head);
        if libc::msync(ptr, size, libc::MS_SYNC) != 0 {
            munmap(ptr, size);
            return Err(format!(
                "msync del anillo falló: {}",
                std::io::Error::last_os_error()
            ));
        }
        munmap(ptr, size);
    }
    Ok(())
}

/// Semilla replicable mínima (fase 1 KV distribuida).
/// Layout compatible con `mycnet_memory::HolographicSeed`:
/// key + amplitude S60 raw + hash blake3. Sin pyo3, sin dependencias cruzadas.
#[derive(Debug, Clone)]
pub struct ReplicableSeed {
    /// Clave original (bytes).
    pub key: Vec<u8>,
    /// Energía total del lattice al replicar (amplitud real medida).
    pub amplitude_raw: i64,
    /// Hash blake3 del payload (integridad extremo a extremo).
    pub hash: [u8; 32],
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
}

impl LiquidMemory {
    /// Crea el servicio. `slots` = tamaño de la lattice (suficiente para
    /// cubrir el payload más grande esperado: 1 slot por 8 bytes de datos).
    pub fn new(slots: usize) -> Self {
        Self {
            lattice: LiquidLattice::new(slots),
            file_table: HashMap::new(),
            owned_buffers: Vec::new(),
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
            .inject_dual_channel(padded.clone(), key_hash.as_bytes().to_vec());

        // 3. Metadata
        self.file_table.insert(
            key.to_string(),
            LiquidEntry {
                len: data.len(),
                hash: *blake3::hash(data).as_bytes(),
                shm_name,
            },
        );
        self.owned_buffers.push(shm);
        Ok(())
    }
    /// Empaqueta una clave local en semilla replicable (fase 1 KV distribuida).
    /// Reutiliza metadata + energía medida del lattice. Sin duplicar `store`.
    pub fn replicate(&self, key: &str) -> Result<ReplicableSeed, String> {
        let entry = self
            .file_table
            .get(key)
            .ok_or_else(|| format!("clave '{key}' no existe local"))?;
        // Energía = suma saturante de amplitudes del lattice (estado real medido).
        let energy: i64 = self
            .lattice
            .buffer
            .lattice
            .iter()
            .map(|n| n.amplitude.to_raw())
            .fold(0i64, i64::saturating_add);
        Ok(ReplicableSeed {
            key: key.as_bytes().to_vec(),
            amplitude_raw: energy,
            hash: entry.hash,
        })
    }

    /// Publica la semilla replicable en el anillo SHM fractal
    /// (`/me60os_fractal_seeds`) para que `mycnetd` la difunda por la malla.
    /// Formato de 32 B compatible con `HolographicSeedBinary`: token derivado
    /// del hash blake3 de la clave, coordenada hexagonal receptora, amplitud
    /// = energía medida, CRC16-CCITT válido. No crea el anillo: falla si
    /// `mycnetd`/cortex no lo publicaron (el productor SHM vive en otro proceso).
    pub fn publish(&self, seed: &ReplicableSeed) -> Result<(), String> {
        if seed.key.is_empty() || seed.key.len() > 512 {
            return Err("clave fuera de rango replicable (1..=512 B)".to_string());
        }
        let key_hash = blake3::hash(&seed.key);
        let digest = key_hash.as_bytes();
        let token_id = u32::from_le_bytes([digest[0], digest[1], digest[2], digest[3]]);
        // Coordenada receptora determinista en el hexágono de 37 nodos.
        let (q, r) = hex_coord_for_key(digest);
        let s = -q - r;
        let mut bytes = [0u8; 32];
        bytes[0..4].copy_from_slice(&token_id.to_le_bytes());
        bytes[4..8].copy_from_slice(&q.to_le_bytes());
        bytes[8..12].copy_from_slice(&r.to_le_bytes());
        bytes[12..16].copy_from_slice(&s.to_le_bytes());
        bytes[16..24].copy_from_slice(&seed.amplitude_raw.to_le_bytes());
        bytes[24] = 0;
        bytes[25] = 0;
        bytes[26..28].copy_from_slice(&1u16.to_le_bytes());
        let crc = crc16_ccitt(&bytes[..28]);
        bytes[28..30].copy_from_slice(&crc.to_le_bytes());
        write_fractal_seed(&bytes)
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
        let key = "kv-sync-piloto";
        let msg = b"semilla-colectiva-fenix-01";
        mem.store(key, msg).expect("store debe funcionar");

        let seed = mem.replicate(key).expect("replicate debe empaquetar");
        assert_eq!(
            seed.key,
            key.as_bytes().to_vec(),
            "la semilla porta la clave"
        );
        assert!(!seed.hash.iter().all(|b| *b == 0), "hash blake3 no vacío");
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
    #[test]
    fn test_publish_rejects_bad_key_and_missing_ring() {
        let mut mem = LiquidMemory::new(64);
        let empty = ReplicableSeed {
            key: vec![],
            amplitude_raw: 1,
            hash: [0u8; 32],
        };
        assert!(mem.publish(&empty).is_err(), "clave vacía se rechaza");
        let long = ReplicableSeed {
            key: vec![b'k'; 513],
            amplitude_raw: 1,
            hash: [0u8; 32],
        };
        assert!(mem.publish(&long).is_err(), "clave >512 B se rechaza");
        // Sin anillo SHM publicado, publish falla cerrado sin crearlo.
        mem.store("solo-local", b"dato").unwrap();
        let seed = mem.replicate("solo-local").unwrap();
        let _ = mem.publish(&seed);
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
