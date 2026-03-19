use crate::models::{CorrelatedIncident, Event, Severity};
use crate::patterns::{
    ContainerCrashLoopPattern, NginxErrorSpikePattern, Pattern, PatternContext, RedisMemoryPattern,
    SshBruteForcePattern,
};
use std::collections::VecDeque;
use me60os_core::spa::SPA;
use me60os_core::physics::ResonantPhysics;

pub struct DecisionEngine {
    event_buffer: VecDeque<Event>,
    patterns: Vec<Box<dyn Pattern>>,
    time_window: chrono::Duration,

    // Configuration for patterns
    ssh_bruteforce_threshold: usize,
    nginx_5xx_threshold: u64,
    redis_memory_threshold_bytes: u64,
    container_restart_threshold: i64,
    enable_thermal_coupling: bool,

    // S60 Physics state
    baseline_load: SPA,
}

impl DecisionEngine {
    pub fn new() -> Self {
        dotenvy::dotenv().ok();
        
        let threshold_str = std::env::var("SSH_BRUTEFORCE_THRESHOLD").unwrap_or_else(|_| "5".to_string());
        let threshold = threshold_str.parse::<usize>().unwrap_or(5);

        let nginx_threshold_str = std::env::var("NGINX_5XX_THRESHOLD").unwrap_or_else(|_| "10".to_string());
        let nginx_threshold = nginx_threshold_str.parse::<u64>().unwrap_or(10);

        let redis_threshold_str = std::env::var("REDIS_MEMORY_THRESHOLD_BYTES").unwrap_or_else(|_| "104857600".to_string()); // 100MB
        let redis_threshold = redis_threshold_str.parse::<u64>().unwrap_or(104_857_600);

        let restart_threshold_str = std::env::var("CONTAINER_RESTART_THRESHOLD").unwrap_or_else(|_| "3".to_string());
        let restart_threshold = restart_threshold_str.parse::<i64>().unwrap_or(3);

        let enable_thermal = std::env::var("ENABLE_THERMAL_COUPLING").map(|v| v == "true").unwrap_or(false);

        Self {
            event_buffer: VecDeque::with_capacity(1000),
            patterns: vec![
                Box::new(SshBruteForcePattern),
                Box::new(NginxErrorSpikePattern),
                Box::new(RedisMemoryPattern),
                Box::new(ContainerCrashLoopPattern),
                // To add a new pattern, just add a new `Box::new(...)` here.
            ],
            time_window: chrono::Duration::try_minutes(5).unwrap_or_default(),
            ssh_bruteforce_threshold: threshold,
            nginx_5xx_threshold: nginx_threshold,
            redis_memory_threshold_bytes: redis_threshold,
            container_restart_threshold: restart_threshold,
            enable_thermal_coupling: enable_thermal,
            baseline_load: SPA::new(1000, 0, 0, 0, 0), // Carga estática base
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

    fn calculate_thermal_multiplier(&self) -> f64 {
        if !self.enable_thermal_coupling {
            return 1.0;
        }

        // 1. Buscar la lectura térmica más reciente
        let latest_temp = self.event_buffer.iter()
            .filter(|e| e.event_type == "cpu_thermal_reading")
            .last();

        let temp_c = match latest_temp {
            Some(e) => e.metadata["celsius"].as_f64().unwrap_or(40.0),
            None => 40.0, // Baseline normal
        };

        // 2. Mapear temperatura a estabilidad (0.0 a 1.0)
        // 40C -> 1.0 (Soberano), 90C -> 0.0 (Caos)
        let stability_raw = if temp_c <= 40.0 {
            1.0
        } else if temp_c >= 90.0 {
            0.0
        } else {
            (90.0 - temp_c) / 50.0
        };

        let stability = SPA::new(0, (stability_raw * 60.0) as i64, 0, 0, 0);
        let priority = SPA::one();

        // 3. Calcular Carga Efectiva (Inercia)
        let load_eff = ResonantPhysics::calculate_effective_load(self.baseline_load, priority, stability);
        
        // 4. Calcular Multiplicador
        // Load_eff es mínimo (~200) cuando es Estable, máximo (1000) cuando es Caos.
        // Queremos que el multiplicador sea 1.0 cuando es Estable (Mínimo).
        // Y que suba cuando hay caos.
        let min_load = ResonantPhysics::calculate_effective_load(
            self.baseline_load, 
            priority, 
            SPA::one()
        );

        let multiplier = load_eff.to_raw() as f64 / min_load.to_raw() as f64;
        
        if multiplier < 1.0 { 1.0 } else { multiplier }
    }

    pub fn correlate(&self) -> Vec<CorrelatedIncident> {
        let multiplier = self.calculate_thermal_multiplier();
        
        // Aplicar multiplicador a los umbrales
        let ssh_threshold = (self.ssh_bruteforce_threshold as f64 * multiplier) as usize;
        let nginx_threshold = (self.nginx_5xx_threshold as f64 * multiplier) as u64;
        let redis_threshold = (self.redis_memory_threshold_bytes as f64 * multiplier) as u64;
        let restart_threshold = (self.container_restart_threshold as f64 * multiplier) as i64;

        let mut incidents = Vec::new();

        // Patrón 1: Posible ataque de fuerza bruta o agotamiento de recursos
        // Como no tenemos logs de Auditd aún, simulamos con métricas
        let high_cpu = self.event_buffer.iter().any(|e| e.event_type == "high_cpu_usage");
        let high_net = self.event_buffer.iter().any(|e| e.event_type == "high_network_traffic"); // A implementar
        // Create a context for the patterns to use
        let context = PatternContext {
            event_buffer: &self.event_buffer,
            ssh_bruteforce_threshold: ssh_threshold,
            nginx_5xx_threshold: nginx_threshold,
            redis_memory_threshold_bytes: redis_threshold,
            container_restart_threshold: restart_threshold,
        };

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
        if failed_logins_count > ssh_threshold && high_cpu_during_logins {
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
                if count > nginx_threshold {
                    incidents.push(CorrelatedIncident {
                        name: "Nginx 5xx Error Spike".to_string(),
                        confidence: 0.90,
                        severity: Severity::High,
                        events: nginx_5xx_events.into_iter().cloned().collect(),
                        recommended_action: "Check backend service logs for application errors.".to_string(),
                        n8n_playbook: "backend_health_check".to_string(),
                    });
                }
        // Iterate over all registered patterns and check for incidents
        for pattern in &self.patterns {
            if let Some(incident) = pattern.check(&context) {
                incidents.push(incident);
            }
        }

        // Patrón 4: Alto uso de memoria en Redis
        // Señal: El uso de memoria de Redis supera el umbral.
        let redis_mem_events: Vec<_> = self.event_buffer.iter()
            .filter(|e| e.event_type == "redis_memory_usage")
            .collect();
        // Note: Pattern 1 (DDoS) was not fully implemented. It can be added
        // as a new struct implementing the `Pattern` trait when ready.

        if let Some(last_event) = redis_mem_events.last() {
            if let Some(used_bytes) = last_event.metadata["used_bytes"].as_u64() {
                if used_bytes > redis_threshold {
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
            if restarts > restart_threshold {
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