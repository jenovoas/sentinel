// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
#![forbid(clippy::float_arithmetic)]
#![forbid(clippy::float_cmp)]
#![forbid(clippy::cast_possible_truncation)]
#![forbid(clippy::cast_precision_loss)]
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/main.rs
//! 🛡️ ME-60OS: NATIVE RESONANT CORE DAEMON 🛡️
//! ---------------------------------------------------------------------------
//! Binario nativo para ejecución de alta frecuencia (41Hz).

use me60os_core::agent_manager::{AgentManager, EnergyMonitorAgent};
use me60os_core::cortex::CortexEngine;
use std::thread;
use std::time::{Duration, Instant};

fn main() {
    println!("🔱 INITIALIZING NATIVE RESONANT CORE [RUST] 🔱");

    // 1. Initialize Cortex (60 Neurons)
    let mut cortex = CortexEngine::new(60);

    // 2. Initialize Agent Manager
    let mut agent_manager = AgentManager::new();

    // 3. Register Native Agents
    agent_manager.register_agent(Box::new(EnergyMonitorAgent::new("CoreMonitor")));

    // 4. Resonant Loop (41Hz -> ~24.39ms per tick)
    let tick_duration = Duration::from_nanos(24_390_243);
    let mut next_tick = Instant::now();

    println!("✅ NATIVE CORTEX LIVE. FREQUENCY: 41Hz");
    println!("   Loop precision: Nanoseconds");

    loop {
        let now = Instant::now();

        if now >= next_tick {
            // --- TICK INICIO ---

            // A. THINK (Execute Agents)
            agent_manager.tick(&cortex);

            // B. SENSE (Consume Buffers)
            cortex.consume_buffer(); // Direct access

            // C. SYNC (Persistence)
            if agent_manager.tick_count.is_multiple_of(360) {
                cortex.sync_persistence();
                println!(
                    "[RUST] Tick {} | Synchronizing Neural State...",
                    agent_manager.tick_count
                );
            }

            // --- TICK FIN ---
            next_tick += tick_duration;
        } else {
            // Spin-lock or Sleep for precision
            thread::yield_now();
        }

        // Safety break if needed (not in production daemon)
    }
}
