// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ DUAL-LANE ROUTER (RUST PURO) 🛡️
//!
//! Arquitectura de doble carril para separar flujos de datos:
//! - Security & Audit Lane: determinista, SIN buffering, WAL obligatorio (fsync).
//! - Observability & Trends Lane: buffering permitido, backpressure, reorder.
//!
//! Migrado de `backend/app/core/data_lanes.py` (recuperado de purge aed3b377^).
//! ELIMINA RIESGOS EXISTENCIALES: out-of-order en Loki, ventana de ceguera,
//! OOM por buffering, fabricación de evidencia por regeneración.
//!
//! NOTA: esto es routing/forense, NO aritmética de cristal. Por eso el
//! timestamp vive en i64 micros y las latencias en u64 ms — SIN float en
//! el core (cumple YATRA: el float solo aparece en I/O de borde si acaso).
//! Los TODOs del .py (dual_guardian, forensic_storage, loki_client) NO se
//! inventan: el Security WAL escribe al mismo archivo que sentinel-cortex
//! (/var/log/sentinel/security_wal.log) de forma síncrona.

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

/// Carril de datos.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DataLane {
    Security,
    Observability,
}

impl DataLane {
    pub fn as_str(&self) -> &'static str {
        match self {
            DataLane::Security => "security",
            DataLane::Observability => "observability",
        }
    }
}

/// Prioridad de evento para routing.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum EventPriority {
    Low,
    Medium,
    High,
    Critical,
}

impl EventPriority {
    pub fn as_str(&self) -> &'static str {
        match self {
            EventPriority::Low => "low",
            EventPriority::Medium => "medium",
            EventPriority::High => "high",
            EventPriority::Critical => "critical",
        }
    }
}

/// Evento con metadata de carril.
#[derive(Debug, Clone)]
pub struct LaneEvent {
    pub lane: DataLane,
    pub source: String,
    pub priority: EventPriority,
    /// Timestamp de recolección en microsegundos (UTC epoch). NO es float.
    pub timestamp_us: i64,
    pub labels: HashMap<String, String>,
    /// Payload serializado (JSON) para WAL/Loki.
    pub data: String,
    /// Si es dato imputado/regenerado (anti-fabricación de evidencia).
    pub synthetic: bool,
}

impl LaneEvent {
    pub fn to_json(&self) -> String {
        // Serialización manual mínima (sin dep externa en core).
        let mut labels = String::new();
        for (i, (k, v)) in self.labels.iter().enumerate() {
            if i > 0 {
                labels.push(',');
            }
            labels.push_str(&format!("\"{}\":\"{}\"", escape(k), escape(v)));
        }
        format!(
            "{{\"lane\":\"{}\",\"source\":\"{}\",\"priority\":\"{}\",\"timestamp_us\":{},\"labels\":{{{}}},\"data\":{},\"synthetic\":{}}}",
            self.lane.as_str(),
            escape(&self.source),
            self.priority.as_str(),
            self.timestamp_us,
            labels,
            self.data,
            self.synthetic,
        )
    }

    /// Ordena por (timestamp) para evitar out-of-order en WAL/Loki.
    pub fn cmp_timestamp(&self, other: &LaneEvent) -> std::cmp::Ordering {
        self.timestamp_us.cmp(&other.timestamp_us)
    }
}

fn escape(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
}

fn now_micros() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_micros() as i64)
        .unwrap_or(0)
}

/// Router de eventos a carriles según origen y contenido.
pub struct DualLaneRouter {
    security_sources: Vec<&'static str>,
    security_events: u64,
    observability_events: u64,
    misrouted_events: u64,
}

impl DualLaneRouter {
    pub fn new() -> Self {
        Self {
            security_sources: vec![
                "auditd", "ebpf", "shield", "dual_guardian", "kernel", "syscall",
                "biometric", "soul_verifier", "rppg", "authentication",
            ],
            security_events: 0,
            observability_events: 0,
            misrouted_events: 0,
        }
    }

