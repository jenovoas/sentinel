// Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
#![forbid(clippy::float_arithmetic)]
#![forbid(clippy::float_cmp)]
#![forbid(clippy::cast_possible_truncation)]
#![forbid(clippy::cast_precision_loss)]
//
// SENTINEL-VERIFIER — Verificador automatizado de invariantes del stack Sentinel.
//
// Corre una serie de checks sobre el estado REAL del sistema (eBPF, systemd,
// HTTP endpoints, logs) y reporta OK/FAIL/SKIP con evidencia. No interpreta.
//
// Uso:
//   sentinel-verifier                # human-readable
//   sentinel-verifier --json         # salida JSON (para dashboards)
//   sentinel-verifier --watch 30     # re-verifica cada 30s

use anyhow::{Context, Result};
use serde::Serialize;
use std::process::Command;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
enum Status {
    Ok,
    Fail,
    Skip,
}

#[derive(Debug, Serialize)]
struct CheckResult {
    id: &'static str,
    name: &'static str,
    status: Status,
    evidence: String,
    detail: Option<String>,
}

impl CheckResult {
    fn ok(id: &'static str, name: &'static str, evidence: String) -> Self {
        Self {
            id,
            name,
            status: Status::Ok,
            evidence,
            detail: None,
        }
    }
    fn fail(
        id: &'static str,
        name: &'static str,
        evidence: String,
        detail: Option<String>,
    ) -> Self {
        Self {
            id,
            name,
            status: Status::Fail,
            evidence,
            detail,
        }
    }
    fn skip(id: &'static str, name: &'static str, reason: String) -> Self {
        Self {
            id,
            name,
            status: Status::Skip,
            evidence: reason,
            detail: None,
        }
    }
}

#[derive(Debug, Serialize)]
struct Report {
    timestamp_unix: u64,
    host: String,
    total: usize,
    ok: usize,
    fail: usize,
    skip: usize,
    results: Vec<CheckResult>,
}

fn run(cmd: &str, args: &[&str]) -> Result<String> {
    let out = Command::new(cmd)
        .args(args)
        .output()
        .with_context(|| format!("spawning {} {:?}", cmd, args))?;
    let mut buf = String::from_utf8_lossy(&out.stdout).to_string();
    if !out.stderr.is_empty() {
        if !buf.is_empty() {
            buf.push('\n');
        }
        buf.push_str(&String::from_utf8_lossy(&out.stderr));
    }
    Ok(buf)
}

fn sudo_run(args: &[&str]) -> Result<String> {
    let mut full = vec!["-n"]; // non-interactive sudo
    full.extend_from_slice(args);
    run("sudo", &full)
}

// 1. Ring-0 LSM programs presentes
fn check_lsm_progs() -> CheckResult {
    match sudo_run(&["bpftool", "prog", "show"]) {
        Ok(out) => {
            let names = [
                "guardian_execve",
                "guardian_cognitive",
                "me60os_ai_guardian_open",
            ];
            let found: Vec<&str> = names.iter().filter(|n| out.contains(*n)).copied().collect();
            if found.len() == names.len() {
                CheckResult::ok(
                    "lsm_progs",
                    "programas LSM Ring-0 cargados",
                    format!("{}/{}: {}", found.len(), names.len(), found.join(", ")),
                )
            } else {
                CheckResult::fail(
                    "lsm_progs",
                    "programas LSM Ring-0 cargados",
                    format!("solo {}/{} encontrados", found.len(), names.len()),
                    Some(format!("salida bpftool:\n{}", out)),
                )
            }
        }
        Err(e) => CheckResult::skip("lsm_progs", "programas LSM Ring-0 cargados", e.to_string()),
    }
}

