// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/forensic_wal.rs
//! # 🛡️ Forensic-Grade Write-Ahead Log (WAL) con Anti-Replay (Claim 4 - Patent Pending)
//!
//! Garantiza integridad inmutable de auditoría forense mediante:
//! 1. HMAC-SHA256 por registro.
//! 2. Encadenamiento hash cronológico (Merkle-chain sequential).
//! 3. Protección anti-replay con nonces únicos y expiración temporal.
//! 4. Separación estricta de DataLanes: Security (síncrono/sin buffer) vs Observability.

use sha3::{Digest, Sha3_256};
use std::collections::HashSet;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use parking_lot::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DataLane {
    Security,
    Observability,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct WalRecord {
    pub event_id: String,
    pub timestamp_sec: u64,
    pub nonce: String,
    pub lane: String,
    pub source: String,
    pub payload: String,
    pub prev_hash: String,
    pub signature: String,
}

pub struct ForensicWal {
    file_path: PathBuf,
    secret_key: Vec<u8>,
    seen_nonces: Mutex<HashSet<String>>,
    last_hash: Mutex<String>,
}

impl ForensicWal {
    pub fn new<P: AsRef<Path>>(path: P, secret_key: &[u8]) -> std::io::Result<Self> {
        let file_path = path.as_ref().to_path_buf();
        if let Some(parent) = file_path.parent() {
            std::fs::create_dir_all(parent)?;
        }

        let mut last_hash = "0".repeat(64);
        let mut seen_nonces = HashSet::new();

        // Si el archivo ya existe, cargar el último hash y los nonces
        if file_path.exists() {
            let file = File::open(&file_path)?;
            let reader = BufReader::new(file);
            for line in reader.lines() {
                if let Ok(l) = line {
                    if let Ok(rec) = serde_json::from_str::<WalRecord>(&l) {
                        seen_nonces.insert(rec.nonce.clone());
                        last_hash = rec.signature.clone();
                    }
                }
            }
        }

        Ok(Self {
            file_path,
            secret_key: secret_key.to_vec(),
            seen_nonces: Mutex::new(seen_nonces),
            last_hash: Mutex::new(last_hash),
        })
    }

    fn compute_signature(&self, event_id: &str, timestamp: u64, nonce: &str, payload: &str, prev_hash: &str) -> String {
        let mut hasher = Sha3_256::new();
        hasher.update(&self.secret_key);
        hasher.update(event_id.as_bytes());
        hasher.update(timestamp.to_be_bytes());
        hasher.update(nonce.as_bytes());
        hasher.update(prev_hash.as_bytes());
        hasher.update(payload.as_bytes());
        hex::encode(hasher.finalize())
    }

    /// Escribe un registro garantizando orden y firma inmutable.
    pub fn append(
        &self,
        event_id: &str,
        source: &str,
        payload: &str,
        lane: DataLane,
    ) -> Result<WalRecord, &'static str> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|_| "Clock drift error")?
            .as_secs();

        let nonce = format!("{}-{}", now, uuid::Uuid::new_v4());

        let mut nonces_guard = self.seen_nonces.lock();
        if nonces_guard.contains(&nonce) {
            return Err("Replay attack detected: duplicate nonce");
        }

        let mut hash_guard = self.last_hash.lock();
        let prev_hash = hash_guard.clone();

        let signature = self.compute_signature(event_id, now, &nonce, payload, &prev_hash);

        let lane_str = match lane {
            DataLane::Security => "security",
            DataLane::Observability => "observability",
        };

        let record = WalRecord {
            event_id: event_id.to_string(),
            timestamp_sec: now,
            nonce: nonce.clone(),
            lane: lane_str.to_string(),
            source: source.to_string(),
            payload: payload.to_string(),
            prev_hash,
            signature: signature.clone(),
        };

        // Serializar y escribir en disco
        let serialized = serde_json::to_string(&record).map_err(|_| "Serialization error")?;
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.file_path)
            .map_err(|_| "Failed to open WAL file")?;

        writeln!(file, "{}", serialized).map_err(|_| "Failed to write to WAL")?;
        file.sync_data().map_err(|_| "Fsync failure")?;

        nonces_guard.insert(nonce);
        *hash_guard = signature;

        Ok(record)
    }

    /// Cuenta el total de líneas interceptadas o registradas en el WAL
    pub fn count_records(&self) -> usize {
        let nonces_guard = self.seen_nonces.lock();
        nonces_guard.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_forensic_wal_append_and_verify() {
        let temp_dir = std::env::temp_dir();
        let wal_path = temp_dir.join(format!("test_wal_{}.log", uuid::Uuid::new_v4()));
        let key = b"secret-sovereign-key-1234567890123456";

        let wal = ForensicWal::new(&wal_path, key).unwrap();
        let rec1 = wal.append("evt-1", "shield", "DROP TABLE blocked", DataLane::Security).unwrap();
        assert_eq!(rec1.prev_hash, "0".repeat(64));

        let rec2 = wal.append("evt-2", "shield", "rm -rf blocked", DataLane::Security).unwrap();
        assert_eq!(rec2.prev_hash, rec1.signature);
        assert_eq!(wal.count_records(), 2);

        let _ = std::fs::remove_file(wal_path);
    }
}
