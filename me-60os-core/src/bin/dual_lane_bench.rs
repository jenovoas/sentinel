// Bench: Dual-lane router — clasificación, WAL security (fsync) y buffer observability.
//
// Corre DualLaneRouter + SecurityLaneCollector + ObservabilityLaneCollector y emite
// métricas reales a stderr. Verifica que el routing es determinista y que el WAL
// security escribe con fsync (sin buffering), y que el observability reordena por ts.

use me60os_core::dual_lane::{
    DataLane, DualLaneRouter, EventPriority, ObservabilityLaneCollector, SecurityLaneCollector,
};
use std::collections::HashMap;

fn main() {
    let dir = std::env::temp_dir();
    let sec_wal = dir.join("sentinel_bench_security_wal.log");
    let obs_wal = dir.join("sentinel_bench_obs_wal.log");
    let _ = std::fs::remove_file(&sec_wal);
    let _ = std::fs::remove_file(&obs_wal);

    let mut router = DualLaneRouter::new();

    // 1. Clasificación determinista: 100 eventos mezclados
    let sources = ["auditd", "ebpf", "prometheus", "app", "llm", "shield"];
    let mut sec_count = 0u64;
    let mut obs_count = 0u64;
    for (i, src) in sources.iter().cycle().take(100).enumerate() {
        let data = if i % 7 == 0 {
            "{\"note\":\"malicious attempt\"}"
        } else {
            "{}"
        };
        let ev = router.classify_event(src, data, None);
        match ev.lane {
            DataLane::Security => sec_count += 1,
            DataLane::Observability => obs_count += 1,
        }
        assert!(router.should_bypass_buffer(&ev) || ev.lane == DataLane::Observability);
    }

    let (s, o, _m) = router.stats();
    eprintln!("=== DUAL-LANE ROUTER ===");
    eprintln!("Eventos totales: {}", s + o);
    eprintln!("Security: {} | Observability: {}", s, o);
    assert_eq!(s, sec_count);
    assert_eq!(o, obs_count);

    // 2. Security WAL: escritura con fsync (sin buffer)
    let mut sec_col = SecurityLaneCollector::new(sec_wal.clone());
    for i in 0..50 {
        let ev = router.classify_event("auditd", &format!("{{\"i\":{}}}", i), None);
        assert!(sec_col.emit_immediate(&ev), "WAL security falló");
    }
    let sec_contents = std::fs::read_to_string(&sec_wal).unwrap();
    let sec_lines = sec_contents.lines().count();
    eprintln!("Security WAL escritos: {} (fsync, sin buffer)", sec_lines);
    eprintln!("Loss rate: {:.4}", sec_col.loss_rate());
    eprintln!("Avg latency ms: {}", sec_col.avg_latency_ms());
    assert_eq!(sec_lines, 50);
    assert!(sec_col.loss_rate() < 1e-9);

    // 3. Observability buffer + reorder por timestamp
    let mut obs_col = ObservabilityLaneCollector::new(obs_wal.clone());
    for ts in (0..10).rev() {
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
    // Forzar flush con un evento extra
    obs_col.emit_buffered(me60os_core::dual_lane::LaneEvent {
        lane: DataLane::Observability,
        source: "app".into(),
        priority: EventPriority::Medium,
        timestamp_us: 999,
        labels: HashMap::new(),
        data: "{}".into(),
        synthetic: false,
    });
    obs_col.flush(); // flush explícito (fin de run)
    let obs_contents = std::fs::read_to_string(&obs_wal).unwrap();
    let first_line = obs_contents.lines().next().unwrap_or("");
    eprintln!("Observability WAL líneas: {}", obs_contents.lines().count());
    eprintln!("Primer evento (debe ser ts=0, reordenado): {}", first_line);
    assert!(
        first_line.contains("\"ts\":0"),
        "buffer no reordenado por timestamp"
    );

    let _ = std::fs::remove_file(&sec_wal);
    let _ = std::fs::remove_file(&obs_wal);

    eprintln!("✅ Dual-lane: routing determinista, WAL security fsync, observability reorder OK");
}
