// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
// 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
// -----------------------------------------------------------------------------
// EXPERIMENTO 012: COMPRESIÓN DE FASE (DUAL CHANNEL)
// -----------------------------------------------------------------------------
// Objetivo:
//   Validar almacenamiento simultáneo en Amplitud (Chan A) y Fase (Chan B).
//   Confirmar que la estabilización corrige errores de fase sin corromper datos.
//   Replica EXP_012_PHASE_COMPRESSION.py en Rust puro (SPA base-60).
// -----------------------------------------------------------------------------

use me60os_core::quantum_core::LiquidLattice;
use me60os_core::spa::SPA;

fn main() {
    println!("🔬 EXP-012: PHASE COMPRESSION & QUANTUM SNAPPING (RUST PURO)");
    println!("{}", "-".repeat(60));

    let mut ok = true;

    // ─────────────────────────────────────────────────────────────
    // 1) SETUP — 3 anillos hexadecimales (~37 nodos)
    // ─────────────────────────────────────────────────────────────
    let mut lattice = LiquidLattice::new(64);

    // ─────────────────────────────────────────────────────────────
    // 2) PAYLOADS DUAL
    //    Canal A: amplitud (chunk 8 bytes → SPA)
    //    Canal B: fase (1 byte → grados 0-359)
    // ─────────────────────────────────────────────────────────────
    let msg_a = b"ENERGY_CHANNEL_CRITICAL_DATA_BLOCK_ALPHA_01";
    let msg_b = b"PHASE_KEY";

    println!(
        "📦 Payload A (Energy): {:?}",
        std::str::from_utf8(msg_a).unwrap()
    );
    println!(
        "📦 Payload B (Phase) : {:?}",
        std::str::from_utf8(msg_b).unwrap()
    );

    // Padding para A >= 16*B (requerido por retrieve: energy > phase para cobertura)
    let padding: Vec<u8> = (0u8..150u8).collect();
    let mut msg_a_padded = msg_a.to_vec();
    msg_a_padded.extend_from_slice(&padding);

    // ─────────────────────────────────────────────────────────────
    // 3) INYECCIÓN DUAL
    // ─────────────────────────────────────────────────────────────
    println!("\n💉 Inyectando en Canales Paralelos...");
    lattice.inject_dual_channel(msg_a_padded.clone(), msg_b.to_vec());

    let phase_inj0 = lattice.buffer.lattice[0].phase;
    println!("   [Debug] Node 0 Phase (After Inject): {:?}", phase_inj0);

    // ─────────────────────────────────────────────────────────────
    // 4) RUIDO DE FASE (deriva de 0.5 grados por nodo)
    // ─────────────────────────────────────────────────────────────
    println!("\n🌪️  Inyectando Ruido de Fase (deriva ~0.5°/nodo)...");
    for node in lattice.buffer.lattice.iter_mut() {
        let noise_deg = SPA::new(0, 30, 0, 0, 0); // 30/60 = 0.5 grados
        node.phase = node.phase + noise_deg;
    }

    let phase_noisy = lattice.buffer.lattice[0].phase;
    println!("   [Debug] Node 0 Phase (Noisy): {:?}", phase_noisy);

    // ─────────────────────────────────────────────────────────────
    // 5) ESTABILIZACIÓN (snap de fase, 5 ciclos)
    // ─────────────────────────────────────────────────────────────
    println!("\n🌊 Ejecutando 'Sector Snapping' (corrección de fase)...");
    snap_phases(&mut lattice.buffer.lattice, 5);

    let phase_snapped = lattice.buffer.lattice[0].phase;
    println!("   [Debug] Node 0 Phase (Snapped): {:?}", phase_snapped);

    // ─────────────────────────────────────────────────────────────
    // 6) RECUPERACIÓN DUAL
    // ─────────────────────────────────────────────────────────────
    println!("\n🔍 Recuperando Dual-Channel...");
    let (rec_a, rec_b) = lattice.retrieve_dual_channel(msg_a_padded.len(), msg_b.len());

    println!(
        "   Rec A len: {} (esperado {})",
        rec_a.len(),
        msg_a_padded.len()
    );
    println!("   Rec B len: {} (esperado {})", rec_b.len(), msg_b.len());

    println!("   Debug B decode (snapped phases):");
    let sector_width = SPA::from_int(45) / SPA::from_int(32);
    let half_width = sector_width / SPA::from_int(2);
    for (i, node) in lattice.buffer.lattice.iter().take(msg_b.len()).enumerate() {
        let deg = node.phase.to_raw() / SPA::SCALE_0;
        let sector_idx = ((node.phase + half_width) / sector_width).to_raw() / SPA::SCALE_0;
        let byte_back = sector_idx.clamp(0, 255) as u8;
        println!(
            "     nodo {}: phase_raw={}, deg={}, byte_back={} (orig={})",
            i,
            node.phase.to_raw(),
            deg,
            byte_back,
            msg_b[i]
        );
    }

    // ─────────────────────────────────────────────────────────────
    // 7) VALIDACIÓN
    // ─────────────────────────────────────────────────────────────
    // Canal B: msg_b debe estar contenido en rec_b
    let rec_b_str = String::from_utf8_lossy(&rec_b);
    if rec_b_str.starts_with(std::str::from_utf8(msg_b).unwrap()) {
        println!("\n✅ SUCCESS: Phase Data Recovered accurately despite noise.");
    } else {
        println!("\n❌ FAILURE: Phase Data Corrupted.");
        println!("   Exp: {:?}", std::str::from_utf8(msg_b).unwrap());
        println!("   Got: {:?}", rec_b_str);
        ok = false;
    }

    // Canal A: integridad total estricta (100% bytes exactos)
    if rec_a == msg_a_padded {
        println!("✅ SUCCESS: Energy Data (amplitud) recuperada con 100% integridad.");
    } else {
        println!(
            "❌ FAILURE: Energy Data Corrupted (recuperados {}/{} bytes).",
            rec_a.len(),
            msg_a_padded.len()
        );
        for (idx, (got, exp)) in rec_a.iter().zip(msg_a_padded.iter()).enumerate() {
            if got != exp {
                println!(
                    "   primer diff en byte {}: got 0x{:02x}, exp 0x{:02x}",
                    idx, got, exp
                );
                break;
            }
        }
        ok = false;
    }

    println!(
        "\n{}",
        if ok {
            "🏆 EXP-012 COMPLETO: compressión de fase + dual channel verificados"
        } else {
            "⚠️  EXP-012: algunas pruebas fallaron"
        }
    );
}