// 2. Ringbuf cortex_events existe y tiene consumidores
fn check_cortex_events_ringbuf() -> CheckResult {
    match sudo_run(&["bpftool", "map", "show"]) {
        Ok(out) => {
            let mut in_cortex_block = false;
            let mut has_consumers = false;
            let mut block = String::new();
            for line in out.lines().chain(std::iter::once("")) {
                if line.contains("cortex_events") {
                    in_cortex_block = true;
                    block = line.to_string();
                } else if in_cortex_block {
                    if line.trim_start().starts_with("pids ") {
                        block.push('\n');
                        block.push_str(line);
                        if !line.trim_end().ends_with("pids") && line.contains('(') {
                            has_consumers = true;
                        }
                    } else if !line.starts_with('\t') && !line.is_empty() {
                        break;
                    }
                }
            }
            if block.is_empty() {
                CheckResult::fail(
                    "cortex_events_ringbuf",
                    "ringbuf cortex_events pinned",
                    "map cortex_events no encontrado".into(),
                    None,
                )
            } else if has_consumers {
                CheckResult::ok(
                    "cortex_events_ringbuf",
                    "ringbuf cortex_events pinned con consumidores",
                    block.trim().to_string(),
                )
            } else {
                CheckResult::fail(
                    "cortex_events_ringbuf",
                    "ringbuf cortex_events pinned",
                    "existe pero SIN consumidores adjuntos".into(),
                    Some(block),
                )
            }
        }
        Err(e) => CheckResult::skip(
            "cortex_events_ringbuf",
            "ringbuf cortex_events",
            e.to_string(),
        ),
    }
}

// 3. Pins en /sys/fs/bpf
fn check_bpf_pins() -> CheckResult {
    let expected = [
        "cortex_events",
        "guardian_alpha",
        "guardian_cognitive",
        "ai_guardian",
        "float_detector",
        "gamma_heartbeat",
    ];
    match sudo_run(&["ls", "/sys/fs/bpf/"]) {
        Ok(out) => {
            let found: Vec<&str> = expected
                .iter()
                .filter(|n| out.contains(*n))
                .copied()
                .collect();
            if found.len() == expected.len() {
                CheckResult::ok(
                    "bpf_pins",
                    "pins /sys/fs/bpf presentes",
                    format!("{}/{}", found.len(), expected.len()),
                )
            } else {
                let missing: Vec<&str> = expected
                    .iter()
                    .filter(|n| !out.contains(*n))
                    .copied()
                    .collect();
                CheckResult::fail(
                    "bpf_pins",
                    "pins /sys/fs/bpf presentes",
                    format!("faltan: {}", missing.join(", ")),
                    Some(format!("los que hay:\n{}", out)),
                )
            }
        }
        Err(e) => CheckResult::skip("bpf_pins", "pins /sys/fs/bpf", e.to_string()),
    }
}

// 4. Cortex no ha hecho core-dump en últimas 24h
fn check_cortex_no_segv() -> CheckResult {
    let out = sudo_run(&[
        "journalctl",
        "-u",
        "sentinel-cortex.service",
        "--no-pager",
        "--since",
        "24 hours ago",
        "-q",
    ]);
    match out {
        Ok(o) => {
            let segv_count = o.matches("core-dump").count()
                + o.matches("SEGV")
                    .count()
                    .saturating_sub(o.matches("core-dump").count());
            if segv_count == 0 {
                CheckResult::ok(
                    "cortex_segv",
                    "cortex sin SEGV últimas 24h",
                    "0 coredumps en journal".into(),
                )
            } else {
                CheckResult::fail(
                    "cortex_segv",
                    "cortex sin SEGV últimas 24h",
                    format!("{} menciones core-dump/SEGV", segv_count),
                    None,
                )
            }
        }
        Err(e) => CheckResult::skip("cortex_segv", "cortex SEGV check", e.to_string()),
    }
}

// 5. gamma-watchdog heartbeats en últimos 60s
fn check_watchdog_alive() -> CheckResult {
    // journal como usuario no ve logs de servicios root → usar sudo
    let out = sudo_run(&[
        "journalctl",
        "-u",
        "sentinel-gamma-watchdog.service",
        "--no-pager",
        "--since",
        "90 seconds ago",
        "-q",
    ]);
    match out {
        Ok(o) => {
            let beats = o.matches("\"alive\"").count();
            if beats >= 3 {
                CheckResult::ok(
                    "watchdog_alive",
                    "gamma-watchdog heartbeats",
                    format!("{} beats en 90s (esperado ~5 @17s)", beats),
                )
            } else {
                CheckResult::fail(
                    "watchdog_alive",
                    "gamma-watchdog heartbeats",
                    format!("solo {} beats en 90s", beats),
                    Some(format!("journal:\n{}", o)),
                )
            }
        }
        Err(e) => CheckResult::skip("watchdog_alive", "gamma-watchdog", e.to_string()),
    }
}

