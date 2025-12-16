use crate::models::{Event, EventType, DetectedPattern, Severity};

pub struct PatternDetector {
    /// Ventana de tiempo para correlacionar eventos (5 minutos)
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
        
        // TODO: Agregar más patrones
        
        patterns
    }
    
    /// Patrón 1: Credential Stuffing
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
    
    /// Patrón 2: Resource Exhaustion
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
}

impl Default for PatternDetector {
    fn default() -> Self {
        Self::new()
    }
}
