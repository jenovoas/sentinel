use std::time::Duration;
use tracing::{info, warn};

/// Escalas de Flujo Cuántico basadas en Base-60
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FlowScale {
    Laminar,    // < 24/60 presión o < 6/60s latencia
    Turbulent,  // > 24/60 presión o > 6/60s latencia
    FlashFlood, // > 51/60 presión o > 30/60s latencia
}

pub struct FluidController {
    capacity: usize,
    current_scale: FlowScale,
}

impl FluidController {
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            current_scale: FlowScale::Laminar,
        }
    }

    /// Calcula la escala del fluido usando ratios sexagesimales puros
    pub fn observe(&mut self, current_occupancy: usize, processing_latency_ms: f64) -> FlowScale {
        // Presión en base 60: (ocupación * 60) / capacidad
        let pressure_s60 = (current_occupancy * 60) / self.capacity;
        
        // Latencia en base 60 (unidades de 1/60s, aprox 16.66ms cada una)
        // 60 unidades = 1000ms. 
        // 6 unidades = 100ms (Turbulent)
        // 30 unidades = 500ms (FlashFlood)
        let latency_s60 = (processing_latency_ms * 60.0 / 1000.0) as usize;

        let new_scale = if pressure_s60 > 51 || latency_s60 > 30 {
            FlowScale::FlashFlood
        } else if pressure_s60 > 24 || latency_s60 > 6 {
            FlowScale::Turbulent
        } else {
            FlowScale::Laminar
        };

        if new_scale != self.current_scale {
            warn!(
                "🌊 Transición Sexagesimal: {:?} -> {:?} (Presión: {}/60, Latencia: {}/60)", 
                self.current_scale, 
                new_scale,
                pressure_s60,
                latency_s60
            );
            self.current_scale = new_scale;
        }

        new_scale
    }

    pub fn get_batch_size(&self) -> usize {
        match self.current_scale {
            FlowScale::Laminar => 10,
            FlowScale::Turbulent => 50,
            FlowScale::FlashFlood => 200,
        }
    }

    pub fn get_sleep_duration(&self) -> Duration {
        match self.current_scale {
            // Laminar: 30/60 s (500ms)
            FlowScale::Laminar => Duration::from_millis(500),
            // Turbulent: 6/60 s (100ms)
            FlowScale::Turbulent => Duration::from_millis(100),
            // FlashFlood: 1/60 s (aprox 16ms)
            FlowScale::FlashFlood => Duration::from_millis(16),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_s60_fluid_transitions() {
        let mut ctrl = FluidController::new(100);
        
        // Caso 1: Todo bajo control (9/60 presión, 1/60s latencia)
        assert_eq!(ctrl.observe(15, 20.0), FlowScale::Laminar);
        
        // Caso 2: Turbulencia por presión (30/60 > 24/60)
        assert_eq!(ctrl.observe(50, 20.0), FlowScale::Turbulent);
        
        // Caso 3: Turbulencia por latencia (10/60s > 6/60s)
        assert_eq!(ctrl.observe(10, 170.0), FlowScale::Turbulent);
        
        // Caso 4: Crítico por presión (55/60 > 51/60)
        assert_eq!(ctrl.observe(92, 20.0), FlowScale::FlashFlood);
        
        // Caso 5: Crítico por latencia (35/60s > 30/60s)
        assert_eq!(ctrl.observe(10, 600.0), FlowScale::FlashFlood);
    }
}
