use std::time::{Duration, Instant};
use tokio::time::sleep;

/// Orquestador de Ritmo Temporal S60
/// Mantiene la coherencia del sistema mediante ciclos armónicos.
pub struct ResonantLoop {
    /// Duración del ciclo de respiración (17s)
    breath_cycle: Duration,
    /// Duración del ciclo maestro (68s)
    master_cycle: Duration,
    /// Inicio del ciclo actual
    cycle_start: Instant,
}

impl ResonantLoop {
    pub fn new() -> Self {
        Self {
            breath_cycle: Duration::from_secs(17),
            master_cycle: Duration::from_secs(68),
            cycle_start: Instant::now(),
        }
    }

    /// Espera hasta el siguiente punto de sincronización armónica
    /// Retorna true si es un "Master Reset" (cada 68s)
    pub async fn wait_next_pulse(&mut self) -> bool {
        let now = Instant::now();
        let elapsed = now.duration_since(self.cycle_start);

        // Calcular tiempo restante para completar el ciclo de 17s
        let remainder = elapsed.as_millis() % self.breath_cycle.as_millis();
        let wait_ms = self.breath_cycle.as_millis() - remainder;

        if wait_ms > 0 {
            tracing::debug!("⏳ Resonant Loop: Syncing phase ({}ms)", wait_ms);
            sleep(Duration::from_millis(wait_ms as u64)).await;
        }

        // Verificar si completamos un ciclo maestro (68s) - AXIOMA V: BIO-CENTRISMO
        // El Salto-17 corrige el drift relativista en este límite.
        let total_elapsed = now.duration_since(self.cycle_start);
        let is_master_reset = total_elapsed >= self.master_cycle;

        if is_master_reset {
            tracing::info!("🌀 MASTER CYCLE RESET (68s): Purging Entropy (Quantum Leap)...");
            self.cycle_start = Instant::now(); // Reset de fase
            true
        } else {
            false
        }
    }
}