fn snap_phases(
    lattice: &mut [me60os_core::isochronous_oscillator::IsochronousOscillator],
    cycles: usize,
) {
    let sector_width = SPA::from_int(45) / SPA::from_int(32);
    let half_width = sector_width / SPA::from_int(2);

    for _ in 0..cycles {
        let phases: Vec<SPA> = lattice.iter().map(|c| c.phase).collect();
        let mut new_phases = phases.clone();
        let size = lattice.len();

        for i in 0..size {
            if phases[i] == SPA::zero() {
                continue;
            }
            let mut total = phases[i];
            let mut count: i64 = 1;

            if i > 0 && phases[i - 1] != SPA::zero() {
                let diff = if phases[i] >= phases[i - 1] {
                    phases[i] - phases[i - 1]
                } else {
                    phases[i - 1] - phases[i]
                };
                if diff <= half_width {
                    total = total + phases[i - 1];
                    count += 1;
                }
            }
            if i < size - 1 && phases[i + 1] != SPA::zero() {
                let diff = if phases[i] >= phases[i + 1] {
                    phases[i] - phases[i + 1]
                } else {
                    phases[i + 1] - phases[i]
                };
                if diff <= half_width {
                    total = total + phases[i + 1];
                    count += 1;
                }
            }
            let avg = total / SPA::from_int(count);

            let sector_idx = ((avg + half_width) / sector_width).to_raw() / SPA::SCALE_0;
            new_phases[i] = sector_width * SPA::from_int(sector_idx.clamp(0, 255));
        }

        for (i, np) in new_phases.iter().enumerate() {
            lattice[i].phase = *np;
        }
    }
}
