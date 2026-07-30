// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// src/bin/adm_sim.rs
//! 🍄 MYCNET SIMULATION 🍄
//! Visualizes the hexagonal lattice formation and signal propagation.

use me60os_core::adm::{AxialCoord, ADM};
use me60os_core::spa::SPA;
use std::{thread, time};

// Helper function to generate a hexagonal spiral of AxialCoords
fn generate_spiral(num_nodes: usize) -> Vec<AxialCoord> {
    let mut nodes = Vec::with_capacity(num_nodes);
    if num_nodes == 0 {
        return nodes;
    }

    nodes.push(AxialCoord::new(0, 0));
    if num_nodes == 1 {
        return nodes;
    }

    let mut q = 0;
    let mut r = 0;

    let mut direction = 0; // 0: +q, 1: +s, 2: +r, 3: -q, 4: -s, 5: -r
    let mut segment_length = 1;
    let mut steps_taken = 0;
    let mut turns_made = 0;

    while nodes.len() < num_nodes {
        match direction {
            0 => q += 1, // +q
            1 => {}      // +s (q--, r++) handled below
            2 => r += 1, // +r
            3 => q -= 1, // -q
            4 => {}      // -s (q++, r--) handled below
            5 => r -= 1, // -r
            _ => unreachable!(),
        }
        // Convert s-coordinate to q,r for AxialCoord
        // If we are tracking q,r,s, then s = -q-r.
        // When moving +s, it means q decreases and r increases.
        // When moving -s, it means q increases and r decreases.
        // The AxialCoord::new(q, r) handles the s implicitly.
        // So, we just need to update q and r based on the direction.
        match direction {
            0 => { /* q already incremented */ }
            1 => {
                q -= 1;
                r += 1;
            } // +s
            2 => { /* r already incremented */ }
            3 => { /* q already decremented */ }
            4 => {
                q += 1;
                r -= 1;
            } // -s
            5 => { /* r already decremented */ }
            _ => unreachable!(),
        }

        nodes.push(AxialCoord::new(q, r));
        if nodes.len() == num_nodes {
            break;
        }

        steps_taken += 1;
        if steps_taken == segment_length {
            steps_taken = 0;
            direction = (direction + 1) % 6;
            turns_made += 1;
            if turns_made % 2 == 0 {
                segment_length += 1;
            }
        }
    }
    nodes
}

fn main() {
    println!("🍄 PREPARING MYCNET LATTICE SIMULATION...");
    let mut net = ADM::new();

    // 1. Create a 72-node Solar Topology (Sacred Geometry)
    println!("   Creating Solar Topology (72 Nodes)...");

    // Simplificación: Generación espiral para garantizar 72 exactos
    let spiral_nodes = generate_spiral(72);
    for node in spiral_nodes {
        net.add_node(node.q, node.r);
    }

    println!("✅ Nodes Created: {}", net.nodes.len());

    // 2. Inject Signal into Center
    let center = AxialCoord::new(0, 0);
    if let Some(node) = net.nodes.get_mut(&center) {
        println!("💉 Injecting Resonant Spike into Center (0,0)...");
        node.amplitude = SPA::new(2, 0, 0, 0, 0); // Trigger threshold
    }

    // 3. Simulate Propagation
    println!("🚀 RUNNING SIMULATION (41Hz)...");
    let dt = SPA::new(0, 0, 0, 0, 1);

    for i in 0..10 {
        println!("\n[TICK {}] --------------------------------", i);
        net.tick(dt);

        for (coord, node) in &net.nodes {
            let amp = node.amplitude.to_string();
            // Ascii art viz (simplified)
            let viz = if node.amplitude > SPA::new(1, 0, 0, 0, 0) {
                "🔴 (ACTIVE)"
            } else if node.amplitude > SPA::new(0, 30, 0, 0, 0) {
                "🟡 (CHARGING)"
            } else {
                "🔵 (IDLE)"
            };

            println!("   Node ({},{}): {} | {}", coord.q, coord.r, viz, amp);
        }

        thread::sleep(time::Duration::from_millis(250));
    }
}
