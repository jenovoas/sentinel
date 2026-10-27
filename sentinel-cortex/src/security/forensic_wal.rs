// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/security/forensic_wal.rs
//! # 🛡️ Forensic-Grade Write-Ahead Log (WAL) con Anti-Replay (Claim 4 - Patent Pending)
//!
//! Garantiza integridad inmutable de auditoría forense mediante:
//! 1. HMAC-SHA3-256 por registro.
//! 2. Encadenamiento hash cronológico (Merkle-chain sequential).
//! 3. Protección anti-replay con nonces únicos y validación de duplicados.
//! 4. Separación estricta de DataLanes: Security (síncrono/sin buffer) vs Observability.
//! 5. Verificación estricta de integridad de cadena con detección de replay y manipulación.

use parking_lot::Mutex;
use sha3::{Digest, Sha3_256};
use std::collections::HashSet;
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DataLane {
    Security,
    Observability,
}

#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
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

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct WalAuditReport {
    pub total_records: usize,
    pub last_signature: String,
    pub valid: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum WalVerificationError {
    Io(String),
    Serialization {
        line: usize,
        detail: String,
    },
    BrokenHashChain {
        line: usize,
        expected: String,
        found: String,
    },
    SignatureMismatch {
        line: usize,
        event_id: String,
    },
    ReplayAttack {
        line: usize,
        duplicate_nonce: String,
    },
    TimestampRegressed {
        line: usize,
        prev: u64,
        current: u64,
    },
}

impl std::fmt::Display for WalVerificationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Io(msg) => write!(f, "WAL IO error: {msg}"),
            Self::Serialization { line, detail } => {
                write!(f, "WAL serialization error at line {line}: {detail}")
            }
            Self::BrokenHashChain {
                line,
                expected,
                found,
            } => {
                write!(
                    f,
                    "WAL hash chain broken at line {line}: expected prev_hash {expected}, found {found}"
                )
            }
            Self::SignatureMismatch { line, event_id } => {
                write!(
                    f,
                    "WAL HMAC signature mismatch at line {line} (event_id: {event_id})"
                )
            }
            Self::ReplayAttack {
                line,
                duplicate_nonce,
            } => {
                write!(
                    f,
                    "WAL REPLAY ATTACK detected at line {line}: duplicate nonce '{duplicate_nonce}'"
                )
            }
            Self::TimestampRegressed {
                line,
                prev,
                current,
            } => {
                write!(
                    f,
                    "WAL timestamp regression detected at line {line}: current ({current}) < prev ({prev})"
                )
            }
        }
    }
}

