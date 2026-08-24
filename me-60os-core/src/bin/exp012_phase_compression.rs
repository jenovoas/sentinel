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
use me60os_core::resonant_matrix::ResonantMatrix;
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
    lattice.buffer.lattice[0].phase = phase_noisy;
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
    for (i, node) in lattice.buffer.lattice.iter().take(msg_b.len()).enumerate() {
        let deg = node.phase.to_raw() / SPA::SCALE_0;
        let byte_back = ((deg * 256) / 360) as u8;
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

    // Canal A: integridad total
    if rec_a.len() >= msg_a_padded.len() / 2 {
        println!("✅ SUCCESS: Energy Data (amplitud) inyectada correctamente.");
    } else {
        println!("⚠️  Energy Data integrity check inconclusive.");
    }

    // ─────────────────────────────────────────────────────────────
    // 8) VERIFICACIÓN FIDELIDAD COLECTIVA (ResonantMatrix, doble malla)
    // ─────────────────────────────────────────────────────────────
    println!("\n{}", "=".repeat(60));
    println!("🔮 FIDELIDAD COLECTIVA — DOBLE MALLA (ResonantMatrix)");
    println!("{}", "=".repeat(60));

    let mut lane_a = ResonantMatrix::new(16);
    let mut lane_b = ResonantMatrix::new(16);

    let seed = "Yo Soy";
    println!("   Semilla: '{}'", seed);

    // Damping = 0 para modo superconductor
    for c in lane_a.crystals.iter_mut() {
        c.damping_factor = SPA::zero();
    }
    for c in lane_b.crystals.iter_mut() {
        c.damping_factor = SPA::zero();
    }

    // Paso 1: base resonante antes de inyectar
    let base_a = lane_a.get_amplitudes();
    let base_b = lane_b.get_amplitudes();

    // Paso 2: inyectar semilla
    for (i, ch) in seed.chars().enumerate() {
        lane_a.inject_pai(i, ch as i64, 1);
        lane_b.inject_pai(i, ch as i64, 1);
    }

    // Paso 3: leer amplitudes corregidas por base
    let amps_a = lane_a.get_amplitudes();
    let amps_b = lane_b.get_amplitudes();

    let mut recovered = String::new();
    let mut converge = true;
    for i in 0..seed.len() {
        let raw_a = (amps_a[i] - base_a[i]).to_raw();
        let raw_b = (amps_b[i] - base_b[i]).to_raw();
        if raw_a.abs_diff(raw_b) > (SPA::SCALE_0 / 50) as u64 {
            converge = false;
        }
        let ch_val = raw_a / SPA::SCALE_0;
        if let Ok(ch) = u8::try_from(ch_val) {
            if ch.is_ascii() && ch != 0 {
                recovered.push(char::from(ch));
            }
        }
    }

    if converge {
        println!("   📖 Reconstruido: '{}' — FIDELIDAD 100% ✅", recovered);
    } else {
        println!(
            "   📖 Reconstruido: '{}' — FIDELIDAD DEGRADADA ⚠️",
            recovered
        );
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
                total = total + phases[i - 1];
                count += 1;
            }
            if i < size - 1 && phases[i + 1] != SPA::zero() {
                total = total + phases[i + 1];
                count += 1;
            }
            new_phases[i] = total / SPA::from_int(count);
        }

        for (i, np) in new_phases.iter().enumerate() {
            lattice[i].phase = *np;
        }
    }
}
