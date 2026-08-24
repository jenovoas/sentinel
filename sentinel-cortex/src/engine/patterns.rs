// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use crate::models::{Event, EventType, DetectedPattern, Severity};
use crate::math::s60::S60;

pub struct PatternDetector {
    /// Ventana de tiempo para correlacionar eventos (5 minutos)
    #[allow(dead_code)]
    time_window_secs: i64,
}

#[allow(dead_code)]
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
        
        // Patrón 3: DDoS Attack
        if let Some(pattern) = self.detect_ddos(events) {
            patterns.push(pattern);
        }

        // Patrón 4: Ransomware / Unencrypted IO
        if let Some(pattern) = self.detect_ransomware(events) {
            patterns.push(pattern);
        }

        // Patrón 5: Privilege Escalation
        if let Some(pattern) = self.detect_privilege_escalation(events) {
            patterns.push(pattern);
        }

        patterns
    }
    
    /// Patrón 1: Credential Stuffing
    fn detect_credential_stuffing(&self, events: &[Event]) -> Option<DetectedPattern> {
        let failed_logins = events.iter()
            .filter(|e| e.event_type == EventType::FailedLogin)
            .count();
        
        let new_ip_login = events.iter()
            .any(|e| e.event_type == EventType::SuccessfulLoginNewIP);
        
        if failed_logins > 50 || new_ip_login {
            return Some(DetectedPattern {
                name: "Credential Stuffing Attack".to_string(),
                confidence: S60::from_raw(12_312_000), // 0.95
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
    
    /// Patrón 2: Resource Exhaustion / DDoS
    fn detect_resource_exhaustion(&self, events: &[Event]) -> Option<DetectedPattern> {
        let has_memory_leak = events.iter()
            .any(|e| e.event_type == EventType::MemoryLeak);
        
        let has_cpu_spike = events.iter()
            .any(|e| e.event_type == EventType::CpuSpike);
        
        if has_memory_leak || has_cpu_spike {
            return Some(DetectedPattern {
                name: "Resource Exhaustion".to_string(),
                confidence: S60::from_raw(11_016_000), // 0.85
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

    /// Patrón 3: DDoS Attack
    fn detect_ddos(&self, events: &[Event]) -> Option<DetectedPattern> {
        let network_spikes = events.iter().filter(|e| e.event_type == EventType::CpuSpike).count();
        if network_spikes > 100 {
            return Some(DetectedPattern {
                name: "DDoS Attack".to_string(),
                confidence: S60::from_raw(11_664_000), // 0.90
                severity: Severity::Critical,
                events: events.to_vec(),
                recommended_action: "Engage XDP rate limiter, notify NOC".to_string(),
                playbook: "ddos_mitigation".to_string(),
            });
        }
        None
    }

    /// Patrón 4: Ransomware
    fn detect_ransomware(&self, events: &[Event]) -> Option<DetectedPattern> {
        let unauth_io = events.iter().any(|e| e.event_type == EventType::UnauthorizedAccess);
        if unauth_io {
            return Some(DetectedPattern {
                name: "Ransomware Suspect".to_string(),
                confidence: S60::from_raw(12_312_000), // 0.95
                severity: Severity::Critical,
                events: events.to_vec(),
                recommended_action: "Isolate process, freeze BPF maps".to_string(),
                playbook: "ransomware_containment".to_string(),
            });
        }
        None
    }

    /// Patrón 5: Privilege Escalation
    fn detect_privilege_escalation(&self, events: &[Event]) -> Option<DetectedPattern> {
        let priv_esc = events.iter().any(|e| e.event_type == EventType::PrivilegeEscalation);
        if priv_esc {
            return Some(DetectedPattern {
                name: "Privilege Escalation Attempt".to_string(),
                confidence: S60::from_raw(11_664_000), // 0.90
                severity: Severity::Critical,
                events: events.to_vec(),
                recommended_action: "Revoke process token, trigger alert".to_string(),
                playbook: "privilege_isolation".to_string(),
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::{Event, EventSource, EventType, Severity};
    use chrono::Utc;

    fn make_event(et: EventType) -> Event {
        Event {
            id: format!("{}", Utc::now().timestamp_nanos_opt().unwrap_or(0)),
            source: EventSource::Prometheus,
            timestamp: Utc::now(),
            severity: Severity::Low,
            event_type: et,
            metadata: serde_json::Value::Null,
        }
    }

    #[test]
    fn test_credential_stuffing_detected() {
        let detector = PatternDetector::new();
        let events: Vec<Event> = (0..60).map(|_| make_event(EventType::FailedLogin)).collect();
        let patterns = detector.detect(&events);
        assert!(patterns.iter().any(|p| p.name.contains("Credential Stuffing")));
    }

    #[test]
    fn test_credential_stuffing_not_detected() {
        let detector = PatternDetector::new();
        let events = vec![make_event(EventType::FailedLogin)];
        let patterns = detector.detect(&events);
        assert!(!patterns.iter().any(|p| p.name.contains("Credential Stuffing")));
    }

    #[test]
    fn test_resource_exhaustion_not_detected_via_main_detect() {
        let detector = PatternDetector::new();
        let events = vec![make_event(EventType::CpuSpike)];
        let patterns = detector.detect(&events);
        // detect() calls detect_ddos (not detect_resource_exhaustion directly)
        // -> 1 CpuSpike is < 100 threshold -> no pattern
        assert!(patterns.is_empty());
    }
}