// 6. Endpoint /api/v1/sentinel_status reporta RING0_PINNED_ACTIVE
fn check_sentinel_status_http() -> CheckResult {
    let out = run(
        "curl",
        &[
            "-s",
            "-m",
            "5",
            "http://localhost:8000/api/v1/sentinel_status",
        ],
    );
    match out {
        Ok(o) => {
            if o.contains("RING0_PINNED_ACTIVE")
                && o.contains("WHITELIST_MAP_ENGAGED")
                && o.contains("LSM_HOOK_ACTIVE")
            {
                CheckResult::ok(
                    "sentinel_status_http",
                    "endpoint sentinel_status",
                    o.trim().to_string(),
                )
            } else {
                CheckResult::fail(
                    "sentinel_status_http",
                    "endpoint sentinel_status",
                    o.trim().to_string(),
                    Some(
                        "esperados: RING0_PINNED_ACTIVE, WHITELIST_MAP_ENGAGED, LSM_HOOK_ACTIVE"
                            .into(),
                    ),
                )
            }
        }
        Err(e) => CheckResult::skip(
            "sentinel_status_http",
            "endpoint sentinel_status",
            e.to_string(),
        ),
    }
}

// 7. /health responde 200 y JSON válido
fn check_health_http() -> CheckResult {
    let out = run(
        "curl",
        &[
            "-s",
            "-m",
            "5",
            "-o",
            "/dev/null",
            "-w",
            "%{http_code}",
            "http://localhost:8000/health",
        ],
    );
    match out {
        Ok(code) if code.trim() == "200" => CheckResult::ok(
            "health_http",
            "endpoint /health",
            format!("HTTP {}", code.trim()),
        ),
        Ok(code) => CheckResult::fail(
            "health_http",
            "endpoint /health",
            format!("HTTP {} (esperado 200)", code.trim()),
            None,
        ),
        Err(e) => CheckResult::skip("health_http", "endpoint /health", e.to_string()),
    }
}

// 8. Servicios sentinel-* activos
fn check_sentinel_services() -> CheckResult {
    let services = [
        "sentinel-cortex",
        "sentinel-gamma-watchdog",
        "sentinel-hex-daemon",
        "sentinel-pai-neural",
        "sentinel-qhc-agent",
        "sentinel-vid-agent",
        "sentinel-adm-agent",
    ];
    let mut down = Vec::new();
    let mut outputs = Vec::new();
    for s in &services {
        match run("systemctl", &["is-active", &format!("{}.service", s)]) {
            Ok(o) => {
                outputs.push(format!("{}: {}", s, o.trim()));
                if o.trim() != "active" {
                    down.push(*s);
                }
            }
            Err(e) => {
                outputs.push(format!("{}: error {}", s, e));
                down.push(*s);
            }
        }
    }
    if down.is_empty() {
        CheckResult::ok(
            "sentinel_services",
            "servicios systemd sentinel-*",
            outputs.join(" | "),
        )
    } else {
        CheckResult::fail(
            "sentinel_services",
            "servicios systemd sentinel-*",
            format!("caídos: {}", down.join(", ")),
            Some(outputs.join("\n")),
        )
    }
}

// 9. ebpf_trace.log está creciendo
fn check_ebpf_trace_growing() -> CheckResult {
    let path = "/var/log/sentinel/ebpf_trace.log";
    let mtime1 = file_mtime(path);
    std::thread::sleep(Duration::from_secs(3));
    let size1 = file_size(path);
    std::thread::sleep(Duration::from_secs(2));
    let size2 = file_size(path);

    match (mtime1, size1, size2) {
        (Some(mt), Some(s1), Some(s2)) => {
            let age = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs() as i64
                - mt as i64;
            if age < 600 {
                CheckResult::ok(
                    "ebpf_trace_log",
                    "ebpf_trace.log vivo",
                    format!("size {}→{} bytes, mtime hace {}s", s1, s2, age),
                )
            } else if s2 > s1 {
                CheckResult::ok(
                    "ebpf_trace_log",
                    "ebpf_trace.log vivo",
                    format!("creció {} bytes en 2s", s2 - s1),
                )
            } else {
                CheckResult::fail(
                    "ebpf_trace_log",
                    "ebpf_trace.log vivo",
                    format!("sin crecimiento, mtime hace {}s", age),
                    None,
                )
            }
        }
        _ => CheckResult::fail(
            "ebpf_trace_log",
            "ebpf_trace.log vivo",
            "archivo no accesible".into(),
            None,
        ),
    }
}