    /// Clasifica evento por source / labels / contenido de data.
    pub fn classify_event(
        &mut self,
        source: &str,
        data: &str,
        labels: Option<HashMap<String, String>>,
    ) -> LaneEvent {
        let labels = labels.unwrap_or_default();
        let mut labels = labels;

        let (lane, priority) = if self.security_sources.iter().any(|s| *s == source) {
            self.security_events += 1;
            (DataLane::Security, EventPriority::Critical)
        } else if labels.keys().any(|k| {
            k == "threat" || k == "attack" || k == "malicious"
        }) {
            self.security_events += 1;
            (DataLane::Security, EventPriority::High)
        } else if contains_any(data.to_lowercase().as_str(), &["malicious", "blocked", "threat", "attack"]) {
            self.security_events += 1;
            (DataLane::Security, EventPriority::High)
        } else {
            self.observability_events += 1;
            (DataLane::Observability, EventPriority::Medium)
        };

        labels.insert("lane".to_string(), lane.as_str().to_string());
        labels.insert("source".to_string(), source.to_string());
        labels.insert("priority".to_string(), priority.as_str().to_string());

        LaneEvent {
            lane,
            source: source.to_string(),
            priority,
            timestamp_us: now_micros(),
            labels,
            data: data.to_string(),
            synthetic: false,
        }
    }

    /// Security lane SIEMPRE bypass; Observability solo si CRITICAL.
    pub fn should_bypass_buffer(&self, event: &LaneEvent) -> bool {
        event.lane == DataLane::Security || event.priority == EventPriority::Critical
    }

    pub fn stats(&self) -> (u64, u64, u64) {
        (self.security_events, self.observability_events, self.misrouted_events)
    }
}

fn contains_any(haystack: &str, needles: &[&str]) -> bool {
    needles.iter().any(|n| haystack.contains(n))
}

/// Collector de Security Lane: SIN buffering, WAL fsync obligatorio.
pub struct SecurityLaneCollector {
    wal_path: PathBuf,
    events_collected: u64,
    events_lost: u64,
    /// Latencia acumulada en ms para promedio (entero, sin float en core).
    latency_ms_total: u64,
    latency_samples: u64,
}

impl SecurityLaneCollector {
    pub fn new(wal_path: PathBuf) -> Self {
        Self {
            wal_path,
            events_collected: 0,
            events_lost: 0,
            latency_ms_total: 0,
            latency_samples: 0,
        }
    }

    /// Emite inmediatamente (sin buffer). WAL con fsync síncrono.
    /// Retorna true si se escribió, false si hubo pérdida (y alerta).
    pub fn emit_immediate(&mut self, event: &LaneEvent) -> bool {
        let start = now_micros();
        let entry = format!("{}\n", event.to_json());
        match OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.wal_path)
            .and_then(|mut f| {
                f.write_all(entry.as_bytes())?;
                f.sync_all()?; // fsync: durabilidad forense
                Ok(())
            })
        {
            Ok(()) => {
                let latency_ms = ((now_micros() - start) as u64).max(1) / 1000;
                self.latency_ms_total += latency_ms;
                self.latency_samples += 1;
                self.events_collected += 1;
                if latency_ms > 10 {
                    eprintln!(
                        "⚠️ Security lane latency high: {}ms (target <10ms)",
                        latency_ms
                    );
                }
                true
            }
            Err(e) => {
                self.events_lost += 1;
                eprintln!(
                    "🚨 INTEGRITY GAP: Security event lost | source={} | ts={} | err={}",
                    event.source, event.timestamp_us, e
                );
                false
            }
        }
    }

    pub fn loss_rate(&self) -> f64 {
        let total = self.events_collected + self.events_lost;
        if total == 0 {
            0.0
        } else {
            self.events_lost as f64 / total as f64
        }
    }

    pub fn avg_latency_ms(&self) -> u64 {
        if self.latency_samples == 0 {
            0
        } else {
            self.latency_ms_total / self.latency_samples
        }
    }
}

/// Collector de Observability Lane: buffering + backpressure + reorder.
pub struct ObservabilityLaneCollector {
    wal_path: PathBuf,
    max_buffer_bytes: usize,
    max_batch_records: usize,
    max_batch_ms: u64,
    buffer: Vec<LaneEvent>,
    buffer_bytes: usize,
    last_flush_us: i64,
    events_collected: u64,
    events_buffered: u64,
    events_flushed: u64,
    events_dropped: u64,
    backpressure_activations: u64,
    avg_batch_size: u64,
}

impl ObservabilityLaneCollector {
    pub fn new(wal_path: PathBuf) -> Self {
        Self {
            wal_path,
            max_buffer_bytes: 10 * 1024 * 1024,
            max_batch_records: 1000,
            max_batch_ms: 1000,
            buffer: Vec::new(),
            buffer_bytes: 0,
            last_flush_us: now_micros(),
            events_collected: 0,
            events_buffered: 0,
            events_flushed: 0,
            events_dropped: 0,
            backpressure_activations: 0,
            avg_batch_size: 0,
        }
    }

