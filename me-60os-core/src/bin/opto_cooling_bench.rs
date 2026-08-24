// Bench: ocupacion fononica vs pasos de enfriamiento optomecánico (S60 puro).
//
// Corre OptomechanicalCooler::run_cooling_sequence_internal() y emite CSV:
//   step, g_raw, cooperativity_raw, n_final_raw
//
// La fisica: n_final = n_th_env / (1 + C) + n_min_limit
// donde C = 4*g^2 / (kappa * gamma_m) es la cooperatividad.
// A mayor g (acoplamiento), mayor C, menor n_final (mas frio).
// El quantum limit n_min_limit = (kappa / 4*omega_m)^2 es el piso cuantico.
//
// Sin floats. Sin RNG. Sin scipy. Aritmetica entera base-60.

#![allow(
    clippy::float_arithmetic,
    clippy::cast_precision_loss,
    clippy::cast_possible_truncation
)] // BIN bench/exp: medicion y estadisticas en f64; conversiones acotadas por construccion
use me60os_core::optomechanical::OptomechanicalCooler;

fn main() {
    let cooler = OptomechanicalCooler::new_internal();

    let n_th = cooler.n_th_env;
    let n_min = cooler.quantum_limit_internal();

    println!("# Bench: Ocupacion fononica vs enfriamiento optomecánico (S60 puro)");
    println!("# n_th_env (raw) = {}", n_th.to_raw());
    println!("# n_min_limit (raw) = {} (piso cuántico)", n_min.to_raw());
    println!("# omega_m (raw) = {}", cooler.omega_m.to_raw());
    println!("# gamma_m (raw) = {}", cooler.gamma_m.to_raw());
    println!("# kappa (raw) = {}", cooler.kappa.to_raw());
    println!("#");
    println!(
        "# Regimen: {}",
        if cooler.kappa.to_raw() < cooler.omega_m.to_raw() {
            "RESUELTO (kappa < omega_m) — enfriamiento eficiente al estado fundamental"
        } else {
            "NO RESUELTO (kappa >= omega_m) — limite Doppler"
        }
    );
    println!("#");
    println!("step,g_raw,cooperativity_raw,n_final_raw");

    let seq = cooler.run_cooling_sequence_internal(2000);

    for (step, (g, c, n_final)) in seq.iter().enumerate() {
        let step = step as u32;
        println!(
            "{},{},{},{}",
            step,
            g.to_raw(),
            c.to_raw(),
            n_final.to_raw()
        );
    }

    // Resumen final
    if let Some((_g_last, _c_last, n_last)) = seq.last().copied() {
        eprintln!("\n=== RESUMEN ===");
        eprintln!("Pasos muestreados: {}", seq.len());
        eprintln!("n_th_env (inicial) raw : {}", n_th.to_raw());
        eprintln!("n_final  (ultima)  raw : {}", n_last.to_raw());
        eprintln!("n_min_limit (piso) raw : {}", n_min.to_raw());
        let reduction = if n_th.to_raw() > 0 {
            // Porcentaje de reduccion: (n_th - n_final) / n_th * 100
            // en enteros S60: ((n_th - n_final) * 100 * SCALE_0) / (n_th * SCALE_0)
            // simplificando: (n_th - n_final) * 100 / n_th (raw directo)
            ((n_th.to_raw() - n_last.to_raw()) * 100) / n_th.to_raw()
        } else {
            0
        };
        eprintln!("Reduccion termica: {}%", reduction);
        if n_last < n_th {
            eprintln!("✅ Enfriamiento fonónico efectivo (n_final < n_th_env)");
        } else {
            eprintln!("⚠️  n_final NO bajó de n_th_env");
        }
        if n_last.to_raw() <= n_min.to_raw() + 1 {
            eprintln!("✅ Alcanzó el piso cuántico (n_final ≈ n_min_limit)");
        } else {
            eprintln!("ℹ️  Aún sobre piso cuántico (n_final > n_min_limit)");
        }
    } else {
        eprintln!("⚠️  Secuencia vacía");
        std::process::exit(1);
    }
}
