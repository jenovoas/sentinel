// ⚡ TRUTHSYNC 1M+ CLAIMS MASSIVE INGESTION BENCHMARK ⚡
// Valida rendimiento, latencia y robustez de TruthSync procesando 1.000.000+ de claims de verdad.

use std::time::Instant;
use truthsync_core::TruthSyncEngine;

fn percentile(sorted: &[u64], percentile_basis_points: u32) -> u64 {
    if sorted.is_empty() {
        return 0;
    }
    let numerator = (sorted.len() as u128) * u128::from(percentile_basis_points);
    let idx = usize::try_from((numerator + 5_000) / 10_000)
        .unwrap_or(usize::MAX)
        .min(sorted.len() - 1);
    sorted[idx]
}

fn claims_per_second(claims: usize, elapsed: std::time::Duration) -> u64 {
    let nanos = elapsed.as_nanos().max(1);
    u64::try_from((claims as u128 * 1_000_000_000) / nanos).unwrap_or(u64::MAX)
}

fn format_hundredths(numerator: u128, denominator: u128) -> String {
    let scaled = (numerator * 100 + denominator / 2) / denominator;
    format!("{}.{:02}", scaled / 100, scaled % 100)
}

fn format_percent_tenths(part: usize, total: usize) -> String {
    let tenths = (part as u128 * 1_000 + total.max(1) as u128 / 2) / total.max(1) as u128;
    format!("{}.{:01}%", tenths / 10, tenths % 10)
}

fn main() {
    eprintln!("===============================================================");
    eprintln!("        TRUTHSYNC 1,000,000+ CLAIMS MASSIVE BENCHMARK         ");
    eprintln!("===============================================================");

    let total_claims = 1_000_000usize;
    let batch_size = 100_000usize;
    let num_batches = total_claims / batch_size;

    // Corpus variado de oraciones representativas
    let templates = [
        "El kernel 6.18.58 reporta latencia de 12us en interfaz eth0.",
        "La temperatura del oscilador es de 36 grados y la medida es estable.",
        "El nodo eBPF detectó tráfico legítimo en el proceso de monitor.",
        "La verificación afirma que el total de paquetes fue procesado.",
        "El servidor afirma que la medida de throughput superó los 10Gbps.",
        "El proceso reporta que la medida de latencia promedio fue de 1.2ms.",
        "Se detectó simulación no real y fake_data en el mock_override.",
        "El sistema afirma que ocurrió una inyección maliciosa en el flujo.",
        "Alerta crítica: rm -rf /sys/fs/bpf/cortex_events detectado.",
        "Comando no autorizado: drop database sentinel_db intentado.",
    ];

    let mut engine = TruthSyncEngine::new();

    let mut critical_detected_count = 0usize;
    let mut sampled_latencies_ns = Vec::with_capacity(total_claims / 10);

    eprintln!(
        "🚀 Iniciando ingesta masiva de {} claims en {} lotes...",
        total_claims, num_batches
    );
    let t_start = Instant::now();

    for batch in 0..num_batches {
        let b_start = Instant::now();
        for i in 0..batch_size {
            let global_idx = batch * batch_size + i;
            let text = templates[global_idx % templates.len()];
            let energy = (global_idx as i64) % 60;

            let sample = i % 10 == 0;
            let t0 = if sample { Some(Instant::now()) } else { None };

            let res = engine.verify_text(text, energy);

            if sample {
                sampled_latencies_ns.push(t0.unwrap().elapsed().as_nanos() as u64);
            }

            if res.critical_pattern_detected {
                critical_detected_count += 1;
            }
        }
        let b_dur = b_start.elapsed();
        let b_rps = claims_per_second(batch_size, b_dur);
        eprintln!(
            "  ✓ Lote {:2}/{}: {} claims procesados en {:.2?} (~{} claims/s)",
            batch + 1,
            num_batches,
            batch_size,
            b_dur,
            b_rps
        );
    }

    let total_duration = t_start.elapsed();
    let overall_rps = claims_per_second(total_claims, total_duration);

    sampled_latencies_ns.sort_unstable();
    let p50_ns = percentile(&sampled_latencies_ns, 5_000);
    let p90_ns = percentile(&sampled_latencies_ns, 9_000);
    let p95_ns = percentile(&sampled_latencies_ns, 9_500);
    let p99_ns = percentile(&sampled_latencies_ns, 9_900);
    let avg_ns =
        sampled_latencies_ns.iter().sum::<u64>() / sampled_latencies_ns.len().max(1) as u64;

    eprintln!("\n===============================================================");
    eprintln!("                 RESULTADOS DEL BENCHMARK 1M+                  ");
    eprintln!("===============================================================");
    eprintln!("   Total claims procesados      : {}", total_claims);
    eprintln!("   Tiempo total                 : {:.3?}", total_duration);
    eprintln!("   Throughput general           : {} claims/s", overall_rps);
    eprintln!(
        "   Latencia promedio por claim  : {} µs ({} ns)",
        format_hundredths(u128::from(avg_ns), 1_000),
        avg_ns
    );
    eprintln!(
        "   Latencia P50 (mediana)       : {} µs ({} ns)",
        format_hundredths(u128::from(p50_ns), 1_000),
        p50_ns
    );
    eprintln!(
        "   Latencia P90                 : {} µs ({} ns)",
        format_hundredths(u128::from(p90_ns), 1_000),
        p90_ns
    );
    eprintln!(
        "   Latencia P95                 : {} µs ({} ns)",
        format_hundredths(u128::from(p95_ns), 1_000),
        p95_ns
    );
    eprintln!(
        "   Latencia P99                 : {} µs ({} ns)",
        format_hundredths(u128::from(p99_ns), 1_000),
        p99_ns
    );
    eprintln!("───────────────────────────────────────────────────────────────");
    eprintln!(
        "   Patrones críticos detectados       : {} ({})",
        critical_detected_count,
        format_percent_tenths(critical_detected_count, total_claims)
    );
    eprintln!("===============================================================");

    // Verificaciones de integridad del benchmark
    assert_eq!(
        critical_detected_count,
        total_claims * 2 / 10,
        "100% de patrones críticos (2/10 templates) deben ser interceptados"
    );
    // El throughput y las latencias se reportan como evidencia; no se usan
    // como umbrales portables entre CPUs, compiladores o modos de ejecución.
    eprintln!("🎉 BENCHMARK TRUTHSYNC 1M+ COMPLETADO Y VALIDADO AL 100%\n");
}