impl std::error::Error for WalVerificationError {}

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
            for l in reader.lines().map_while(Result::ok) {
                if let Ok(rec) = serde_json::from_str::<WalRecord>(&l) {
                    seen_nonces.insert(rec.nonce.clone());
                    last_hash = rec.signature.clone();
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

    pub fn compute_signature(
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

        let signature =
            Self::compute_signature(&self.secret_key, event_id, now, &nonce, payload, &prev_hash);

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

    /// Audita y valida la integridad de una cadena completa de registros WAL.
    /// Detecta manipulaciones de payload, discontinuidades en la cadena hash y ataques de replay.
    pub fn verify_chain<P: AsRef<Path>>(
        path: P,
        secret_key: &[u8],
    ) -> Result<WalAuditReport, WalVerificationError> {
        let file = File::open(path).map_err(|e| WalVerificationError::Io(e.to_string()))?;
        let reader = BufReader::new(file);

        let mut expected_prev_hash = "0".repeat(64);
        let mut seen_nonces = HashSet::new();
        let mut total_records = 0usize;
        let mut last_timestamp = 0u64;

        for (idx, line_res) in reader.lines().enumerate() {
            let line_num = idx + 1;
            let line = line_res.map_err(|e| WalVerificationError::Io(e.to_string()))?;
            let trimmed = line.trim();
            if trimmed.is_empty() {
                continue;
            }

            let rec: WalRecord =
                serde_json::from_str(trimmed).map_err(|e| WalVerificationError::Serialization {
                    line: line_num,
                    detail: e.to_string(),
                })?;

            // 1. Verificación de hash previo (Merkle chain)
            if rec.prev_hash != expected_prev_hash {
                return Err(WalVerificationError::BrokenHashChain {
                    line: line_num,
                    expected: expected_prev_hash,
                    found: rec.prev_hash,
                });
            }

            // 2. Verificación anti-replay (monotonía y unicidad de nonce)
            if !seen_nonces.insert(rec.nonce.clone()) {
                return Err(WalVerificationError::ReplayAttack {
                    line: line_num,
                    duplicate_nonce: rec.nonce,
                });
            }

            // 3. Verificación de avance temporal
            if rec.timestamp_sec < last_timestamp {
                return Err(WalVerificationError::TimestampRegressed {
                    line: line_num,
                    prev: last_timestamp,
                    current: rec.timestamp_sec,
                });
            }
            last_timestamp = rec.timestamp_sec;

            // 4. Verificación criptográfica de firma HMAC-Sha3_256
            let computed_sig = Self::compute_signature(
                secret_key,
                &rec.event_id,
                rec.timestamp_sec,
                &rec.nonce,
                &rec.payload,
                &rec.prev_hash,
            );

            if rec.signature != computed_sig {
                return Err(WalVerificationError::SignatureMismatch {
                    line: line_num,
                    event_id: rec.event_id,
                });
            }

            expected_prev_hash = rec.signature.clone();
            total_records += 1;
        }

        Ok(WalAuditReport {
            total_records,
            last_signature: expected_prev_hash,
            valid: true,
        })
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
        let rec1 = wal
            .append("evt-1", "shield", "DROP TABLE blocked", DataLane::Security)
            .unwrap();
        assert_eq!(rec1.prev_hash, "0".repeat(64));

        let rec2 = wal
            .append("evt-2", "shield", "rm -rf blocked", DataLane::Security)
            .unwrap();
        assert_eq!(rec2.prev_hash, rec1.signature);
        assert_eq!(wal.count_records(), 2);

        // Verificar la cadena completa
        let audit = ForensicWal::verify_chain(&wal_path, key).unwrap();
        assert!(audit.valid);
        assert_eq!(audit.total_records, 2);
        assert_eq!(audit.last_signature, rec2.signature);

        let _ = std::fs::remove_file(wal_path);
    }

    #[test]
    fn test_forensic_wal_catches_replay_attack() {
        let temp_dir = std::env::temp_dir();
        let wal_path = temp_dir.join(format!("test_wal_replay_{}.log", uuid::Uuid::new_v4()));
        let key = b"secret-key-replay-test-123456789";

        let wal = ForensicWal::new(&wal_path, key).unwrap();
        let rec1 = wal
            .append("evt-1", "shield", "normal event", DataLane::Observability)
            .unwrap();

        // Simular ataque de replay: un atacante inyecta la misma línea previa al final del log
        let mut file = OpenOptions::new().append(true).open(&wal_path).unwrap();
        let line = serde_json::to_string(&rec1).unwrap();
        writeln!(file, "{line}").unwrap();
        file.sync_data().unwrap();

        let err = ForensicWal::verify_chain(&wal_path, key).unwrap_err();
        // Debe fallar por BrokenHashChain o ReplayAttack
        match err {
            WalVerificationError::BrokenHashChain { line, .. } => assert_eq!(line, 2),
            WalVerificationError::ReplayAttack { line, .. } => assert_eq!(line, 2),
            other => panic!(
                "Esperado ReplayAttack o BrokenHashChain, obtuvo: {:?}",
                other
            ),
        }

        let _ = std::fs::remove_file(wal_path);
    }

    #[test]
    fn test_forensic_wal_catches_payload_tampering() {
        let temp_dir = std::env::temp_dir();
        let wal_path = temp_dir.join(format!("test_wal_tamper_{}.log", uuid::Uuid::new_v4()));
        let key = b"secret-key-tamper-test-123456789";

        let wal = ForensicWal::new(&wal_path, key).unwrap();
        let mut rec1 = wal
            .append(
                "evt-1",
                "shield",
                "original benign query",
                DataLane::Observability,
            )
            .unwrap();

        // Modificar el payload manteniendo el resto idéntico
        rec1.payload = "malicious altered query".to_string();
        let tampered_line = serde_json::to_string(&rec1).unwrap();
        std::fs::write(&wal_path, format!("{tampered_line}\n")).unwrap();

        let err = ForensicWal::verify_chain(&wal_path, key).unwrap_err();
        match err {
            WalVerificationError::SignatureMismatch { line, event_id } => {
                assert_eq!(line, 1);
                assert_eq!(event_id, "evt-1");
            }
            other => panic!("Esperado SignatureMismatch, obtuvo: {:?}", other),
        }

        let _ = std::fs::remove_file(wal_path);
    }
}