fn file_mtime(path: &str) -> Option<u64> {
    let md = std::fs::metadata(path).ok()?;
    let mt = md.modified().ok()?;
    Some(mt.duration_since(UNIX_EPOCH).ok()?.as_secs())
}
fn file_size(path: &str) -> Option<u64> {
    std::fs::metadata(path).ok()?.len().into()
}

// 10. retention_score sube o está en valor razonable
fn check_lattice_metrics() -> CheckResult {
    let out = run("curl", &["-s", "-m", "5", "http://localhost:8000/metrics"]);
    match out {
        Ok(o) => {
            let retention = o
                .lines()
                .find(|l| l.starts_with("sentinel_liquid_lattice_retention_score "))
                .and_then(|l| l.split_whitespace().nth(1))
                .and_then(|v| v.parse::<f64>().ok());
            let energy = o
                .lines()
                .find(|l| l.starts_with("sentinel_lattice_total_energy "))
                .and_then(|l| l.split_whitespace().nth(1))
                .and_then(|v| v.parse::<u64>().ok());
            match (retention, energy) {
                (Some(r), Some(e)) => {
                    if e == 0 {
                        CheckResult::fail(
                            "lattice_metrics",
                            "LiquidLattice métricas",
                            format!("total_energy=0 (sin eventos aún), retention={}", r),
                            None,
                        )
                    } else {
                        CheckResult::ok(
                            "lattice_metrics",
                            "LiquidLattice métricas",
                            format!("retention={:.4}, total_energy={}", r, e),
                        )
                    }
                }
                _ => CheckResult::fail(
                    "lattice_metrics",
                    "LiquidLattice métricas",
                    "métricas esperadas no encontradas en /metrics".into(),
                    None,
                ),
            }
        }
        Err(e) => CheckResult::skip("lattice_metrics", "LiquidLattice métricas", e.to_string()),
    }
}

fn run_all_checks() -> Vec<CheckResult> {
    vec![
        check_lsm_progs(),
        check_cortex_events_ringbuf(),
        check_bpf_pins(),
        check_cortex_no_segv(),
        check_watchdog_alive(),
        check_sentinel_status_http(),
        check_health_http(),
        check_sentinel_services(),
        check_ebpf_trace_growing(),
        check_lattice_metrics(),
    ]
}

fn hostname() -> String {
    run("hostname", &[])
        .unwrap_or_else(|_| "unknown".into())
        .trim()
        .to_string()
}

fn print_human(report: &Report) {
    let icon = |s: Status| match s {
        Status::Ok => "✅",
        Status::Fail => "❌",
        Status::Skip => "⚠️ ",
    };
    println!(
        "\n=== SENTINEL VERIFIER @ {} ({}) ===",
        report.host, report.timestamp_unix
    );
    println!(
        "  {} OK | {} FAIL | {} SKIP (de {})\n",
        report.ok, report.fail, report.skip, report.total
    );
    for r in &report.results {
        println!("  {} [{:>22}] {}", icon(r.status), r.id, r.name);
        println!("      → {}", r.evidence);
        if let Some(d) = &r.detail {
            for line in d.lines().take(3) {
                println!("        {}", line);
            }
        }
    }
    println!();
}

#[tokio::main]
async fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    let json_mode = args.iter().any(|a| a == "--json");
    let watch_secs: Option<u64> = args
        .iter()
        .position(|a| a == "--watch")
        .and_then(|i| args.get(i + 1))
        .and_then(|v| v.parse().ok());

    loop {
        let results = run_all_checks();
        let ok = results.iter().filter(|r| r.status == Status::Ok).count();
        let fail = results.iter().filter(|r| r.status == Status::Fail).count();
        let skip = results.iter().filter(|r| r.status == Status::Skip).count();

        let report = Report {
            timestamp_unix: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
            host: hostname(),
            total: results.len(),
            ok,
            fail,
            skip,
            results,
        };

        if json_mode {
            println!("{}", serde_json::to_string(&report)?);
        } else {
            print_human(&report);
        }

        match watch_secs {
            Some(s) => tokio::time::sleep(Duration::from_secs(s)).await,
            None => break,
        }
    }
    Ok(())
}
