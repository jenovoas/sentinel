// Reproducible high-volume benchmark for TruthSync (<1M claims).
// Timing is reported as evidence and is not treated as a portable pass/fail
// threshold; throughput depends on CPU, compiler and runtime configuration.

use std::time::Instant;
use truthsync_core::TruthSyncEngine;

fn percentile(sorted: &[u64], pct: usize) -> u64 {
    if sorted.is_empty() {
        return 0;
    }
    let index = (sorted.len() * pct).div_ceil(100).saturating_sub(1);
    sorted[index.min(sorted.len() - 1)]
}

fn main() {
    const TOTAL_CLAIMS: usize = 1_000_000;
    const SAMPLE_EVERY: usize = 10;

    let templates = [
        "El kernel reporta latencia de 12us en interfaz eth0.",
        "La temperatura del oscilador es de 36 grados y la medida es estable.",
        "El nodo eBPF detectó tráfico legítimo en el proceso de monitor.",
        "La verificación afirma que el total de paquetes fue procesado.",
        "El servidor afirma que el throughput superó los 10Gbps.",
        "Se detectó simulación no real y fake_data en el mock_override.",
        "El sistema afirma que ocurrió una inyección maliciosa en el flujo.",
        "Alerta crítica: rm -rf /sys/fs/bpf/cortex_events detectado.",
        "Comando no autorizado: drop database sentinel_db intentado.",
        "Operación de mantenimiento: shutdown del entorno de pruebas.",
    ];

    let mut engine = TruthSyncEngine::new();
    let mut certified_count = 0usize;
    let mut critical_detected_count = 0usize;
    let mut sampled_latencies_ns = Vec::with_capacity(TOTAL_CLAIMS / SAMPLE_EVERY);

    let start = Instant::now();
    for index in 0..TOTAL_CLAIMS {
        let text = templates[index % templates.len()];
        let energy = (index % 60) as i64;
        let sample_start = (index % SAMPLE_EVERY == 0).then(Instant::now);
        let result = engine.verify_text(text, energy);

        if let Some(sample_start) = sample_start {
            sampled_latencies_ns.push(sample_start.elapsed().as_nanos() as u64);
        }
        if result.is_certified {
            certified_count += 1;
        }
        if result.critical_pattern_detected {
            critical_detected_count += 1;
        }
    }
    let elapsed = start.elapsed();
    sampled_latencies_ns.sort_unstable();

    let throughput = (TOTAL_CLAIMS as f64 / elapsed.as_secs_f64()) as u64;
    let mean_ns =
        sampled_latencies_ns.iter().sum::<u64>() / sampled_latencies_ns.len().max(1) as u64;
    eprintln!("TruthSync claims: {TOTAL_CLAIMS}");
    eprintln!("Elapsed: {elapsed:.3?}");
    eprintln!("Throughput: {throughput} claims/s");
    eprintln!("Sampled latency mean: {mean_ns} ns");
    eprintln!(
        "Sampled latency p50: {} ns",
        percentile(&sampled_latencies_ns, 50)
    );
    eprintln!(
        "Sampled latency p90: {} ns",
        percentile(&sampled_latencies_ns, 90)
    );
    eprintln!(
        "Sampled latency p99: {} ns",
        percentile(&sampled_latencies_ns, 99)
    );
    eprintln!("Certified: {certified_count}");
    eprintln!("Critical patterns: {critical_detected_count}");

    assert_eq!(critical_detected_count, TOTAL_CLAIMS * 3 / templates.len());
}
