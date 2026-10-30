// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/forensic_wal.rs
//! # 🛡️ Forensic-Grade Write-Ahead Log (WAL) con Anti-Replay (Claim 4 - Patent Pending)
//!
//! Garantiza integridad inmutable de auditoría forense mediante:
//! 1. Firma legacy versión 0 y HMAC-SHA3-256 en registros nuevos versión 2.
//! 2. Encadenamiento hash cronológico (Merkle-chain sequential).
//! 3. Protección anti-replay con nonces únicos y expiración temporal.
//! 4. Separación estricta de DataLanes: Security (síncrono/sin buffer) vs Observability.

use hmac::{KeyInit, Mac, SimpleHmac};
use parking_lot::Mutex;
use sha3::{Digest, Sha3_256};
use std::collections::HashSet;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::os::unix::fs::OpenOptionsExt;
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DataLane {
    Security,
    Observability,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct WalRecord {
    #[serde(default)]
    pub schema_version: u8,
    pub event_id: String,
    pub timestamp_sec: u64,
    pub nonce: String,
    pub lane: String,
    pub source: String,
    pub payload: String,
    pub prev_hash: String,
    pub signature: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WalAuditReport {
    pub total_records: usize,
    pub last_signature: String,
}

#[derive(Debug, thiserror::Error)]
pub enum WalVerificationError {
    #[error("WAL I/O error: {0}")]
    Io(String),
    #[error("Invalid WAL record at line {line}: {detail}")]
    Serialization { line: usize, detail: String },
    #[error("Unsupported WAL schema version {version} at line {line}")]
    UnsupportedVersion { line: usize, version: u8 },
    #[error("Broken WAL chain at line {line}: expected {expected}, found {found}")]
    BrokenHashChain {
        line: usize,
        expected: String,
        found: String,
    },
    #[error("WAL signature mismatch at line {line} (event {event_id})")]
    SignatureMismatch { line: usize, event_id: String },
    #[error("Repeated WAL nonce at line {line}")]
    ReplayAttack { line: usize },
    #[error("WAL timestamp regressed at line {line}: {current} < {previous}")]
    TimestampRegressed {
        line: usize,
        previous: u64,
        current: u64,
    },
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

        // No se permite añadir sobre un WAL corrupto: eso ocultaría la corrupción previa.
        if file_path.exists() {
            Self::verify_chain(&file_path, secret_key)
                .map_err(|error| std::io::Error::new(std::io::ErrorKind::InvalidData, error))?;
            let file = File::open(&file_path)?;
            let reader = BufReader::new(file);
            for line in reader.lines() {
                let line = line?;
                if line.trim().is_empty() {
                    continue;
                }
                let rec: WalRecord = serde_json::from_str(&line)
                    .map_err(|error| std::io::Error::new(std::io::ErrorKind::InvalidData, error))?;
                seen_nonces.insert(rec.nonce);
                last_hash = rec.signature;
            }
        }

        Ok(Self {
            file_path,
            secret_key: secret_key.to_vec(),
            seen_nonces: Mutex::new(seen_nonces),
            last_hash: Mutex::new(last_hash),
        })
    }

    fn compute_legacy_signature(
        secret_key: &[u8],
        event_id: &str,
        timestamp: u64,
        nonce: &str,
        payload: &str,
        prev_hash: &str,
    ) -> String {
        let mut hasher = Sha3_256::new();
        hasher.update(secret_key);
        hasher.update(event_id.as_bytes());
        hasher.update(timestamp.to_be_bytes());
        hasher.update(nonce.as_bytes());
        hasher.update(prev_hash.as_bytes());
        hasher.update(payload.as_bytes());
        hex::encode(hasher.finalize())
    }

    fn compute_v2_signature(record: &WalRecord, secret_key: &[u8]) -> String {
        let mut mac = SimpleHmac::<Sha3_256>::new_from_slice(secret_key)
            .expect("HMAC accepts keys of any length");
        mac.update(b"sentinel-forensic-wal-v2\0");
        let timestamp = record.timestamp_sec.to_be_bytes();
        for field in [
            record.event_id.as_bytes(),
            timestamp.as_slice(),
            record.nonce.as_bytes(),
            record.lane.as_bytes(),
            record.source.as_bytes(),
            record.payload.as_bytes(),
            record.prev_hash.as_bytes(),
        ] {
            let field_len = u64::try_from(field.len()).expect("field length fits in u64");
            mac.update(&field_len.to_be_bytes());
            mac.update(field);
        }
        hex::encode(mac.finalize().into_bytes())
    }

    /// Audita cada registro antes de aceptar una cadena como base para nuevas escrituras.
    pub fn verify_chain<P: AsRef<Path>>(
        path: P,
        secret_key: &[u8],
    ) -> Result<WalAuditReport, WalVerificationError> {
        let file = File::open(path).map_err(|error| WalVerificationError::Io(error.to_string()))?;
        let reader = BufReader::new(file);
        let mut expected_prev_hash = "0".repeat(64);
        let mut seen_nonces = HashSet::new();
        let mut total_records = 0;
        let mut last_timestamp = 0;

        for (index, line_result) in reader.lines().enumerate() {
            let line_number = index + 1;
            let line = line_result.map_err(|error| WalVerificationError::Io(error.to_string()))?;
            if line.trim().is_empty() {
                continue;
            }
            let record: WalRecord = serde_json::from_str(line.trim()).map_err(|error| {
                WalVerificationError::Serialization {
                    line: line_number,
                    detail: error.to_string(),
                }
            })?;
            if record.schema_version != 0 && record.schema_version != 2 {
                return Err(WalVerificationError::UnsupportedVersion {
                    line: line_number,
                    version: record.schema_version,
                });
            }
            if record.prev_hash != expected_prev_hash {
                return Err(WalVerificationError::BrokenHashChain {
                    line: line_number,
                    expected: expected_prev_hash,
                    found: record.prev_hash,
                });
            }
            if !seen_nonces.insert(record.nonce.clone()) {
                return Err(WalVerificationError::ReplayAttack { line: line_number });
            }
            if record.timestamp_sec < last_timestamp {
                return Err(WalVerificationError::TimestampRegressed {
                    line: line_number,
                    previous: last_timestamp,
                    current: record.timestamp_sec,
                });
            }
            last_timestamp = record.timestamp_sec;

            let signature = if record.schema_version == 0 {
                Self::compute_legacy_signature(
                    secret_key,
                    &record.event_id,
                    record.timestamp_sec,
                    &record.nonce,
                    &record.payload,
                    &record.prev_hash,
                )
            } else {
                Self::compute_v2_signature(&record, secret_key)
            };
            if record.signature != signature {
                return Err(WalVerificationError::SignatureMismatch {
                    line: line_number,
                    event_id: record.event_id,
                });
            }
            expected_prev_hash = record.signature;
            total_records += 1;
        }

        Ok(WalAuditReport {
            total_records,
            last_signature: expected_prev_hash,
        })
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

        let lane_str = match lane {
            DataLane::Security => "security",
            DataLane::Observability => "observability",
        };

        let record = WalRecord {
            schema_version: 2,
            event_id: event_id.to_string(),
            timestamp_sec: now,
            nonce: nonce.clone(),
            lane: lane_str.to_string(),
            source: source.to_string(),
            payload: payload.to_string(),
            prev_hash,
            signature: String::new(),
        };
        let signature = Self::compute_v2_signature(&record, &self.secret_key);
        let mut record = record;
        record.signature = signature.clone();

        // Serializar y escribir en disco
        let serialized = serde_json::to_string(&record).map_err(|_| "Serialization error")?;
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .mode(0o600)
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
        let key = [
            *uuid::Uuid::new_v4().as_bytes(),
            *uuid::Uuid::new_v4().as_bytes(),
        ]
        .concat();

        let wal = ForensicWal::new(&wal_path, &key).unwrap();
        let rec1 = wal
            .append("evt-1", "shield", "DROP TABLE blocked", DataLane::Security)
            .unwrap();
        assert_eq!(rec1.prev_hash, "0".repeat(64));

        let rec2 = wal
            .append("evt-2", "shield", "rm -rf blocked", DataLane::Security)
            .unwrap();
        assert_eq!(rec2.prev_hash, rec1.signature);
        assert_eq!(wal.count_records(), 2);

        let _ = std::fs::remove_file(wal_path);
    }
}
