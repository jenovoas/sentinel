# 🧠 Sentinel Cortex - Claim 2: Decision Engine (Semanas 3-4)

## ¿Qué es el Decision Engine?

Es el **cerebro** de Sentinel Cortex que:
1. Recibe eventos de múltiples fuentes (Prometheus, Loki, PostgreSQL, etc.)
2. Los correlaciona para detectar patrones de ataque
3. Calcula un **confidence score** (0.0-1.0)
4. Decide qué playbook ejecutar en N8N

**Ejemplo simple**:
```
50 failed logins (Auditd) + 
Successful login from new IP (App logs) + 
Large data transfer (Network) 
= 95% confidence de "credential stuffing" 
→ Ejecutar playbook "intrusion_lockdown"
```

---

## 🎯 Objetivo de estas 2 semanas

Crear un sistema Rust que:
- ✅ Reciba eventos de diferentes fuentes
- ✅ Detecte 5 patrones de ataque básicos
- ✅ Calcule confidence scores
- ✅ Llame webhooks de N8N cuando detecte amenazas

**NO necesitas**: Honeypots, firewall manager, ni nada avanzado. Solo el cerebro básico.

---

## 📋 Plan Semana 3 (Días 1-7)

### Día 1: Setup del proyecto Rust

**Crear estructura**:
```bash
cd /home/jnovoas/sentinel
mkdir -p neural-guard
cd neural-guard
cargo init --name neural-guard

# Agregar dependencias
```

**Cargo.toml**:
```toml
[package]
name = "neural-guard"
version = "0.1.0"
edition = "2021"

[dependencies]
# Web server
axum = "0.7"
tokio = { version = "1", features = ["full"] }
tower = "0.4"

# Database
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio-native-tls"] }
redis = { version = "0.24", features = ["tokio-comp"] }

# HTTP client
reqwest = { version = "0.11", features = ["json"] }

# Serialization
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# Time
chrono = { version = "0.4", features = ["serde"] }

# Logging
tracing = "0.1"
tracing-subscriber = "0.3"

# Config
dotenvy = "0.15"
```

**Estructura de carpetas**:
```
neural-guard/
├── src/
│   ├── main.rs              # Entry point
│   ├── config.rs            # Configuración
│   ├── collectors/          # Recolectores de datos
│   │   ├── mod.rs
│   │   ├── prometheus.rs
│   │   └── postgres.rs
│   ├── models/              # Estructuras de datos
│   │   ├── mod.rs
│   │   └── event.rs
│   ├── engine/              # Motor de decisión
│   │   ├── mod.rs
│   │   ├── correlator.rs
│   │   └── patterns.rs
│   └── actions/             # Acciones (N8N webhooks)
│       ├── mod.rs
│       └── n8n_client.rs
├── Cargo.toml
└── .env
```

**Tiempo**: 2-3 horas

---

### Día 2-3: Modelos de datos

**src/models/event.rs**:
```rust
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

#[derive(Debug, Clone, Serialize, Deserialize)]
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
```

**Tiempo**: 3-4 horas

---

### Día 4-5: Collector básico (Prometheus)

