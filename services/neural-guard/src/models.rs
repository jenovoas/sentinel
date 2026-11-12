// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use chrono::{DateTime, Utc};
use me60os_core::spa::SPA;
use serde::{ser::SerializeStruct, Deserialize, Serialize, Serializer};
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

#[derive(Debug, Clone)]
pub struct CorrelatedIncident {
    pub name: String,
    pub confidence_s60: SPA,
    pub severity: Severity,
    pub events: Vec<Event>,
    pub recommended_action: String,
    pub n8n_playbook: String,
}

impl Serialize for CorrelatedIncident {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut incident = serializer.serialize_struct("CorrelatedIncident", 6)?;
        incident.serialize_field("name", &self.name)?;
        incident.serialize_field("confidence_s60_raw", &self.confidence_s60.to_raw())?;
        incident.serialize_field("severity", &self.severity)?;
        incident.serialize_field("events", &self.events)?;
        incident.serialize_field("recommended_action", &self.recommended_action)?;
        incident.serialize_field("n8n_playbook", &self.n8n_playbook)?;
        incident.end()
    }
}
