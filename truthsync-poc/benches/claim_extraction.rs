use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use truthsync_core::ClaimExtractor;

fn benchmark_single_claim(c: &mut Criterion) {
    let extractor = ClaimExtractor::new();
    
    let test_text = "The unemployment rate is 3.5% according to the Bureau of Labor Statistics. \
                     This represents a significant improvement from last year. \
                     I think the economy is doing well overall. \
                     Tesla announced a new electric vehicle priced at $25,000. \
                     The stock market was up 2% today on positive economic news. \
                     Climate change is affecting weather patterns globally. \
                     Many experts believe we need immediate action. \
                     The new policy will take effect next month.";
    
    c.bench_function("single_claim_extraction", |b| {
        b.iter(|| {
            extractor.extract(black_box(test_text))
        });
    });
}

fn benchmark_batch_processing(c: &mut Criterion) {
    let extractor = ClaimExtractor::new();
    
    let test_text = "The unemployment rate is 3.5% according to the Bureau of Labor Statistics. \
                     Tesla announced a new electric vehicle priced at $25,000. \
                     The stock market was up 2% today on positive economic news.";
    
    let mut group = c.benchmark_group("batch_processing");
    
    for size in [10, 100, 1000].iter() {
        let batch: Vec<&str> = vec![test_text; *size];
        
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, _| {
            b.iter(|| {
                extractor.extract_batch(black_box(&batch))
            });
        });
    }
    
    group.finish();
}

criterion_group!(benches, benchmark_single_claim, benchmark_batch_processing);
criterion_main!(benches);
