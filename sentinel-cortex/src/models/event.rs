// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use crate::math::s60::S60;

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
    UnauthorizedAccess,
    PrivilegeEscalation,
    
    // Red
    LargeDataTransfer,
    UnusualTraffic,
    
    // Aplicación
    ErrorSpike,
    SlowResponse,
}

#[derive(Debug, Clone, Serialize)]
pub struct DetectedPattern {
    pub name: String,
    pub confidence: S60,  // Protocolo YATRA (S60)
    pub severity: Severity,
    pub events: Vec<Event>,
    pub recommended_action: String,
    pub playbook: String,  // Nombre del playbook N8N
}
