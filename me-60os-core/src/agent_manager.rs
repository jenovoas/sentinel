// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/agent_manager.rs
//! 🛡️ ME-60OS: NATIVE AGENT ORCHESTRATOR (RUST) 🛡️
//! ---------------------------------------------------------------------------
//! Maneja el registro y ejecución de agentes SPA con precisión de nanosegundos.

use crate::cortex::CortexEngine;
use crate::spa::SPA;

/// Trait fundamental para agentes en ME-60OS.
pub trait AgentSPA: Send + Sync {
    fn name(&self) -> &str;

    /// Percibir el estado del Cortex (Zero-Copy access)
    fn percibir(&mut self, cortex: &CortexEngine) -> bool;

    /// Tomar una decisión basada en el estado
    fn decidir(&mut self) -> String;

    /// Actuar sobre el sistema
    fn actuar(&mut self, action: String);

    /// Ciclo completo: percibir -> decidir -> actuar
    fn tick(&mut self, cortex: &CortexEngine) {
        if self.percibir(cortex) {
            let action = self.decidir();
            if action != "NO_OP" {
                self.actuar(action);
            }
        }
    }
}

/// Gestor de agentes nativos.
pub struct AgentManager {
    pub agents: Vec<Box<dyn AgentSPA>>,
    pub tick_count: u64,
}

impl AgentManager {
    pub fn new() -> Self {
        Self {
            agents: Vec::new(),
            tick_count: 0,
        }
    }

    pub fn register_agent(&mut self, agent: Box<dyn AgentSPA>) {
        println!("🤖 [RUST-ORCH] Agente registrado: {}", agent.name());
        self.agents.push(agent);
    }

    /// Ejecuta un tick síncrono para todos los agentes.
    pub fn tick(&mut self, cortex: &CortexEngine) {
        self.tick_count += 1;
        for agent in &mut self.agents {
            agent.tick(cortex);
        }
    }
}

impl Default for AgentManager {
    fn default() -> Self {
        Self::new()
    }
}

// --- EJEMPLO DE AGENTE NATIVO: MONITOR DE ENERGÍA ---
pub struct EnergyMonitorAgent {
    name: String,
    last_energy: SPA,
}

impl EnergyMonitorAgent {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            last_energy: SPA::zero(),
        }
    }
}

impl AgentSPA for EnergyMonitorAgent {
    fn name(&self) -> &str {
        &self.name
    }

    fn percibir(&mut self, cortex: &CortexEngine) -> bool {
        // En Rust, cortex.total_energy es accesible directamente
        self.last_energy = cortex.total_energy;
        true
    }

    fn decidir(&mut self) -> String {
        // Lógica simple: si la energía supera 1.5, enfriar
        let threshold = SPA::new(1, 30, 0, 0, 0); // 1.5
        if self.last_energy > threshold {
            "COOLING_REQUESTED".to_string()
        } else {
            "NO_OP".to_string()
        }
    }

    fn actuar(&mut self, action: String) {
        println!("⚡ [AGENT:{}] Directiva nativa: {}", self.name, action);
    }
}
