use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Evento normalizado de cualquier fuente
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub id: String,
    pub source: EventSource,
    pub timestamp: DateTime<Utc>,
    pub severity: Severity,
    pub event_type: EventType,
    pub metadata: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EventSource {
    Prometheus,
    PostgreSQL,
    Loki,
    Auditd,
    Docker,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
pub enum Severity {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum EventType {
    // Métricas
    CpuSpike,
    MemoryLeak,
    DiskFull,
    
    // Seguridad
    FailedLogin,
    SuccessfulLoginNewIP,
    SuspiciousCommand,
    
    // Red
    LargeDataTransfer,
    UnusualTraffic,
    
    // Aplicación
    ErrorSpike,
    SlowResponse,
}

/// Patrón de ataque detectado
#[derive(Debug, Clone, Serialize)]
pub struct DetectedPattern {
    pub name: String,
    pub confidence: f32,  // 0.0 - 1.0
    pub severity: Severity,
    pub events: Vec<Event>,
    pub recommended_action: String,
    pub playbook: String,  // Nombre del playbook N8N
}
