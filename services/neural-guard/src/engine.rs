use crate::models::{CorrelatedIncident, Event, Severity};
use std::collections::VecDeque;

pub struct DecisionEngine {
    event_buffer: VecDeque<Event>,
    time_window: chrono::Duration,
    ssh_bruteforce_threshold: usize,
    nginx_5xx_threshold: u64,
    redis_memory_threshold_bytes: u64,
    container_restart_threshold: i64,
}

impl DecisionEngine {
    pub fn new() -> Self {
        // Lee el umbral desde una variable de entorno, con 5 como valor por defecto.
        let threshold_str =
            std::env::var("SSH_BRUTEFORCE_THRESHOLD").unwrap_or_else(|_| "5".to_string());
        let threshold = threshold_str.parse::<usize>().unwrap_or(5);

        let nginx_threshold_str =
            std::env::var("NGINX_5XX_THRESHOLD").unwrap_or_else(|_| "10".to_string());
        let nginx_threshold = nginx_threshold_str.parse::<u64>().unwrap_or(10);

        let redis_threshold_str =
            std::env::var("REDIS_MEMORY_THRESHOLD_BYTES").unwrap_or_else(|_| "104857600".to_string()); // 100MB
        let redis_threshold = redis_threshold_str.parse::<u64>().unwrap_or(104_857_600);

        let restart_threshold_str =
            std::env::var("CONTAINER_RESTART_THRESHOLD").unwrap_or_else(|_| "3".to_string());
        let restart_threshold = restart_threshold_str.parse::<i64>().unwrap_or(3);

        Self {
            event_buffer: VecDeque::with_capacity(1000),
            time_window: chrono::Duration::try_minutes(5).unwrap_or_default(),
            ssh_bruteforce_threshold: threshold,
            nginx_5xx_threshold: nginx_threshold,
            redis_memory_threshold_bytes: redis_threshold,
            container_restart_threshold: restart_threshold,
        }
    }

    pub fn add_event(&mut self, event: Event) {
        self.event_buffer.push_back(event);
        self.prune_old_events();
    }

    fn prune_old_events(&mut self) {
        let now = chrono::Utc::now();
        while let Some(event) = self.event_buffer.front() {
            if now.signed_duration_since(event.timestamp) > self.time_window {
                self.event_buffer.pop_front();
            } else {
                break;
            }
        }
    }

    pub fn correlate(&self) -> Vec<CorrelatedIncident> {
        let mut incidents = Vec::new();

        // Patrón 1: Posible ataque de fuerza bruta o agotamiento de recursos
        // Como no tenemos logs de Auditd aún, simulamos con métricas
        let high_cpu = self.event_buffer.iter().any(|e| e.event_type == "high_cpu_usage");
        let high_net = self.event_buffer.iter().any(|e| e.event_type == "high_network_traffic"); // A implementar

        if high_cpu && high_net {
            incidents.push(CorrelatedIncident {
                name: "Potential Brute-Force or DDoS".to_string(),
                confidence: 0.75,
                severity: Severity::Critical,
                events: self.event_buffer.iter().cloned().collect(),
                recommended_action: "Activate network firewall rules and rate limiting.".to_string(),
                n8n_playbook: "ddos_mitigation".to_string(),
            });
        }

        // Patrón 2: Ataque de fuerza bruta de SSH
        // Señales: Múltiples logins fallidos y un aumento en el uso de CPU.
        let failed_logins_count = self.event_buffer.iter()
            .filter(|e| e.event_type == "failed_login")
            .count();

        let high_cpu_during_logins = self.event_buffer.iter().any(|e| e.event_type == "high_cpu_usage");

        // Umbral: más de 5 logins fallidos en la ventana de tiempo y CPU alto.
        if failed_logins_count > self.ssh_bruteforce_threshold && high_cpu_during_logins {
            // Recolectar solo los eventos relevantes para este incidente
            let relevant_events: Vec<Event> = self.event_buffer.iter()
                .filter(|e| e.event_type == "failed_login" || e.event_type == "high_cpu_usage")
                .cloned()
                .collect();

            incidents.push(CorrelatedIncident {
                name: "SSH Brute-Force Attack Detected".to_string(),
                confidence: 0.85,
                severity: Severity::Critical,
                events: relevant_events,
                recommended_action: "Temporarily ban the source IP addresses from the failed logins.".to_string(),
                n8n_playbook: "ssh_bruteforce_mitigation".to_string(),
            });
        }

        // Patrón 3: Pico de errores 5xx en Nginx
        // Señal: El número de errores 5xx supera el umbral en la ventana de tiempo.
        let nginx_5xx_events: Vec<_> = self.event_buffer.iter()
            .filter(|e| e.event_type == "nginx_5xx_spike")
            .collect();

        if let Some(last_event) = nginx_5xx_events.last() {
            if let Some(count) = last_event.metadata["count"].as_u64() {
                if count > self.nginx_5xx_threshold {
                    incidents.push(CorrelatedIncident {
                        name: "Nginx 5xx Error Spike".to_string(),
                        confidence: 0.90,
                        severity: Severity::High,
                        events: nginx_5xx_events.into_iter().cloned().collect(),
                        recommended_action: "Check backend service logs for application errors.".to_string(),
                        n8n_playbook: "backend_health_check".to_string(),
                    });
                }
            }
        }

        // Patrón 4: Alto uso de memoria en Redis
        // Señal: El uso de memoria de Redis supera el umbral.
        let redis_mem_events: Vec<_> = self.event_buffer.iter()
            .filter(|e| e.event_type == "redis_memory_usage")
            .collect();

        if let Some(last_event) = redis_mem_events.last() {
            if let Some(used_bytes) = last_event.metadata["used_bytes"].as_u64() {
                if used_bytes > self.redis_memory_threshold_bytes {
                    incidents.push(CorrelatedIncident {
                        name: "Redis High Memory Usage".to_string(),
                        confidence: 0.95,
                        severity: Severity::High,
                        events: redis_mem_events.into_iter().cloned().collect(),
                        recommended_action: "Investigate Redis keys. Consider eviction policy or scaling.".to_string(),
                        n8n_playbook: "redis_memory_check".to_string(),
                    });
                }
            }
        }

        // Patrón 5: Reinicios inesperados de contenedores
        // Señal: Un contenedor se reinicia más veces que el umbral.
        let restart_events: Vec<Event> = self.event_buffer.iter()
            .filter(|e| e.event_type == "container_restarted")
            .cloned()
            .collect();

        // Agrupar por servicio para detectar reinicios del mismo contenedor
        let mut service_restarts: std::collections::HashMap<String, i64> = std::collections::HashMap::new();
        for event in &restart_events {
            if let Some(service_name) = event.metadata["service"].as_str() {
                let restarts = event.metadata["restarts"].as_i64().unwrap_or(0);
                service_restarts.insert(service_name.to_string(), restarts);
            }
        }

        for (service, restarts) in service_restarts {
            if restarts > self.container_restart_threshold {
                let relevant_events: Vec<Event> = restart_events.iter().filter(|e| e.metadata["service"] == service).cloned().collect();
                incidents.push(CorrelatedIncident {
                    name: format!("Container Crash Loop: {}", service),
                    confidence: 0.98,
                    severity: Severity::Critical,
                    events: relevant_events,
                    recommended_action: format!("Investigate logs for container '{}'. It has restarted {} times.", service, restarts),
                    n8n_playbook: "container_crash_alert".to_string(),
                });
            }
        }

        incidents
    }
}