    /// Emite con buffering. Flush si batch lleno o timeout.
    pub fn emit_buffered(&mut self, event: LaneEvent) -> bool {
        let event_bytes = event.to_json().len();
        // Backpressure: si no cabe, flush y si aún no cabe, drop menor prioridad.
        if self.buffer_bytes + event_bytes > self.max_buffer_bytes {
            eprintln!(
                "⚠️ Backpressure activated: buffer {}MB",
                self.buffer_bytes / 1024 / 1024
            );
            self.backpressure_activations += 1;
            self.flush_buffer();
            // Si aún no cabe tras flush:
            if self.buffer_bytes + event_bytes > self.max_buffer_bytes {
                // El evento individual excede el buffer: no puede bufferizarse.
                // Drop primero uno existente de menor prioridad para hacer espacio;
                // si el entrante sigue sin caber, se descarta (backpressure duro).
                if let Some(dropped) = self.drop_lowest_priority() {
                    eprintln!(
                        "ℹ️ Dropped buffered event: {} (priority={})",
                        dropped.source,
                        dropped.priority.as_str()
                    );
                }
                if self.buffer_bytes + event_bytes > self.max_buffer_bytes {
                    self.events_dropped += 1;
                    self.events_collected += 1;
                    return false;
                }
            }
        }

        self.buffer.push(event);
        self.buffer_bytes += event_bytes;
        self.events_buffered += 1;

        let now = now_micros();
        let should_flush = self.buffer.len() >= self.max_batch_records
            || ((now - self.last_flush_us) as u64) >= self.max_batch_ms;
        if should_flush {
            self.flush_buffer();
        }
        true
    }

    /// Fuerza flush del buffer (reordenado por timestamp). Útil al final del run.
    pub fn flush(&mut self) {
        self.flush_buffer();
    }

