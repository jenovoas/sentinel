// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
use crate::models::{CorrelatedIncident, Event};
use crate::patterns::{
    ContainerCrashLoopPattern, CrossNervioPattern, DdosPattern, NervioAIntrusionPattern,
    NervioBIntegrityPattern, NginxErrorSpikePattern, Pattern, PatternContext, RedisMemoryPattern,
    SshBruteForcePattern, TrafficDropPattern,
};
use me60os_core::physics::ResonantPhysics;
use me60os_core::spa::SPA;
use std::collections::VecDeque;

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

        let threshold_str =
            std::env::var("SSH_BRUTEFORCE_THRESHOLD").unwrap_or_else(|_| "5".to_string());
        let threshold = threshold_str.parse::<usize>().unwrap_or(5);

        let nginx_threshold_str =
            std::env::var("NGINX_5XX_THRESHOLD").unwrap_or_else(|_| "10".to_string());
        let nginx_threshold = nginx_threshold_str.parse::<u64>().unwrap_or(10);

        let redis_threshold_str = std::env::var("REDIS_MEMORY_THRESHOLD_BYTES")
            .unwrap_or_else(|_| "104857600".to_string()); // 100MB
        let redis_threshold = redis_threshold_str.parse::<u64>().unwrap_or(104_857_600);

        let restart_threshold_str =
            std::env::var("CONTAINER_RESTART_THRESHOLD").unwrap_or_else(|_| "3".to_string());
        let restart_threshold = restart_threshold_str.parse::<i64>().unwrap_or(3);

        let traffic_threshold_str =
            std::env::var("TRAFFIC_DROP_THRESHOLD_RPS").unwrap_or_else(|_| "100".to_string());
        let traffic_threshold = traffic_threshold_str.parse::<u64>().unwrap_or(100);

        let enable_thermal = std::env::var("ENABLE_THERMAL_COUPLING")
            .map(|v| v == "true")
            .unwrap_or(false);

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

    fn temperature_celsius(value: &serde_json::Value) -> i64 {
        let serialized = value
            .as_i64()
            .map(|number| number.to_string())
            .or_else(|| value.as_str().map(str::to_owned))
            .or_else(|| value.is_number().then(|| value.to_string()));

        serialized
            .and_then(|number| number.split(['.', 'e', 'E']).next()?.parse::<i64>().ok())
            .unwrap_or(40)
    }

    fn scale_threshold(value: u64, multiplier: SPA) -> u64 {
        let scale = SPA::SCALE_0 as u128;
        let multiplier_raw = multiplier.to_raw().max(SPA::SCALE_0) as u128;
        let scaled = u128::from(value)
            .checked_mul(multiplier_raw)
            .unwrap_or(u128::MAX)
            / scale;

        scaled.min(u128::from(u64::MAX)) as u64
    }

    fn calculate_thermal_multiplier(&self) -> SPA {
        if !self.enable_thermal_coupling {
            return SPA::one();
        }

        let temp_c = self
            .event_buffer
            .iter()
            .rfind(|event| event.event_type == "cpu_thermal_reading")
            .map(|event| Self::temperature_celsius(&event.metadata["celsius"]))
            .unwrap_or(40)
            .clamp(40, 90);

        let scale = SPA::SCALE_0 as i128;
        let stability_raw = if temp_c <= 40 {
            scale
        } else if temp_c >= 90 {
            0
        } else {
            i128::from(90 - temp_c) * scale / 50
        };
        let stability = SPA::from_raw(stability_raw as i64);
        let priority = SPA::one();

        let load_eff =
            ResonantPhysics::calculate_effective_load(self.baseline_load, priority, stability);
        let min_load =
            ResonantPhysics::calculate_effective_load(self.baseline_load, priority, SPA::one());
        let denominator = min_load.to_raw();

        if denominator <= 0 {
            return SPA::one();
        }

        let multiplier_raw =
            (i128::from(load_eff.to_raw()) * scale / i128::from(denominator)).max(scale);
        SPA::from_raw(multiplier_raw.min(i128::from(i64::MAX)) as i64)
    }

    pub fn correlate(&self) -> Vec<CorrelatedIncident> {
        let multiplier = self.calculate_thermal_multiplier();

        // Aplicar multiplicadores en escala SPA, sin conversiones flotantes.
        let ssh_threshold =
            Self::scale_threshold(self.ssh_bruteforce_threshold as u64, multiplier) as usize;
        let nginx_threshold = Self::scale_threshold(self.nginx_5xx_threshold, multiplier);
        let redis_threshold =
            Self::scale_threshold(self.redis_memory_threshold_bytes, multiplier);
        let restart_threshold = Self::scale_threshold(
            self.container_restart_threshold.max(0) as u64,
            multiplier,
        )
        .min(i64::MAX as u64) as i64;
        let traffic_threshold = self.traffic_drop_threshold;

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

        // Cada patrón recibe umbrales ya normalizados en escala entera.

        incidents
    }
}

#[cfg(test)]
mod tests {
    use super::DecisionEngine;
    use crate::models::{Event, EventSource, Severity};
    use chrono::Utc;
    use serde_json::json;
    use uuid::Uuid;

    fn thermal_event(value: &str) -> Event {
        Event {
            id: Uuid::new_v4(),
            source: EventSource::NervioCThermal,
            timestamp: Utc::now(),
            severity: Severity::Info,
            event_type: "cpu_thermal_reading".to_string(),
            metadata: json!({ "celsius": value }),
        }
    }

    #[test]
    fn parses_decimal_temperature_without_floating_point() {
        assert_eq!(
            DecisionEngine::temperature_celsius(&json!("65.9")),
            65
        );
        assert_eq!(DecisionEngine::temperature_celsius(&json!(72)), 72);
    }

    #[test]
    fn thermal_multiplier_is_integer_and_non_decreasing_with_heat() {
        let mut cool = DecisionEngine::new();
        cool.enable_thermal_coupling = true;
        cool.add_event(thermal_event("40"));

        let mut hot = DecisionEngine::new();
        hot.enable_thermal_coupling = true;
        hot.add_event(thermal_event("90"));

        assert!(hot.calculate_thermal_multiplier().to_raw()
            >= cool.calculate_thermal_multiplier().to_raw());
    }
}
