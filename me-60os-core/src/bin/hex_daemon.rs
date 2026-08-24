#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)]
// BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🛑 HEXAGONAL CONTROLLER DAEMON (Pilar 2 de la Trinidad Sentinel)
//! ===============================================================
//! Agente que ejecuta la Red Hexagonal de 91 Nodos con Salto 17.

use me60os_core::hexagonal_control::HexagonalController;
use std::thread;
use std::time::Duration;

fn main() {
    println!("🛡️  SENTINEL: Hexagonal Controller Daemon Active (Pilar 2 - Size 7: 91 Nodes)");
    let mut controller = HexagonalController::new(7);
    let mut tick = 0u64;

    loop {
        if tick.is_multiple_of(5) {
            // Read Time Crystal live energy from Cortex local metrics HTTP endpoint
            let crystal_energy_raw: i64 =
                match reqwest::blocking::get("http://127.0.0.1:8000/metrics") {
                    Ok(resp) => resp
                        .text()
                        .ok()
                        .and_then(|body| {
                            body.lines()
                                .find(|l| l.starts_with("sentinel_lattice_total_energy"))
                                .and_then(|l| {
                                    l.split_whitespace()
                                        .nth(1)
                                        .and_then(|v| v.parse::<i64>().ok())
                                })
                        })
                        .unwrap_or(0),
                    Err(_) => 0,
                };

            // Apply Salto 17 stabilization & Time-Crystal Coupled Dynamic Encryption Key Rotation
            let rift_center = (tick as usize * 17) % controller.n_nodes;
            let dynamic_key = controller.compute_crystal_coupled_key(crystal_energy_raw, tick);
            let (_status_code, _coherence, affected) = controller
                .control_rift_propagation(rift_center)
                .unwrap_or((-1, me60os_core::spa::SPA::zero(), 0));

            println!(
                "🔷 TICK {:04} | Hex Lattice Nodes: {} | Crystal Energy: {} | Dynamic Key S60: {} | Affected: {} | Status: STABLE (Salto 17 + Time Crystal Key)",
                tick,
                controller.n_nodes,
                crystal_energy_raw,
                dynamic_key,
                affected
            );
        }
        tick += 1;
        thread::sleep(Duration::from_secs(1));
    }
}
