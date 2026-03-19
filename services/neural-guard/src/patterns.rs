use crate::models::{CorrelatedIncident, Event, Severity};
use std::collections::{HashMap, VecDeque};

/// The context required for a pattern to make a decision.
/// It provides read-only access to the event buffer and configuration thresholds.
pub struct PatternContext<'a> {
    pub event_buffer: &'a VecDeque<Event>,
    pub ssh_bruteforce_threshold: usize,
    pub nginx_5xx_threshold: u64,
    pub redis_memory_threshold_bytes: u64,
    pub container_restart_threshold: i64,
}

/// A trait for any correlation pattern. Each pattern is a self-contained
/// unit of logic that checks for a specific type of incident.
pub trait Pattern: Send + Sync {
    /// Checks the event buffer against the pattern's logic.
    /// Returns a `CorrelatedIncident` if the pattern matches.
    fn check(&self, context: &PatternContext) -> Option<CorrelatedIncident>;
}

// --- Pattern Implementations ---

/// **Pattern 2: SSH Brute-Force Attack**
/// Detects multiple failed logins correlated with high CPU usage.
pub struct SshBruteForcePattern;
impl Pattern for SshBruteForcePattern {
    fn check(&self, context: &PatternContext) -> Option<CorrelatedIncident> {
        let failed_logins_count = context
            .event_buffer
            .iter()
            .filter(|e| e.event_type == "failed_login")
            .count();

        let high_cpu_during_logins = context
            .event_buffer
            .iter()
            .any(|e| e.event_type == "high_cpu_usage");

        if failed_logins_count > context.ssh_bruteforce_threshold && high_cpu_during_logins {
            let relevant_events: Vec<Event> = context
                .event_buffer
                .iter()
                .filter(|e| e.event_type == "failed_login" || e.event_type == "high_cpu_usage")
                .cloned()
                .collect();

            return Some(CorrelatedIncident {
                name: "SSH Brute-Force Attack Detected".to_string(),
                confidence: 0.85,
                severity: Severity::Critical,
                events: relevant_events,
                recommended_action:
                    "Temporarily ban the source IP addresses from the failed logins.".to_string(),
                n8n_playbook: "ssh_bruteforce_mitigation".to_string(),
            });
        }
        None
    }
}

/// **Pattern 3: Nginx 5xx Error Spike**
/// Detects when the number of Nginx 5xx errors exceeds a threshold.
pub struct NginxErrorSpikePattern;
impl Pattern for NginxErrorSpikePattern {
    fn check(&self, context: &PatternContext) -> Option<CorrelatedIncident> {
        let nginx_5xx_events: Vec<_> = context
            .event_buffer
            .iter()
            .filter(|e| e.event_type == "nginx_5xx_spike")
            .collect();

        if let Some(last_event) = nginx_5xx_events.last() {
            if let Some(count) = last_event.metadata["count"].as_u64() {
                if count > context.nginx_5xx_threshold {
                    return Some(CorrelatedIncident {
                        name: "Nginx 5xx Error Spike".to_string(),
                        confidence: 0.90,
                        severity: Severity::High,
                        events: nginx_5xx_events.into_iter().cloned().collect(),
                        recommended_action: "Check backend service logs for application errors."
                            .to_string(),
                        n8n_playbook: "backend_health_check".to_string(),
                    });
                }
            }
        }
        None
    }
}

/// **Pattern 4: High Redis Memory Usage**
/// Detects when Redis memory usage surpasses a defined limit.
pub struct RedisMemoryPattern;
impl Pattern for RedisMemoryPattern {
    fn check(&self, context: &PatternContext) -> Option<CorrelatedIncident> {
        let redis_mem_events: Vec<_> = context
            .event_buffer
            .iter()
            .filter(|e| e.event_type == "redis_memory_usage")
            .collect();

        if let Some(last_event) = redis_mem_events.last() {
            if let Some(used_bytes) = last_event.metadata["used_bytes"].as_u64() {
                if used_bytes > context.redis_memory_threshold_bytes {
                    return Some(CorrelatedIncident {
                        name: "Redis High Memory Usage".to_string(),
                        confidence: 0.95,
                        severity: Severity::High,
                        events: redis_mem_events.into_iter().cloned().collect(),
                        recommended_action:
                            "Investigate Redis keys. Consider eviction policy or scaling."
                                .to_string(),
                        n8n_playbook: "redis_memory_check".to_string(),
                    });
                }
            }
        }
        None
    }
}

/// **Pattern 5: Container Crash Loop**
/// Detects when a container restarts more times than the allowed threshold.
pub struct ContainerCrashLoopPattern;
impl Pattern for ContainerCrashLoopPattern {
    fn check(&self, context: &PatternContext) -> Option<CorrelatedIncident> {
        let mut service_restarts: HashMap<String, i64> = HashMap::new();
        context.event_buffer.iter()
            .filter(|e| e.event_type == "container_restarted")
            .for_each(|event| {
                if let Some(service_name) = event.metadata["service"].as_str() {
                    let restarts = event.metadata["restarts"].as_i64().unwrap_or(0);
                    service_restarts.insert(service_name.to_string(), restarts);
                }
            });

        for (service, restarts) in service_restarts {
            if restarts > context.container_restart_threshold {
                let relevant_events: Vec<Event> = context.event_buffer.iter().filter(|e| e.metadata["service"] == service).cloned().collect();
                return Some(CorrelatedIncident {
                    name: format!("Container Crash Loop: {}", service),
                    confidence: 0.98,
                    severity: Severity::Critical,
                    events: relevant_events,
                    recommended_action: format!("Investigate logs for container '{}'. It has restarted {} times.", service, restarts),
                    n8n_playbook: "container_crash_alert".to_string(),
                });
            }
        }
        None
    }
}
