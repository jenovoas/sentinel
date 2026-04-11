use crate::models::{Event, EventType, DetectedPattern, Severity};
use crate::math::s60::S60;

pub struct PatternDetector {
    /// Ventana de tiempo para correlacionar eventos (5 minutos)
    #[allow(dead_code)]
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

        // Patrón 4: Suspicious Behavior
        if let Some(pattern) = self.detect_suspicious_behavior(events) {
            patterns.push(pattern);
        }

        // Patrón 5: Brute Force Attack
        if let Some(pattern) = self.detect_brute_force(events) {
            patterns.push(pattern);
        }

        // Patrón 6: Application Degradation
        if let Some(pattern) = self.detect_app_degradation(events) {
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
        
        if failed_logins > 50 && new_ip_login {
            return Some(DetectedPattern {
                name: "Credential Stuffing Attack".to_string(),
                confidence: S60::from_raw(205_200), // 0;51,36 S60 ≈ 0.95
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
                confidence: S60::from_raw(183_600), // 0;51,0 S60 ≈ 0.85
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
        let has_large_transfer = events.iter().any(|e| e.event_type == EventType::LargeDataTransfer);
        let has_unusual_traffic = events.iter().any(|e| e.event_type == EventType::UnusualTraffic);

        if has_large_transfer && has_unusual_traffic {
            return Some(DetectedPattern {
                name: "Data Exfiltration Attempt".to_string(),
                confidence: S60::from_raw(194_400), // 0.90 (194400 / 216000)
                severity: Severity::High,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::LargeDataTransfer | EventType::UnusualTraffic))
                    .cloned()
                    .collect(),
                recommended_action: "Isolate host, investigate network connections".to_string(),
                playbook: "intrusion_lockdown".to_string(),
            });
        }
        None
    }

    /// Patrón 4: Suspicious Behavior
    fn detect_suspicious_behavior(&self, events: &[Event]) -> Option<DetectedPattern> {
        let suspicious_events: Vec<Event> = events.iter()
            .filter(|e| e.event_type == EventType::SuspiciousCommand)
            .cloned()
            .collect();

        if !suspicious_events.is_empty() {
            return Some(DetectedPattern {
                name: "Suspicious Behavior Detected".to_string(),
                confidence: S60::from_raw(205_200), // 0.95 (205200 / 216000)
                severity: Severity::High,
                events: suspicious_events,
                recommended_action: "Audit user session, check process tree".to_string(),
                playbook: "intrusion_lockdown".to_string(),
            });
        }
        None
    }

    /// Patrón 5: Brute Force Attack
    fn detect_brute_force(&self, events: &[Event]) -> Option<DetectedPattern> {
        let failed_logins = events.iter()
            .filter(|e| e.event_type == EventType::FailedLogin)
            .count();

        if failed_logins > 100 {
            return Some(DetectedPattern {
                name: "Brute Force Attack".to_string(),
                confidence: S60::from_raw(211_680), // 0.98 (211680 / 216000)
                severity: Severity::Critical,
                events: events.iter()
                    .filter(|e| e.event_type == EventType::FailedLogin)
                    .cloned()
                    .collect(),
                recommended_action: "Block IP, enable MFA if not active".to_string(),
                playbook: "intrusion_lockdown".to_string(),
            });
        }
        None
    }

    /// Patrón 6: Application Degradation
    fn detect_app_degradation(&self, events: &[Event]) -> Option<DetectedPattern> {
        let has_error_spike = events.iter().any(|e| e.event_type == EventType::ErrorSpike);
        let has_slow_response = events.iter().any(|e| e.event_type == EventType::SlowResponse);

        if has_error_spike && has_slow_response {
            return Some(DetectedPattern {
                name: "Application Performance Degradation".to_string(),
                confidence: S60::from_raw(172_800), // 0.80 (172800 / 216000)
                severity: Severity::Medium,
                events: events.iter()
                    .filter(|e| matches!(e.event_type, EventType::ErrorSpike | EventType::SlowResponse))
                    .cloned()
                    .collect(),
                recommended_action: "Check application logs, verify upstream services".to_string(),
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::{EventSource, EventType, Severity};
    use chrono::Utc;

    fn mock_event(event_type: EventType) -> Event {
        Event {
            id: format!("test-{}", event_type as u32),
            source: EventSource::Auditd,
            timestamp: Utc::now(),
            severity: Severity::Medium,
            event_type,
            metadata: serde_json::json!({}),
        }
    }

    #[test]
    fn test_detect_data_exfiltration() {
        let detector = PatternDetector::new();
        let events = vec![
            mock_event(EventType::LargeDataTransfer),
            mock_event(EventType::UnusualTraffic),
        ];
        let patterns = detector.detect(&events);
        assert!(patterns.iter().any(|p| p.name == "Data Exfiltration Attempt"));
    }

    #[test]
    fn test_detect_suspicious_behavior() {
        let detector = PatternDetector::new();
        let events = vec![mock_event(EventType::SuspiciousCommand)];
        let patterns = detector.detect(&events);
        assert!(patterns.iter().any(|p| p.name == "Suspicious Behavior Detected"));
    }

    #[test]
    fn test_detect_brute_force() {
        let detector = PatternDetector::new();
        let mut events = Vec::new();
        for _ in 0..101 {
            events.push(mock_event(EventType::FailedLogin));
        }
        let patterns = detector.detect(&events);
        assert!(patterns.iter().any(|p| p.name == "Brute Force Attack"));
    }

    #[test]
    fn test_detect_app_degradation() {
        let detector = PatternDetector::new();
        let events = vec![
            mock_event(EventType::ErrorSpike),
            mock_event(EventType::SlowResponse),
        ];
        let patterns = detector.detect(&events);
        assert!(patterns.iter().any(|p| p.name == "Application Performance Degradation"));
    }

    #[test]
    fn test_no_false_positives() {
        let detector = PatternDetector::new();
        let events = vec![
            mock_event(EventType::CpuSpike), // Needs MemoryLeak for Resource Exhaustion
        ];
        let patterns = detector.detect(&events);
        assert!(patterns.is_empty());
    }
}