**src/collectors/prometheus.rs**:
```rust
use reqwest::Client;
use crate::models::{Event, EventSource, EventType, Severity};
use chrono::Utc;

pub struct PrometheusCollector {
    client: Client,
    base_url: String,
}

impl PrometheusCollector {
    pub fn new(base_url: String) -> Self {
        Self {
            client: Client::new(),
            base_url,
        }
    }
    
    /// Consulta Prometheus y devuelve eventos
    pub async fn collect(&self) -> Result<Vec<Event>, Box<dyn std::error::Error>> {
        let mut events = Vec::new();
        
        // Query 1: CPU alto
        let cpu_query = "rate(node_cpu_seconds_total[5m])";
        let cpu_result = self.query(cpu_query).await?;
        
        if let Some(value) = cpu_result.as_f64() {
            if value > 0.8 {  // 80% CPU
                events.push(Event {
                    id: uuid::Uuid::new_v4().to_string(),
                    source: EventSource::Prometheus,
                    timestamp: Utc::now(),
                    severity: Severity::High,
                    event_type: EventType::CpuSpike,
                    metadata: serde_json::json!({
                        "cpu_usage": value,
                        "threshold": 0.8,
                    }),
                });
            }
        }
        
        // Query 2: Memoria
        let mem_query = "node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes";
        let mem_result = self.query(mem_query).await?;
        
        if let Some(value) = mem_result.as_f64() {
            if value < 0.1 {  // Menos de 10% disponible
                events.push(Event {
                    id: uuid::Uuid::new_v4().to_string(),
                    source: EventSource::Prometheus,
                    timestamp: Utc::now(),
                    severity: Severity::Critical,
                    event_type: EventType::MemoryLeak,
                    metadata: serde_json::json!({
                        "available_memory_pct": value,
                        "threshold": 0.1,
                    }),
                });
            }
        }
        
        Ok(events)
    }
    
    async fn query(&self, query: &str) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        let url = format!("{}/api/v1/query?query={}", self.base_url, query);
        let response = self.client.get(&url).send().await?;
        let json: serde_json::Value = response.json().await?;
        
        // Extraer primer valor del resultado
        Ok(json["data"]["result"][0]["value"][1].clone())
    }
}
```

**Tiempo**: 4-5 horas

---

### Día 6-7: Pattern Detector (5 patrones básicos)

**src/engine/patterns.rs**:
```rust
use crate::models::{Event, EventType, DetectedPattern, Severity};
use std::collections::HashMap;

pub struct PatternDetector {
    // Ventana de tiempo para correlacionar eventos (5 minutos)
    time_window_secs: i64,
}

impl PatternDetector {
    pub fn new() -> Self {
        Self {
            time_window_secs: 300,  // 5 minutos
        }
    }
    
    /// Analiza eventos y detecta patrones
    pub fn detect(&self, events: &[Event]) -> Vec<DetectedPattern> {
        let mut patterns = Vec::new();
        
        // Patrón 1: Credential Stuffing
        if let Some(pattern) = self.detect_credential_stuffing(events) {
            patterns.push(pattern);
        }
        
        // Patrón 2: Memory Leak + CPU Spike
        if let Some(pattern) = self.detect_resource_exhaustion(events) {
            patterns.push(pattern);
        }
        
        // Patrón 3: Data Exfiltration
        if let Some(pattern) = self.detect_data_exfiltration(events) {
            patterns.push(pattern);
        }
        
        // Patrón 4: DDoS
        if let Some(pattern) = self.detect_ddos(events) {
            patterns.push(pattern);
        }
        
        // Patrón 5: Disk Full
        if let Some(pattern) = self.detect_disk_full(events) {
            patterns.push(pattern);
        }
        
        patterns
    }
    
    /// Patrón 1: Credential Stuffing
    /// Señales: Muchos failed logins + 1 successful login desde nueva IP
    fn detect_credential_stuffing(&self, events: &[Event]) -> Option<DetectedPattern> {
        let failed_logins = events.iter()
            .filter(|e| e.event_type == EventType::FailedLogin)
            .count();
        
        let new_ip_login = events.iter()
            .any(|e| e.event_type == EventType::SuccessfulLoginNewIP);
        
        if failed_logins > 50 && new_ip_login {
            return Some(DetectedPattern {
                name: "Credential Stuffing Attack".to_string(),
                confidence: 0.95,
                severity: Severity::Critical,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::FailedLogin | EventType::SuccessfulLoginNewIP))
                    .cloned()
                    .collect(),
                recommended_action: "Block IP, lock account, revoke sessions".to_string(),
                playbook: "intrusion_lockdown".to_string(),
            });
        }
        
        None
    }
    
    /// Patrón 2: Resource Exhaustion (Memory Leak + CPU Spike)
    fn detect_resource_exhaustion(&self, events: &[Event]) -> Option<DetectedPattern> {
        let has_memory_leak = events.iter()
            .any(|e| e.event_type == EventType::MemoryLeak);
        
        let has_cpu_spike = events.iter()
            .any(|e| e.event_type == EventType::CpuSpike);
        
        if has_memory_leak && has_cpu_spike {
            return Some(DetectedPattern {
                name: "Resource Exhaustion".to_string(),
                confidence: 0.85,
                severity: Severity::High,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::MemoryLeak | EventType::CpuSpike))
                    .cloned()
                    .collect(),
                recommended_action: "Restart service, scale resources".to_string(),
                playbook: "auto_remediation".to_string(),
            });
        }
        
        None
    }
    
    /// Patrón 3: Data Exfiltration
    fn detect_data_exfiltration(&self, events: &[Event]) -> Option<DetectedPattern> {
        let large_transfer = events.iter()
            .any(|e| e.event_type == EventType::LargeDataTransfer);
        
        let new_ip_login = events.iter()
            .any(|e| e.event_type == EventType::SuccessfulLoginNewIP);
        
        if large_transfer && new_ip_login {
            return Some(DetectedPattern {
                name: "Data Exfiltration Attempt".to_string(),
                confidence: 0.88,
                severity: Severity::Critical,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::LargeDataTransfer | EventType::SuccessfulLoginNewIP))
                    .cloned()
                    .collect(),
                recommended_action: "Block IP, lock account, audit data access".to_string(),
                playbook: "intrusion_lockdown".to_string(),
            });
        }
        
        None
    }
    
    /// Patrón 4: DDoS
    fn detect_ddos(&self, events: &[Event]) -> Option<DetectedPattern> {
        let error_spikes = events.iter()
            .filter(|e| e.event_type == EventType::ErrorSpike)
            .count();
        
        if error_spikes > 100 {
            return Some(DetectedPattern {
                name: "DDoS Attack".to_string(),
                confidence: 0.80,
                severity: Severity::Critical,
                events: events.iter()
                    .filter(|e| e.event_type == EventType::ErrorSpike)
                    .cloned()
                    .collect(),
                recommended_action: "Enable rate limiting, block suspicious IPs".to_string(),
                playbook: "ddos_mitigation".to_string(),
            });
        }
        
        None
    }
    
    /// Patrón 5: Disk Full
    fn detect_disk_full(&self, events: &[Event]) -> Option<DetectedPattern> {
        let disk_full = events.iter()
            .any(|e| e.event_type == EventType::DiskFull);
        
        if disk_full {
            return Some(DetectedPattern {
                name: "Disk Space Critical".to_string(),
                confidence: 0.99,
                severity: Severity::High,
                events: events.iter()
                    .filter(|e| e.event_type == EventType::DiskFull)
                    .cloned()
                    .collect(),
                recommended_action: "Clean logs, expand disk, archive old data".to_string(),
                playbook: "disk_cleanup".to_string(),
            });
        }
        
        None
    }
}
```

