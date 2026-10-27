// Bench: Dual-lane router completo — clasificación, WAL security (fsync), buffer observability,
// percentiles (p50, p90, p99), throughput y gráficos ASCII de distribución.

use me60os_core::dual_lane::{
    DataLane, DualLaneRouter, EventPriority, ObservabilityLaneCollector, SecurityLaneCollector,
};
use std::collections::HashMap;
use std::time::Instant;

fn render_ascii_histogram(title: &str, data: &[u64], unit: &str) {
    if data.is_empty() {
        return;
    }
    eprintln!("\n┌─────────────────────────────────────────────────────────────┐");
    eprintln!("│ {:<59} │", title);
    eprintln!("└─────────────────────────────────────────────────────────────┘");

    let min = *data.iter().min().unwrap();
    let max = *data.iter().max().unwrap();

    if min == max {
        eprintln!("Todos los valores son idénticos: {min} {unit}");
        return;
    }

    let num_bins = 8;
    let range = (max - min) as f64;
    let bin_size = (range / num_bins as f64).max(1.0);

    let mut counts = vec![0usize; num_bins];
    for &val in data {
        let bin = (((val - min) as f64 / bin_size) as usize).min(num_bins - 1);
        counts[bin] += 1;
    }

    let max_count = *counts.iter().max().unwrap_or(&1).max(&1);
    let bar_width = 32;

    for (i, &count) in counts.iter().enumerate() {
        let b_start = min as f64 + i as f64 * bin_size;
        let b_end = b_start + bin_size;
        let filled = (count * bar_width) / max_count;
        let bar: String = "█".repeat(filled);
        eprintln!(
            "[{:6.1} - {:6.1} {}] ({:5}) |{:<32}|",
            b_start, b_end, unit, count, bar
        );
    }
}

fn percentile(sorted: &[u64], pct: f64) -> u64 {
    if sorted.is_empty() {
        return 0;
    }
    let idx = ((sorted.len() as f64 * pct / 100.0).round() as usize).min(sorted.len() - 1);
    sorted[idx]
}

