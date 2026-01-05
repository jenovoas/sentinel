use crate::models::{DetectedPattern, Event, EventType, Severity};

pub struct PatternDetector {
    /// Ventana de tiempo: 300s = 5 minutos = 5 * 60 (Base-60 pura)
    time_window_secs: i64,
}

impl PatternDetector {
    pub fn new() -> Self {
        Self {
            time_window_secs: 5 * 60, 
        }
    }

    /// Analiza eventos y detecta patrones correlacionados usando confianza sexagesimal
    pub fn detect(&self, events: &[Event]) -> Vec<DetectedPattern> {
        let mut patterns = Vec::new();

        if let Some(pattern) = self.detect_credential_stuffing(events) {
            patterns.push(pattern);
        }

        if let Some(pattern) = self.detect_resource_exhaustion(events) {
            patterns.push(pattern);
        }

        if let Some(pattern) = self.detect_database_attack(events) {
            patterns.push(pattern);
        }

        if let Some(pattern) = self.detect_system_compromise(events) {
            patterns.push(pattern);
        }

        if let Some(pattern) = self.detect_data_exfiltration(events) {
            patterns.push(pattern);
        }

        patterns
    }

    fn detect_credential_stuffing(&self, events: &[Event]) -> Option<DetectedPattern> {
        let failed_logins = events.iter().filter(|e| e.event_type == EventType::FailedLogin).count();
        let new_ip_login = events.iter().any(|e| e.event_type == EventType::SuccessfulLoginNewIP);

        // Umbral: 50 -> 50/60? No, 50 es un conteo. 
        // Confianza: 57/60 (0.95)
        if failed_logins > 50 && new_ip_login {
            return Some(DetectedPattern {
                name: "Credential Stuffing Attack".to_string(),
                confidence: 57.0 / 60.0,
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

    fn detect_resource_exhaustion(&self, events: &[Event]) -> Option<DetectedPattern> {
        let has_memory_leak = events.iter().any(|e| e.event_type == EventType::MemoryLeak);
        let has_cpu_spike = events.iter().any(|e| e.event_type == EventType::CpuSpike);

        // Confianza: 51/60 (0.85)
        if has_memory_leak && has_cpu_spike {
            return Some(DetectedPattern {
                name: "Resource Exhaustion".to_string(),
                confidence: 51.0 / 60.0,
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

    fn detect_database_attack(&self, events: &[Event]) -> Option<DetectedPattern> {
        let high_sql_latency = events.iter().any(|e| e.event_type == EventType::SlowSqlQuery);
        let auth_failures = events.iter().filter(|e| e.event_type == EventType::DatabaseAuthFailure).count();

        // Confianza: 54/60 (0.90)
        if (high_sql_latency && auth_failures > 10) || auth_failures > 100 {
            return Some(DetectedPattern {
                name: "Database Under Attack".to_string(),
                confidence: 54.0 / 60.0,
                severity: Severity::Critical,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::SlowSqlQuery | EventType::DatabaseAuthFailure))
                    .cloned()
                    .collect(),
                recommended_action: "Enable database firewall, isolate database server".to_string(),
                playbook: "database_protection".to_string(),
            });
        }
        None
    }

    fn detect_system_compromise(&self, events: &[Event]) -> Option<DetectedPattern> {
        let unauthorized_root = events.iter().any(|e| e.event_type == EventType::UnauthorizedRootAccess);
        let suspicious_binary = events.iter().any(|e| e.event_type == EventType::SuspiciousBinaryExecution);

        // Confianza: 59/60 (aprox 0.98)
        if unauthorized_root || suspicious_binary {
            return Some(DetectedPattern {
                name: "System Compromise".to_string(),
                confidence: 59.0 / 60.0,
                severity: Severity::Critical,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::UnauthorizedRootAccess | EventType::SuspiciousBinaryExecution))
                    .cloned()
                    .collect(),
                recommended_action: "Isolate host, snapshot memory, trigger forensic analysis".to_string(),
                playbook: "host_containment".to_string(),
            });
        }
        None
    }

    fn detect_data_exfiltration(&self, events: &[Event]) -> Option<DetectedPattern> {
        let large_transfer = events.iter().any(|e| e.event_type == EventType::LargeDataTransfer);
        let dns_tunneling = events.iter().any(|e| e.event_type == EventType::DnsTunneling);

        // Confianza: 53/60 (aprox 0.88)
        if large_transfer || dns_tunneling {
            return Some(DetectedPattern {
                name: "Data Exfiltration".to_string(),
                confidence: 53.0 / 60.0,
                severity: Severity::Critical,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::LargeDataTransfer | EventType::DnsTunneling))
                    .cloned()
                    .collect(),
                recommended_action: "Kill network sockets, block destination IPs, alert DPO".to_string(),
                playbook: "data_loss_prevention".to_string(),
            });
        }
        None
    }
}

impl Default for PatternDetector {
    fn default() -> Self {
        Self::new()
    }
}