**Tiempo**: 5-6 horas

---

## 📋 Plan Semana 4 (Días 8-14)

### Día 8-9: N8N Client (llamar webhooks)

**src/actions/n8n_client.rs**:
```rust
use reqwest::Client;
use crate::models::DetectedPattern;

pub struct N8NClient {
    client: Client,
    base_url: String,
}

impl N8NClient {
    pub fn new(base_url: String) -> Self {
        Self {
            client: Client::new(),
            base_url,
        }
    }
    
    /// Ejecuta un playbook en N8N
    pub async fn trigger_playbook(
        &self,
        pattern: &DetectedPattern
    ) -> Result<(), Box<dyn std::error::Error>> {
        let webhook_url = format!("{}/webhook/{}", self.base_url, pattern.playbook);
        
        let payload = serde_json::json!({
            "pattern_name": pattern.name,
            "confidence": pattern.confidence,
            "severity": pattern.severity,
            "event_count": pattern.events.len(),
            "recommended_action": pattern.recommended_action,
            "timestamp": chrono::Utc::now().to_rfc3339(),
        });
        
        let response = self.client
            .post(&webhook_url)
            .json(&payload)
            .send()
            .await?;
        
        if response.status().is_success() {
            tracing::info!("✅ Playbook '{}' triggered successfully", pattern.playbook);
        } else {
            tracing::error!("❌ Failed to trigger playbook '{}': {}", pattern.playbook, response.status());
        }
        
        Ok(())
    }
}
```



