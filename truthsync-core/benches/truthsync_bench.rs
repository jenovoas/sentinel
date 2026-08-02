use criterion::{black_box, criterion_group, criterion_main, Criterion};
use truthsync_core::{ClaimExtractor, TruthSyncEngine};

fn bench_claim_extract_short(c: &mut Criterion) {
    let extractor = ClaimExtractor::new();
    let text = "El kernel fue actualizado correctamente. La temperatura es de 36 grados. Hace buen día.";
    c.bench_function("claim_extract_short", |b| {
        b.iter(|| extractor.extract(black_box(text)))
    });
}

fn bench_claim_extract_long(c: &mut Criterion) {
    let extractor = ClaimExtractor::new();
    let text = [
        "El kernel fue actualizado correctamente.",
        "La temperatura reporta 36 grados centígrados.",
        "El nodo eBPF detectó una anomalía en el proceso.",
        "El total de latencia fue de 2.4ms.",
        "Hace buen día y el cielo está despejado.",
        "El sistema afirma que todos los checks pasaron.",
        "La medida de throughput es de 10Gbps.",
        "El servidor es el principal punto de acceso.",
        "No hay evidencia de inyección maliciosa.",
        "Los logs demuestran que el kernel inició sin errores.",
    ]
    .join(" ");
    c.bench_function("claim_extract_long", |b| {
        b.iter(|| extractor.extract(black_box(&text)))
    });
}

fn bench_verify_clean(c: &mut Criterion) {
    let mut engine = TruthSyncEngine::new();
    let text = "El kernel fue actualizado. La temperatura es de 36 grados. El nodo reporta OK.";
    c.bench_function("verify_clean", |b| {
        b.iter(|| engine.verify_text(black_box(text), black_box(42)))
    });
}

fn bench_verify_malicious(c: &mut Criterion) {
    let mut engine = TruthSyncEngine::new();
    let text = "El kernel fue actualizado con fake_data y mock_override. simulación no real detectada.";
    c.bench_function("verify_malicious", |b| {
        b.iter(|| engine.verify_text(black_box(text), black_box(42)))
    });
}

fn bench_verify_heavy(c: &mut Criterion) {
    let mut engine = TruthSyncEngine::new();
    let text = [
        "El kernel fue actualizado correctamente.",
        "La temperatura reporta 36 grados centígrados.",
        "El nodo eBPF detectó una anomalía en el proceso.",
        "El total de latencia fue de 2.4ms.",
        "Hace buen día y el cielo está despejado.",
        "El sistema afirma que todos los checks pasaron.",
        "La medida de throughput es de 10Gbps.",
        "El servidor es el principal punto de acceso.",
        "No hay evidencia de inyección maliciosa.",
        "Los logs demuestran que el kernel inició sin errores.",
        "Se detectó fake_data en el mock_override del sistema.",
        "La simulación no real fue desbloqueo no autorizado.",
    ]
    .join(" ");
    c.bench_function("verify_heavy", |b| {
        b.iter(|| engine.verify_text(black_box(&text), black_box(42)))
    });
}

fn bench_verify_cached(c: &mut Criterion) {
    // MEJORA #3: benchmark cache hit performance
    let mut engine = TruthSyncEngine::new();
    let text = "texto repetido para cache";
    // Warm cache
    engine.verify_text(text, 42);
    c.bench_function("verify_cached", |b| {
        b.iter(|| engine.verify_text(black_box(text), black_box(42)))
    });
}

criterion_group!(
    benches,
    bench_claim_extract_short,
    bench_claim_extract_long,
    bench_verify_clean,
    bench_verify_malicious,
    bench_verify_heavy,
    bench_verify_cached,
);
criterion_main!(benches);