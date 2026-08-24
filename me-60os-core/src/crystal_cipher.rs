// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 💎 CRYSTAL CIPHER — Clave efímera por pulso del cristal
//!
//! La fase del cristal (IsochronousOscillator, S60) ES el fenómeno físico que
//! late en el hardware. No es una "cáscara" alrededor de una función: el pulso
//! mismo es la semilla. Cada master cycle (68s = 4 breath, ver quantum_heartbeat.py)
//! la fase deriva una clave AES-256-GCM determinista. Misma fase + mismo pulso
//! -> misma clave. Pulso distinto -> clave distinta. El descifrado está
//! sincronizado por el mismo cristal (aislamiento dinámico ring0-adjacent).
//!
//! Acople: la capa de cifrado protege lo que watchdog / cortex / guardian-A /
//! guardian-B comparten en SHM (PySharedBuffer) y en el ringbuf del LSM.

use crate::isochronous_oscillator::IsochronousOscillator;
use crate::spa::SPA;
use aes_gcm::{
    aead::{Aead, KeyInit, Payload},
    Aes256Gcm,
};
// APRENDIZAJE: aes-gcm quiere Nonce como GenericArray<u8,U12>. Pasar &[u8;12]
// con `.into()` (ver encrypt/decrypt) evita el tipo y el warning de import unused.
use std::sync::Mutex;

/// Ciclo maestro en segundos (igual que quantum_heartbeat.py: 4 x 17s breath).
pub const MASTER_CYCLE_S: u64 = 68;
/// Ciclo de respiración en segundos.
pub const BREATH_CYCLE_S: u64 = 17;

/// Capa de cifrado dinámico alimentada por el cristal.
pub struct CrystalCipher {
    crystal: Mutex<IsochronousOscillator>,
    pulse: u64,
    key_cache: Mutex<[u8; 32]>,
}

impl CrystalCipher {
    pub fn new(name: &str) -> Self {
        let crystal = IsochronousOscillator::new(name);
        let mut s = Self {
            crystal: Mutex::new(crystal),
            pulse: 0,
            key_cache: Mutex::new([0u8; 32]),
        };
        // Semilla inicial desde la fase de arranque del cristal.
        s.rotate();
        s
    }

    /// Avanza el cristal un breath y rota la clave de la capa.
    /// Cada 4 breath -> master cycle -> la fase purga deriva nueva clave.
    pub fn tick_breath(&mut self) {
        let dt = SPA::new(BREATH_CYCLE_S as i64, 0, 0, 0, 0);
        {
            let mut c = self.crystal.lock().unwrap();
            c.oscillate(dt);
        }
        self.pulse += 1;
        if self.pulse.is_multiple_of(4) {
            self.rotate();
        }
    }

    /// Deriva la clave de la fase actual del cristal + contador de pulso.
    /// Blake3(phase_raw || pulse) -> 32 bytes. Determinista, S60-seeded.
    fn rotate(&mut self) {
        let phase_raw = {
            let c = self.crystal.lock().unwrap();
            c.get_phase().to_raw()
        };
        let mut seed = Vec::with_capacity(16);
        seed.extend_from_slice(&phase_raw.to_le_bytes());
        seed.extend_from_slice(&self.pulse.to_le_bytes());
        // También mezclamos la amplitud (energía del pulso) — fenómeno real.
        let amp_raw = {
            let c = self.crystal.lock().unwrap();
            c.get_amplitude().to_raw()
        };
        seed.extend_from_slice(&amp_raw.to_le_bytes());
        let hash = blake3::hash(&seed);
        *self.key_cache.lock().unwrap() = *hash.as_bytes();
    }

    /// Clave actual de la capa (efímera, por pulso).
    pub fn current_key(&self) -> [u8; 32] {
        *self.key_cache.lock().unwrap()
    }

    /// Cifra un payload de la capa con la clave de pulso actual.
    /// Nonce 12 bytes derivado del pulso (determinista para el descifrador
    /// sincronizado por el mismo cristal).
    pub fn encrypt(&self, plaintext: &[u8]) -> Option<Vec<u8>> {
        let key = self.current_key();
        let cipher = Aes256Gcm::new(&key.into());
        let nonce = self.nonce_for_pulse();
        let payload = Payload { msg: plaintext, aad: b"sentinel-crystal-layer" };
        cipher.encrypt((&nonce).into(), payload).ok()
    }

    /// Descifra un payload de la capa. Requiere el mismo pulso/cristal.
    pub fn decrypt(&self, ciphertext: &[u8]) -> Option<Vec<u8>> {
        let key = self.current_key();
        let cipher = Aes256Gcm::new(&key.into());
        let nonce = self.nonce_for_pulse();
        let payload = Payload { msg: ciphertext, aad: b"sentinel-crystal-layer" };
        cipher.decrypt((&nonce).into(), payload).ok()
    }

    fn nonce_for_pulse(&self) -> [u8; 12] {
        let mut n = [0u8; 12];
        let p = self.pulse.to_le_bytes();
        n[..8].copy_from_slice(&p);
        let phase_lo = (self.crystal.lock().unwrap().get_phase().to_raw() & 0xFFFF_FFFF) as u32;
        n[8..].copy_from_slice(&phase_lo.to_le_bytes());
        n
    }

    /// Fuerza una rotación manual (purga de entropía -> nueva clave).
    pub fn force_rotate(&mut self) {
        self.rotate();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_same_phase_same_key() {
        // Dos cifradores con el mismo cristal (misma fase de arranque) -> misma clave.
        let a = CrystalCipher::new("Test-A");
        let b = CrystalCipher::new("Test-A");
        assert_eq!(a.current_key(), b.current_key());
    }

    #[test]
    fn test_encrypt_decrypt_roundtrip() {
        let c = CrystalCipher::new("Layer-Test");
        let pt = b"guardian-link: watchdog<->cortex<->A<->B";
        let ct = c.encrypt(pt).expect("encrypt fallo");
        let dt = c.decrypt(&ct).expect("decrypt fallo");
        assert_eq!(dt, pt);
    }

    #[test]
    fn test_pulse_rotates_key() {
        let mut c = CrystalCipher::new("Rot-Test");
        let k0 = c.current_key();
        // 4 breath -> master cycle -> rotate
        for _ in 0..4 {
            c.tick_breath();
        }
        let k1 = c.current_key();
        assert_ne!(k0, k1, "la clave debe rotar cada master cycle");
    }

    #[test]
    fn test_different_crystal_different_key() {
        // Dos cifradores: uno late 4 breath (master cycle), otro queda en pulso 0.
        // Misma fase de arranque pero pulso distinto -> clave distinta (aislamiento).
        let mut c1 = CrystalCipher::new("Iso-1");
        for _ in 0..4 {
            c1.tick_breath();
        }
        let c2 = CrystalCipher::new("Iso-1"); // pulso 0, fase de arranque
        assert_ne!(c1.current_key(), c2.current_key());
    }
}
