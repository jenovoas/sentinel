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
                return Err(format!("shm_open(create) falló: {}", std::io::Error::last_os_error()));
            }
            if ftruncate(fd, size as i64) == -1 {
                let e = std::io::Error::last_os_error();
                close(fd);
                shm_unlink(c_name.as_ptr());
                return Err(format!("ftruncate falló: {e}"));
            }
            let ptr = mmap(ptr::null_mut(), size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if ptr == MAP_FAILED {
                let e = std::io::Error::last_os_error();
                close(fd);
                shm_unlink(c_name.as_ptr());
                return Err(format!("mmap falló: {e}"));
            }
            Ok(Self { ptr: ptr as *mut u8, size, fd, name: name.to_string() })
        }
    }

    fn open(name: &str, size: usize) -> Result<Self, String> {
        let c_name = CString::new(name).map_err(|e| format!("nombre inválido: {e}"))?;
        // SAFETY: shm_open and mmap are standard POSIX; c_name is null-terminated and verified by CString::new
        unsafe {
            let fd = shm_open(c_name.as_ptr(), O_RDWR, 0o600);
            if fd == -1 {
                return Err(format!("shm_open(open) falló: {}", std::io::Error::last_os_error()));
            }
            let ptr = mmap(ptr::null_mut(), size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if ptr == MAP_FAILED {
                let e = std::io::Error::last_os_error();
                close(fd);
                return Err(format!("mmap falló: {e}"));
            }
            Ok(Self { ptr: ptr as *mut u8, size, fd, name: name.to_string() })
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
        unsafe {
            Ok(std::slice::from_raw_parts(self.ptr.add(offset), len).to_vec())
        }
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
        let payload: Vec<u8> = (0..4096u32).map(|i| (i % 256) as u8).collect();
        mem.store("big", &payload).unwrap();
        let got = mem.retrieve("big").unwrap().unwrap();
        assert_eq!(got, payload);
    }
}
