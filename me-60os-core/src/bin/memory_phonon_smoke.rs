// Smoke test de memorias de cristal resonante + computación fonónica + dual channel.
// Rust puro (sin Python, sin kernel). Valida lo que SÍ existe en el core.
//
// NOTA: ResonantMatrix (lattice hexagonal 68k nodos) solo existe en modo
// extension-module (Python); aca usamos LiquidLattice + inject_dual_channel
// (quantum_core) que SI estan disponibles en binario Rust.

use me60os_core::optomechanical::OptomechanicalCooler;
use me60os_core::quantum_core::LiquidLattice;
use me60os_core::pai60_lib;
use me60os_core::spa::SPA;

fn main() {
    let mut ok = true;

    // ─────────────────────────────────────────────────────────────
    // 1) COMPUTACIÓN FONÓNICA (sideband cooling, base-60 puro)
    // ─────────────────────────────────────────────────────────────
    println!("❄️  [1] OPTOMECHANICAL / FONONES");
    let cooler = OptomechanicalCooler::new_internal();
    let n_th = cooler.n_th_env;
    println!("   n_th_env (calibración): {} (raw {})", n_th, n_th.to_raw());
    let qlim = cooler.quantum_limit_internal();
    println!("   quantum limit n_min    : {} (raw {})", qlim, qlim.to_raw());
    // Secuencia de enfriamiento: la ocupación fonónica final debe bajar de n_th
    let seq = cooler.run_cooling_sequence_internal(200);
    if let Some((_g, _c, n_final)) = seq.last().copied() {
        println!("   n_final tras enfriamiento: {} (raw {})", n_final, n_final.to_raw());
        // Efecto de enfriamiento: n_final < n_th (por división por 1+c)
        if n_final < n_th {
            println!("   ✅ enfriamiento fonónico efectivo (n_final < n_th)");
        } else {
            println!("   ⚠️  n_final no bajó de n_th");
            ok = false;
        }
    } else {
        println!("   ⚠️  secuencia de enfriamiento vacía");
        ok = false;
    }

    // ─────────────────────────────────────────────────────────────
    // 2) DUAL CHANNEL (inyección de amplitud + fase en malla de cristal)
    // ─────────────────────────────────────────────────────────────
    println!("\n💠 [2] DUAL CHANNEL (amplitud canal A + fase canal B)");
    let mut lat = LiquidLattice::new(64);
    // Canal A: 8 bytes payload -> amplitud S60 en nodo i
    let payload_a: Vec<u8> = (1u8..=8).collect(); // 01 02 .. 08
    // Canal B: 1 byte por nodo -> fase (grados 0..359 mapeados de 0..255)
    let payload_b: Vec<u8> = (0u8..=63).collect();
    lat.inject_dual_channel(payload_a.clone(), payload_b.clone());

    // Verificar que el nodo 0 recibió amplitud derivada de payload_a[0..8]
    // (big-endian 8 bytes => 0x0102030405060708) pasada por SPA::from_raw.
    let expected_amp_raw: i64 = i64::from_be_bytes([1, 2, 3, 4, 5, 6, 7, 8]);
    let node0_amp = lat.buffer.lattice[0].amplitude.to_raw();
    println!("   nodo0 amplitud raw: {} (esperado {})", node0_amp, expected_amp_raw);
    if node0_amp == SPA::from_raw(expected_amp_raw).to_raw() {
        println!("   ✅ canal A (amplitud) inyectado correcto");
    } else {
        println!("   ⚠️  canal A no coincide");
        ok = false;
    }
    // Verificar fase del nodo 0 derivada de payload_b[0]=0 -> 0 grados
    let node0_phase = lat.buffer.lattice[0].phase.to_raw();
    println!("   nodo0 fase raw: {} (de byte B=0 -> 0°)", node0_phase);
    if node0_phase == SPA::new(0, 0, 0, 0, 0).to_raw() {
        println!("   ✅ canal B (fase) inyectado correcto");
    } else {
        println!("   ⚠️  canal B no coincide");
        ok = false;
    }

    // ─────────────────────────────────────────────────────────────
    // 3) PAI-60 (conversión binario -> amplitud recíproca EXACTA)
    // ─────────────────────────────────────────────────────────────
    println!("\n🔢 [3] PAI-60 (razón recíproca exacta, sin float)");
    // 30 / 60 = 1/2 exacto => raw de SPA(0,30,0,0,0)
    match pai60_lib::pai60_divide(SPA::from_int(30), 60) {
        Some(half) => {
            let expected = SPA::new(0, 30, 0, 0, 0).to_raw();
            println!("   30/60 => raw {} (esperado {})", half.to_raw(), expected);
            if half.to_raw() == expected {
                println!("   ✅ PAI-60 30/60 = 1/2 exacto");
            } else {
                println!("   ⚠️  PAI-60 no dio 1/2");
                ok = false;
            }
        }
        None => {
            println!("   ⚠️  denominador 60 no encontrado en tabla PAI-60");
            ok = false;
        }
    }

    // ─────────────────────────────────────────────────────────────
    println!("\n{}", if ok { "✅ MEMORIA/FONON/DUAL/PAI VERIFICADOS (S60, sin floats)" } else { "⚠️  ALGUNA VERIFICACIÓN FALLÓ" });
    std::process::exit(if ok { 0 } else { 1 });
}