    /// Flush con reordenamiento por timestamp (anti out-of-order).
    fn flush_buffer(&mut self) {
        if self.buffer.is_empty() {
            return;
        }
        self.buffer.sort_by(|a, b| a.cmp_timestamp(b));
        let mut written = 0u64;
        if let Ok(mut f) = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.wal_path)
        {
            for ev in &self.buffer {
                let entry = format!("{}\n", ev.to_json());
                if f.write_all(entry.as_bytes()).is_ok() {
                    written += 1;
                }
            }
            let _ = f.sync_all();
        }
        if written < self.buffer.len() as u64 {
            eprintln!(
                "⚠️ WAL batch write incomplete: {}/{}",
                written,
                self.buffer.len()
            );
        }
        let batch_size = self.buffer.len() as u64;
        self.events_flushed += batch_size;
        if self.events_flushed > 0 {
            self.avg_batch_size = (self.avg_batch_size
                * (self.events_flushed - batch_size)
                + batch_size)
                / self.events_flushed;
        }
        self.buffer.clear();
        self.buffer_bytes = 0;
        self.last_flush_us = now_micros();
    }

    /// Drop evento de menor prioridad (LOW → MEDIUM → HIGH; nunca CRITICAL).
    fn drop_lowest_priority(&mut self) -> Option<LaneEvent> {
        for prio in [EventPriority::Low, EventPriority::Medium, EventPriority::High] {
            if let Some(pos) = self.buffer.iter().position(|e| e.priority == prio) {
                let dropped = self.buffer.remove(pos);
                self.buffer_bytes -= dropped.to_json().len();
                self.events_dropped += 1;
                return Some(dropped);
            }
        }
        None
    }

    pub fn drop_rate(&self) -> f64 {
        if self.events_collected == 0 {
            0.0
        } else {
            self.events_dropped as f64 / self.events_collected as f64
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_security_source_routes_to_security() {
        let mut router = DualLaneRouter::new();
        let ev = router.classify_event("auditd", "{}", None);
        assert_eq!(ev.lane, DataLane::Security);
        assert_eq!(ev.priority, EventPriority::Critical);
    }

    #[test]
    fn test_threat_label_routes_to_security_high() {
        let mut router = DualLaneRouter::new();
        let mut labels = HashMap::new();
        labels.insert("threat".to_string(), "1".to_string());
        let ev = router.classify_event("app", "{}", Some(labels));
        assert_eq!(ev.lane, DataLane::Security);
        assert_eq!(ev.priority, EventPriority::High);
    }

    #[test]
    fn test_malicious_data_routes_to_security() {
        let mut router = DualLaneRouter::new();
        let ev = router.classify_event("app", "{\"note\":\"malicious payload\"}", None);
        assert_eq!(ev.lane, DataLane::Security);
    }

    #[test]
    fn test_default_routes_to_observability() {
        let mut router = DualLaneRouter::new();
        let ev = router.classify_event("prometheus", "{}", None);
        assert_eq!(ev.lane, DataLane::Observability);
        assert_eq!(ev.priority, EventPriority::Medium);
        assert!(!ev.synthetic);
    }

    #[test]
    fn test_should_bypass_buffer() {
        let router = DualLaneRouter::new();
        let sec = LaneEvent {
            lane: DataLane::Security,
            source: "auditd".into(),
            priority: EventPriority::Critical,
            timestamp_us: 0,
            labels: HashMap::new(),
            data: "{}".into(),
            synthetic: false,
        };
        assert!(router.should_bypass_buffer(&sec));
        let obs = LaneEvent {
            lane: DataLane::Observability,
            source: "app".into(),
            priority: EventPriority::Medium,
            timestamp_us: 0,
            labels: HashMap::new(),
            data: "{}".into(),
            synthetic: false,
        };
        assert!(!router.should_bypass_buffer(&obs));
    }

    #[test]
    fn test_security_wal_write_and_fsync() {
        let dir = std::env::temp_dir();
        let wal = dir.join(format!("sentinel_test_wal_{}.log", std::process::id()));
        let mut col = SecurityLaneCollector::new(wal.clone());
        let ev = LaneEvent {
            lane: DataLane::Security,
            source: "auditd".into(),
            priority: EventPriority::Critical,
            timestamp_us: 123456,
            labels: HashMap::new(),
            data: "{\"x\":1}".into(),
            synthetic: false,
        };
        assert!(col.emit_immediate(&ev));
        assert_eq!(col.events_collected, 1);
        assert_eq!(col.events_lost, 0);
        let contents = std::fs::read_to_string(&wal).unwrap();
        assert!(contents.contains("\"source\":\"auditd\""));
        assert!(contents.contains("\"timestamp_us\":123456"));
        let _ = std::fs::remove_file(&wal);
    }

    #[test]
    fn test_observability_buffer_flush_reorder() {
        let dir = std::env::temp_dir();
        let wal = dir.join(format!("sentinel_test_obs_{}.log", std::process::id()));
        let mut col = ObservabilityLaneCollector::new(wal.clone());
        // Insertar desordenado por timestamp
        for ts in [300, 100, 200] {
            col.emit_buffered(LaneEvent {
                lane: DataLane::Observability,
                source: "app".into(),
                priority: EventPriority::Medium,
                timestamp_us: ts,
                labels: HashMap::new(),
                data: format!("{{\"ts\":{}}}", ts),
                synthetic: false,
            });
        }
        // Forzar flush explícito (fin de run)
        col.flush();
        let contents = std::fs::read_to_string(&wal).unwrap();
        // El primer evento escrito debe ser el de ts=100 (reordenado)
        let first_ts = contents
            .lines()
            .next()
            .and_then(|l| l.find("\"ts\":100"))
            .is_some();
        assert!(first_ts, "buffer no fue reordenado por timestamp");
        let _ = std::fs::remove_file(&wal);
    }

    #[test]
    fn test_backpressure_drops_lowest_priority() {
        let dir = std::env::temp_dir();
        let wal = dir.join(format!("sentinel_test_bp_{}.log", std::process::id()));
        let mut col = ObservabilityLaneCollector::new(wal.clone());
        col.max_buffer_bytes = 20; // evento individual (~35 bytes) supera el buffer
        // Llenar con eventos MEDIUM (cada uno > max_buffer_bytes)
        for i in 0..5 {
            col.emit_buffered(LaneEvent {
                lane: DataLane::Observability,
                source: "app".into(),
                priority: EventPriority::Medium,
                timestamp_us: i,
                labels: HashMap::new(),
                data: "{\"pad\":\"xxxxxxxxxxxx\"}".into(),
                synthetic: false,
            });
        }
        // Cada evento supera max_buffer_bytes: tras flush sigue sin caber → drop
        assert!(col.events_dropped > 0, "backpressure no descartó nada");
        let _ = std::fs::remove_file(&wal);
    }
}
