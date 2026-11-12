use std::collections::HashSet;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::time::Instant;
use truthsync_core::TruthSyncEngine;

fn percentile(sorted: &[u64], percentile_basis_points: u32) -> u64 {
    if sorted.is_empty() {
        return 0;
    }
    let numerator = (sorted.len() as u128) * u128::from(percentile_basis_points);
    let index = usize::try_from((numerator + 5_000) / 10_000)
        .unwrap_or(usize::MAX)
        .min(sorted.len() - 1);
    sorted[index]
}

fn format_hundredths(numerator: u128, denominator: u128) -> String {
    let scaled = (numerator * 100 + denominator / 2) / denominator;
    format!("{}.{:02}", scaled / 100, scaled % 100)
}

fn claims_per_second(claims: usize, elapsed: std::time::Duration) -> u64 {
    let nanos = elapsed.as_nanos().max(1);
    u64::try_from((claims as u128 * 1_000_000_000) / nanos).unwrap_or(u64::MAX)
}

fn load_unique_claims(
    path: &str,
) -> Result<(usize, usize, Vec<String>), Box<dyn std::error::Error>> {
    let reader = BufReader::new(File::open(path)?);
    let mut rows = 0usize;
    let mut seen = HashSet::new();
    let mut claims = Vec::new();

    for line in reader.lines() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        rows += 1;
        let record: serde_json::Value = serde_json::from_str(&line)?;
        let Some(claim) = record
            .get("claim_reviewed")
            .and_then(serde_json::Value::as_str)
        else {
            continue;
        };
        let claim = claim.trim();
        if claim.is_empty() {
            continue;
        }
        let normalized = claim
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ")
            .to_lowercase();
        if seen.insert(normalized) {
            claims.push(claim.to_owned());
        }
    }
    Ok((rows, seen.len(), claims))
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args()
        .nth(1)
        .ok_or("uso: truthsync_dataset_bench <claims.jsonl>")?;
    let (rows, unique_count, claims) = load_unique_claims(&path)?;
    if claims.is_empty() {
        return Err("el archivo no contiene textos claim_reviewed utilizables".into());
    }

    let mut engine = TruthSyncEngine::new();
    let mut latencies_ns = Vec::with_capacity(claims.len() / 10 + 1);
    let mut critical_count = 0usize;
    let start = Instant::now();
    for (index, claim) in claims.iter().enumerate() {
        let sample = index % 10 == 0;
        let before = sample.then(Instant::now);
        let result = engine.verify_text(claim, (index % 60) as i64);
        critical_count += usize::from(result.critical_pattern_detected);
        if let Some(before) = before {
            latencies_ns.push(before.elapsed().as_nanos() as u64);
        }
    }
    let elapsed = start.elapsed();
    latencies_ns.sort_unstable();

    println!("Fuente: {path}");
    println!("Filas JSONL: {rows}");
    println!("Afirmaciones únicas normalizadas: {unique_count}");
    println!("Afirmaciones procesadas: {}", claims.len());
    println!("Tiempo total: {:.3?}", elapsed);
    println!(
        "Rendimiento: {} afirmaciones/s",
        claims_per_second(claims.len(), elapsed)
    );
    println!(
        "Latencia muestreada (n={}): media {} µs, p50 {} µs, p95 {} µs, p99 {} µs",
        latencies_ns.len(),
        format_hundredths(
            u128::from(latencies_ns.iter().sum::<u64>()),
            (latencies_ns.len().max(1) as u128) * 1_000,
        ),
        format_hundredths(u128::from(percentile(&latencies_ns, 5_000)), 1_000),
        format_hundredths(u128::from(percentile(&latencies_ns, 9_500)), 1_000),
        format_hundredths(u128::from(percentile(&latencies_ns, 9_900)), 1_000),
    );
    println!("Patrones críticos encontrados: {critical_count}");
    Ok(())
}
