// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! 🕸️ ADM AGENT (Active Distributed Mesh)
//! =====================================
//! Reemplazo en Rust de `network_resonance.py`
//! Mantiene la coherencia de la red Malla (Metric Q -> SPA).

#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)] // BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
use me60os_core::spa::SPA;
use std::process::Command;
use std::thread;
use std::time::Duration;

/// Estructura para representar un vecino de la malla
#[derive(Debug)]
struct MeshNeighbor {
    _mac: String,
    tq_spa: SPA,
}

struct AdmAgent {
    target_coherence: SPA,
    current_coherence: SPA,
}

impl AdmAgent {
    pub fn new() -> Self {
        Self {
            // Target ~0.85 (0;51)
            target_coherence: SPA::new(0, 51, 0, 0, 0),
            current_coherence: SPA::zero(),
        }
    }

    pub fn run_loop(&mut self) {
        println!("🕸️  ADM AGENT ONLINE (SPA Metrics)");

        loop {
            self.tick();
            // Rhythm: 17s pulse is ideal, but for network monitoring we might want faster polling.
            // Using 5s for now locally.
            thread::sleep(Duration::from_secs(5));
        }
    }

    fn tick(&mut self) {
        let neighbors = self.read_batman_neighbors();

        if neighbors.is_empty() {
            println!("⚠️  No neighbors found. Isolation Mode.");
            return;
        }

        // Calculate Coherencia (Average TQ)
        let mut total_tq = SPA::zero();
        for n in &neighbors {
            total_tq = total_tq + n.tq_spa;
        }

        // n_len as SPA
        let n_len = SPA::from_raw(neighbors.len() as i64 * SPA::SCALE_0);
        let avg_coherence = total_tq / n_len;
        self.current_coherence = avg_coherence;

        self.decide_and_act();
    }

    fn read_batman_neighbors(&self) -> Vec<MeshNeighbor> {
        let output = Command::new("batctl").arg("n").output();

        match output {
            Ok(o) if o.status.success() => {
                let text = String::from_utf8_lossy(&o.stdout);
                self.parse_batctl(&text)
            }
            _ => {
                // Fallback / Simulation Mode
                // eprintln!("Failed to run batctl. Using dummy data.");
                vec![
                    MeshNeighbor {
                        _mac: "aa:bb:cc:dd:ee:01".to_string(),
                        tq_spa: SPA::new(0, 55, 0, 0, 0),
                    },
                    MeshNeighbor {
                        _mac: "aa:bb:cc:dd:ee:02".to_string(),
                        tq_spa: SPA::new(0, 48, 0, 0, 0),
                    },
                ]
            }
        }
    }

    fn parse_batctl(&self, text: &str) -> Vec<MeshNeighbor> {
        let mut neighbors = Vec::new();
        let lines: Vec<&str> = text.lines().collect();

        // Skip header if existent
        for line in lines.iter().skip(2) {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 4 {
                let mac = parts[0].to_string();
                // TQ is usually column 4 (index 3) or similar depending on version.
                // Assuming "02:02:02:02:02:02   0.240s   (255) ..."
                // TQ in parens is 0-255.

                // Buscar el valor entre paréntesis pareciéndose a TQ
                if let Some(tq_str) = parts
                    .iter()
                    .find(|p| p.starts_with('(') && p.ends_with(')'))
                {
                    let tq_clean = tq_str.trim_matches(|c| c == '(' || c == ')');
                    if let Ok(tq_int) = tq_clean.parse::<i64>() {
                        // Normalize 0-255 to SPA [0,1]
                        // val / 255
                        let spa_val = SPA::from_raw(tq_int * SPA::SCALE_0)
                            / SPA::from_raw(255 * SPA::SCALE_0);
                        neighbors.push(MeshNeighbor {
                            _mac: mac,
                            tq_spa: spa_val,
                        });
                    }
                }
            }
        }
        neighbors
    }

    fn decide_and_act(&self) {
        println!(
            "📊 Coherence: {} (Target: {})",
            self.current_coherence, self.target_coherence
        );

        if self.current_coherence < self.target_coherence {
            println!("⚡ LOW COHERENCE -> Requesting Phase Sync");
            // Here we would trigger a realignment
        } else if self.current_coherence > SPA::new(0, 58, 0, 0, 0) {
            println!("✅ HIGH COHERENCE -> Eco Mode");
        } else {
            println!("✅ Nominal.");
        }
    }
}

fn main() {
    let mut agent = AdmAgent::new();
    agent.run_loop();
}