---

### Día 10-11: Main loop (orquestación)

**src/main.rs**:
```rust
mod config;
mod models;
mod collectors;
mod engine;
mod actions;

use collectors::prometheus::PrometheusCollector;
use engine::patterns::PatternDetector;
use actions::n8n_client::N8NClient;
use std::time::Duration;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup logging
    tracing_subscriber::fmt::init();
    
    // Load config
    dotenvy::dotenv().ok();
    let prometheus_url = std::env::var("PROMETHEUS_URL")?;
    let n8n_url = std::env::var("N8N_URL")?;
    
    // Initialize components
    let prometheus = PrometheusCollector::new(prometheus_url);
    let detector = PatternDetector::new();
    let n8n = N8NClient::new(n8n_url);
    
    tracing::info!("🧠 Sentinel Cortex Decision Engine started");
    
    // Main loop: collect → detect → act
    loop {
        tracing::debug!("📊 Collecting events...");
        
        // Collect events from Prometheus
        let events = prometheus.collect().await?;
        tracing::info!("Collected {} events", events.len());
        
        // Detect patterns
        let patterns = detector.detect(&events);
        tracing::info!("Detected {} patterns", patterns.len());
        
        // Trigger playbooks for detected patterns
        for pattern in patterns {
            tracing::warn!(
                "🚨 Pattern detected: {} (confidence: {:.2})",
                pattern.name,
                pattern.confidence
            );
            
            // Only trigger if confidence > 0.7
            if pattern.confidence > 0.7 {
                n8n.trigger_playbook(&pattern).await?;
            }
        }
        
        // Wait 30 seconds before next iteration
        tokio::time::sleep(Duration::from_secs(30)).await;
    }
}
```

**Tiempo**: 3-4 horas

---

### Día 12-13: Testing

**tests/integration_test.rs**:
```rust
#[tokio::test]
async fn test_credential_stuffing_detection() {
    let detector = PatternDetector::new();
    
    // Simular 60 failed logins + 1 successful login desde nueva IP
    let mut events = vec![];
    
    for _ in 0..60 {
        events.push(Event {
            id: uuid::Uuid::new_v4().to_string(),
            source: EventSource::Auditd,
            timestamp: Utc::now(),
            severity: Severity::Medium,
            event_type: EventType::FailedLogin,
            metadata: serde_json::json!({}),
        });
    }
    
    events.push(Event {
        id: uuid::Uuid::new_v4().to_string(),
        source: EventSource::PostgreSQL,
        timestamp: Utc::now(),
        severity: Severity::High,
        event_type: EventType::SuccessfulLoginNewIP,
        metadata: serde_json::json!({ "ip": "1.2.3.4" }),
    });
    
    let patterns = detector.detect(&events);
    
    assert_eq!(patterns.len(), 1);
    assert_eq!(patterns[0].name, "Credential Stuffing Attack");
    assert!(patterns[0].confidence > 0.9);
}
```

**Tiempo**: 4-5 horas

---

### Día 14: Deployment

**docker-compose.yml** (agregar servicio):
```yaml
neural-guard:
  build:
    context: ./neural-guard
    dockerfile: Dockerfile
  container_name: sentinel-neural-guard
  environment:
    - PROMETHEUS_URL=http://prometheus:9090
    - N8N_URL=http://n8n-security:5678
    - RUST_LOG=info
  depends_on:
    - prometheus
    - n8n-security
  networks:
    - sentinel_network
  restart: unless-stopped
```

**Dockerfile**:
```dockerfile
FROM rust:1.75 as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/neural-guard /usr/local/bin/
CMD ["neural-guard"]
```

---

## 🎯 Resultado Final

Al terminar estas 2 semanas tendrás:

✅ **Decision Engine funcional** que:
- Recolecta eventos de Prometheus cada 30 segundos
- Detecta 5 patrones de ataque
- Calcula confidence scores
- Llama webhooks de N8N automáticamente

✅ **Claim 2 listo para patente** con:
- Código implementado y testeado
- Documentación técnica
- Ejemplos de uso

✅ **Demo funcionando** para mostrar a inversores

---

