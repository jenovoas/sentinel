// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EventSource {
    NervioAIntrusion, // Syscalls, memoria, red (Guardian Alpha)
    NervioBIntegrity, // Backups, config, certs (Guardian Beta)
    NervioCThermal,   // Temperatura y entropía (Octomecánica)
    Prometheus,       // Métricas generales
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Severity {
    Info,
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    #[serde(default = "Uuid::new_v4")]
    pub id: Uuid,
    pub source: EventSource,
    #[serde(default = "Utc::now")]
    pub timestamp: DateTime<Utc>,
    pub severity: Severity,
    pub event_type: String, // e.g., "syscall_execve", "backup_checksum_failed"
    pub metadata: serde_json::Value,
}

#[derive(Debug, Clone, Serialize)]
pub struct CorrelatedIncident {
    pub name: String,
    pub confidence: f32, // 0.0 - 1.0
    pub severity: Severity,
    pub events: Vec<Event>,
    pub recommended_action: String,
    pub n8n_playbook: String,
}
