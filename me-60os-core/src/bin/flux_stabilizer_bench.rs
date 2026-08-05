// Bench: drift residual vs ciclos de estabilización de flux (S60 puro).
//
// Corre FluxStabilizer::stabilize() y emite CSV:
//   step,flux_raw,noise_raw,drift_raw
//
// El drift residual mide |current_flux - target_sigma| tras cada ciclo.
// Se espera convergencia exponencial hacia el target (damping factor 0.95).
// Ruido LCG determinista → fluctuaciones acotadas.
// Guardrails [8;0, 12;0] previenen divergencia.

use me60os_core::flux_stabilizer::FluxStabilizer;
use me60os_core::spa::SPA;

fn main() {
    let mut stabilizer = FluxStabilizer::new();
    let steps = 100;

    println!("# Bench: Drift residual vs ciclos de estabilización (S60 puro)");
    println!("# target_sigma (raw) = {}", stabilizer.target_sigma.to_raw());
    println!("# damping_factor (raw) = {}", stabilizer.damping_factor.to_raw());
    println!("# limit_upper (raw) = {}", stabilizer.limit_upper.to_raw());
    println!("# limit_lower (raw) = {}", stabilizer.limit_lower.to_raw());
    println!("# steps = {}", steps);
    println!("#");
    println!("step,flux_raw,noise_raw,drift_raw");

    let target_raw = stabilizer.target_sigma.to_raw();
    let one = SPA::new(1, 0, 0, 0, 0);
    let complement_damping = one - stabilizer.damping_factor;
    let noise_divisor = SPA::from_int(10);

    // Perturbación inicial
    stabilizer.current_flux = stabilizer.target_sigma + SPA::new(0, 5, 0, 0, 0);

    for step in 0..steps {
        // Ruido
        let noise = stabilizer.pseudo_flux_noise();
        let noise_scaled = {
            let raw = noise.to_raw();
            let div = noise_divisor.to_raw();
            if div != 0 { SPA::from_raw(raw / div) } else { SPA::zero() }
        };

        // Ecuación de estabilización
        let term1 = stabilizer.current_flux * stabilizer.damping_factor;
        let term2 = stabilizer.target_sigma * complement_damping;
        let mut next_flux = term1 + term2 + noise_scaled;

        // Guardrails
        if next_flux > stabilizer.limit_upper { next_flux = stabilizer.limit_upper; }
        if next_flux < stabilizer.limit_lower { next_flux = stabilizer.limit_lower; }

        stabilizer.current_flux = next_flux;

        let drift_raw = (stabilizer.current_flux - stabilizer.target_sigma).to_raw();
        println!("{},{},{},{}", step, stabilizer.current_flux.to_raw(), noise_scaled.to_raw(), drift_raw);
    }

    // Resumen final
    let final_drift = stabilizer.residual_drift().abs();
    let max_drift = stabilizer.history.iter()
        .map(|f| (*f - stabilizer.target_sigma).to_raw().abs())
        .max()
        .unwrap_or(0);
    let avg_drift = if !stabilizer.history.is_empty() {
        stabilizer.history.iter()
            .map(|f| (*f - stabilizer.target_sigma).to_raw().abs())
            .sum::<i64>() / stabilizer.history.len() as i64
    } else { 0 };

    eprintln!("\n=== RESUMEN FLUX STABILIZER ===");
    eprintln!("Pasos: {}", steps);
    eprintln!("Target sigma (raw): {}", target_raw);
    eprintln!("Final flux (raw): {}", stabilizer.current_flux.to_raw());
    eprintln!("Drift final (raw): {} (|{:.2}%|)", final_drift, (final_drift as f64 / target_raw as f64) * 100.0);
    eprintln!("Drift máximo (raw): {}", max_drift);
    eprintln!("Drift promedio (raw): {}", avg_drift);
    eprintln!("Flux dentro de guardrails: {}",
        stabilizer.history.iter().all(|f| *f >= stabilizer.limit_lower && *f <= stabilizer.limit_upper));

    // Verificar convergencia
    if final_drift < target_raw / 10 {
        eprintln!("✅ Convergencia aceptable (drift < 10% target)");
    } else {
        eprintln!("⚠️  Drift residual alto — revisar damping/noise");
    }
}