fn main() {
    let dir = std::env::temp_dir();
    let sec_wal = dir.join("sentinel_bench_security_wal.log");
    let obs_wal = dir.join("sentinel_bench_obs_wal.log");
    let _ = std::fs::remove_file(&sec_wal);
    let _ = std::fs::remove_file(&obs_wal);

    eprintln!("===============================================================");
    eprintln!("         BENCHMARK COMPLETO DUAL-LANE (ROUTER + WAL)           ");
    eprintln!("===============================================================");

    // ─────────────────────────────────────────────────────────────────────────
    // 1. Benchmark de clasificación de eventos de alto rendimiento (10.000 evs)
    // ─────────────────────────────────────────────────────────────────────────
    let mut router = DualLaneRouter::new();
    let sources = ["auditd", "ebpf", "prometheus", "app", "llm", "shield"];
    let iterations = 10_000usize;
    let mut latencies_ns = Vec::with_capacity(iterations);

    let t0 = Instant::now();
    for i in 0..iterations {
        let src = sources[i % sources.len()];
        let data = if i % 7 == 0 {
            "{\"note\":\"malicious attempt detected\"}"
        } else {
            "{\"status\":\"ok\",\"metric\":42}"
        };

        let start = Instant::now();
        let ev = router.classify_event(src, data, None);
        let elapsed_ns = start.elapsed().as_nanos() as u64;
        latencies_ns.push(elapsed_ns);

        assert!(router.should_bypass_buffer(&ev) || ev.lane == DataLane::Observability);
    }
    let total_routing_duration = t0.elapsed();

    let mut sorted_latencies = latencies_ns.clone();
    sorted_latencies.sort_unstable();

    let p50 = percentile(&sorted_latencies, 50.0);
    let p90 = percentile(&sorted_latencies, 90.0);
    let p95 = percentile(&sorted_latencies, 95.0);
    let p99 = percentile(&sorted_latencies, 99.0);
    let max = *sorted_latencies.last().unwrap_or(&0);
    let avg = sorted_latencies.iter().sum::<u64>() / sorted_latencies.len().max(1) as u64;
    let throughput = (iterations as f64 / total_routing_duration.as_secs_f64()) as u64;

    let (s, o, _m) = router.stats();
    eprintln!("\n📊 1. CLASIFICACIÓN DE EVENTOS (ROUTER):");
    eprintln!("   Total eventos evaluados : {}", iterations);
    eprintln!(
        "   Distribución de lanes   : Security = {} | Observability = {}",
        s, o
    );
    eprintln!(
        "   Tiempo total            : {:.2?}",
        total_routing_duration
    );
    eprintln!("   Throughput              : {} ev/s", throughput);
    eprintln!("   Latencia media          : {} ns", avg);
    eprintln!("   Percentil p50 (mediana) : {} ns", p50);
    eprintln!("   Percentil p90           : {} ns", p90);
    eprintln!("   Percentil p95           : {} ns", p95);
    eprintln!("   Percentil p99           : {} ns", p99);
    eprintln!("   Latencia máx            : {} ns", max);

    // Convertir a µs para el histograma
    let latencies_us: Vec<u64> = latencies_ns.iter().map(|&ns| ns / 1000).collect();
    render_ascii_histogram(
        "Histograma de Latencia de Clasificación",
        &latencies_us,
        "µs",
    );

    // ─────────────────────────────────────────────────────────────────────────
    // 2. Benchmark de Security WAL (fsync sincrónico en disco)
    // ─────────────────────────────────────────────────────────────────────────
    let wal_iterations = 200usize;
    let mut sec_col = SecurityLaneCollector::new(sec_wal.clone());
    let mut wal_latencies_us = Vec::with_capacity(wal_iterations);

    let t_wal_start = Instant::now();
    for i in 0..wal_iterations {
        let ev = router.classify_event("auditd", &format!("{{\"sec_event_index\":{}}}", i), None);
        let w0 = Instant::now();
        let ok = sec_col.emit_immediate(&ev);
        let w_elapsed_us = w0.elapsed().as_micros() as u64;
        wal_latencies_us.push(w_elapsed_us);
        assert!(ok, "WAL security emit falló");
    }
    let total_wal_duration = t_wal_start.elapsed();

    let sec_contents = std::fs::read_to_string(&sec_wal).unwrap();
    let sec_lines = sec_contents.lines().count();
    assert_eq!(sec_lines, wal_iterations);
    assert!(sec_col.loss_rate() < 1e-9);

    let mut sorted_wal = wal_latencies_us.clone();
    sorted_wal.sort_unstable();

    let wal_p50 = percentile(&sorted_wal, 50.0);
    let wal_p90 = percentile(&sorted_wal, 90.0);
    let wal_p99 = percentile(&sorted_wal, 99.0);
    let wal_avg = sorted_wal.iter().sum::<u64>() / sorted_wal.len().max(1) as u64;

    eprintln!("\n🔒 2. SECURITY LANE WAL (FSYNC REAL SIN BUFFER):");
    eprintln!("   Registros escritos      : {} líneas", sec_lines);
    eprintln!("   Tiempo total fsync      : {:.2?}", total_wal_duration);
    eprintln!(
        "   Tasa de pérdida         : {:.4} (0.0% estricto)",
        sec_col.loss_rate()
    );
    eprintln!("   Latencia media          : {} µs", wal_avg);
    eprintln!("   Percentil p50           : {} µs", wal_p50);
    eprintln!("   Percentil p90           : {} µs", wal_p90);
    eprintln!("   Percentil p99           : {} µs", wal_p99);

    render_ascii_histogram(
        "Histograma de Latencia fsync Security WAL",
        &sorted_wal,
        "µs",
    );

    // ─────────────────────────────────────────────────────────────────────────
    // 3. Observability buffer + reordenamiento cronológico por timestamp
    // ─────────────────────────────────────────────────────────────────────────
    let mut obs_col = ObservabilityLaneCollector::new(obs_wal.clone());
    for ts in (0..50).rev() {
        obs_col.emit_buffered(me60os_core::dual_lane::LaneEvent {
            lane: DataLane::Observability,
            source: "app".into(),
            priority: EventPriority::Medium,
            timestamp_us: ts,
            labels: HashMap::new(),
            data: format!("{{\"ts\":{}}}", ts),
            synthetic: false,
        });
    }
    obs_col.flush();

    let obs_contents = std::fs::read_to_string(&obs_wal).unwrap();
    let obs_lines: Vec<&str> = obs_contents.lines().collect();
    eprintln!("\n📈 3. OBSERVABILITY LANE (BUFFER CON REORDENAMIENTO TEMPORAL):");
    eprintln!("   Líneas en log buffer    : {}", obs_lines.len());
    assert_eq!(obs_lines.len(), 50);

    let first = obs_lines.first().unwrap();
    let last = obs_lines.last().unwrap();
    eprintln!("   Primer registro reordenado: {}", first);
    eprintln!("   Último registro reordenado: {}", last);
    assert!(first.contains("\"ts\":0"), "El primer evento debe ser ts=0");
    assert!(
        last.contains("\"ts\":49"),
        "El último evento debe ser ts=49"
    );

    let _ = std::fs::remove_file(&sec_wal);
    let _ = std::fs::remove_file(&obs_wal);

    eprintln!("\n===============================================================");
    eprintln!("   ✅ BENCHMARK DUAL-LANE COMPLETADO EXITOSAMENTE AL 100%       ");
    eprintln!("===============================================================");
}
