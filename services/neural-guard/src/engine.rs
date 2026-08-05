// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use crate::models::{CorrelatedIncident, Event};
use crate::patterns::{
    ContainerCrashLoopPattern, CrossNervioPattern, DdosPattern, NginxErrorSpikePattern,
    NervioAIntrusionPattern, NervioBIntegrityPattern, Pattern, PatternContext, TrafficDropPattern,
    RedisMemoryPattern, SshBruteForcePattern,
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
    traffic_drop_threshold: u64,
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

        let traffic_threshold_str = std::env::var("TRAFFIC_DROP_THRESHOLD_RPS").unwrap_or_else(|_| "100".to_string());
        let traffic_threshold = traffic_threshold_str.parse::<u64>().unwrap_or(100);

        let enable_thermal = std::env::var("ENABLE_THERMAL_COUPLING").map(|v| v == "true").unwrap_or(false);

        Self {
            event_buffer: VecDeque::with_capacity(1000),
            patterns: vec![
                Box::new(DdosPattern),
                Box::new(SshBruteForcePattern),
                Box::new(NginxErrorSpikePattern),
                Box::new(RedisMemoryPattern),
                Box::new(ContainerCrashLoopPattern),
                Box::new(TrafficDropPattern),
                // Dos Nervios: detectores independientes + correlación cruzada
                Box::new(NervioAIntrusionPattern),
                Box::new(NervioBIntegrityPattern),
                Box::new(CrossNervioPattern), // Va último: escala cuando ambos nervios confirman
            ],
            time_window: chrono::Duration::try_minutes(5).unwrap_or_default(),
            ssh_bruteforce_threshold: threshold,
            nginx_5xx_threshold: nginx_threshold,
            redis_memory_threshold_bytes: redis_threshold,
            container_restart_threshold: restart_threshold,
            traffic_drop_threshold: traffic_threshold,
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
        let traffic_threshold = self.traffic_drop_threshold; // El umbral de caída no debería escalar con la temperatura

        let mut incidents = Vec::new();

        // Create a context for the patterns to use
        let context = PatternContext {
            event_buffer: &self.event_buffer,
            ssh_bruteforce_threshold: ssh_threshold,
            nginx_5xx_threshold: nginx_threshold,
            redis_memory_threshold_bytes: redis_threshold,
            container_restart_threshold: restart_threshold,
            traffic_drop_threshold: traffic_threshold,
        };

        // Iterate over all registered patterns and check for incidents
        for pattern in &self.patterns {
            if let Some(incident) = pattern.check(&context) {
                incidents.push(incident);
            }
        }

        // Note: Pattern 1 (DDoS) was not fully implemented. It can be added
        // as a new struct implementing the `Pattern` trait when ready.

        incidents
    }
}