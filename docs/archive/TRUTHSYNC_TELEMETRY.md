# ⏱️ TruthSync - Real-Time Telemetry & Performance Profiling

**Goal**: Measure everything, optimize hardware, refine in production  
**Stack**: Rust metrics + Prometheus + Grafana  
**Granularity**: Microsecond-level timing

---

## 📊 What We Measure

```
VERIFICATION PIPELINE:
├─ Claim extraction: timing, throughput
├─ Pattern matching: latency, cache hits
├─ Trust scoring: lookup time, cache misses
├─ ML inference: when triggered, duration
├─ Network filtering: DNS/HTTP latency
└─ End-to-end: total verification time

SYSTEM METRICS:
├─ CPU usage per core
├─ Memory allocation/deallocation
├─ Cache hit rates
├─ Network I/O
└─ Disk I/O

BUSINESS METRICS:
├─ Claims verified/second
├─ Accuracy rate
├─ False positives/negatives
├─ User feedback
└─ Learning improvements
```

---

## ⚡ Rust Instrumentation

### High-Precision Timing

```rust
// truthsync-core/src/metrics.rs

use std::time::Instant;
use prometheus::{Histogram, Counter, Gauge};

lazy_static! {
    // Histograms (microsecond precision)
    static ref CLAIM_EXTRACTION_DURATION: Histogram = 
        Histogram::with_opts(
            HistogramOpts::new(
                "claim_extraction_duration_microseconds",
                "Time to extract claims"
            ).buckets(vec![10.0, 50.0, 100.0, 500.0, 1000.0])
        ).unwrap();
    
    static ref PATTERN_MATCH_DURATION: Histogram = 
        Histogram::with_opts(
            HistogramOpts::new(
                "pattern_match_duration_microseconds",
                "Time to match patterns"
            ).buckets(vec![1.0, 5.0, 10.0, 50.0, 100.0])
        ).unwrap();
    
    static ref TRUST_SCORE_DURATION: Histogram = 
        Histogram::with_opts(
            HistogramOpts::new(
                "trust_score_duration_microseconds",
                "Time to score trust"
            ).buckets(vec![1.0, 5.0, 10.0, 50.0])
        ).unwrap();
    
    // Counters
    static ref CLAIMS_VERIFIED: Counter = 
        Counter::new("claims_verified_total", "Total claims verified").unwrap();
    
    static ref CACHE_HITS: Counter = 
        Counter::new("cache_hits_total", "Cache hits").unwrap();
    
    static ref CACHE_MISSES: Counter = 
        Counter::new("cache_misses_total", "Cache misses").unwrap();
    
    // Gauges
    static ref ACTIVE_VERIFICATIONS: Gauge = 
        Gauge::new("active_verifications", "Currently processing").unwrap();
}

pub struct MetricsCollector;

impl MetricsCollector {
    /// Time a function with microsecond precision
    pub fn time<F, R>(histogram: &Histogram, f: F) -> R
    where
        F: FnOnce() -> R,
    {
        let start = Instant::now();
        let result = f();
        let duration = start.elapsed();
        
        // Record in microseconds
        histogram.observe(duration.as_micros() as f64);
        
        result
    }
}
```

### Instrumented Code

```rust
// truthsync-core/src/claim_extractor.rs

impl ClaimExtractor {
    pub fn extract(&self, text: &str) -> Vec<Claim> {
        // Increment active verifications
        ACTIVE_VERIFICATIONS.inc();
        
        // Time the extraction
        let claims = MetricsCollector::time(&CLAIM_EXTRACTION_DURATION, || {
            text.split(&['.', '!', '?'][..])
                .par_iter()
                .filter_map(|s| self.extract_claim(s))
                .collect()
        });
        
        // Record results
        CLAIMS_VERIFIED.inc_by(claims.len() as f64);
        ACTIVE_VERIFICATIONS.dec();
        
        claims
    }
    
    fn extract_claim(&self, sentence: &str) -> Option<Claim> {
        // Check cache first
        if let Some(cached) = self.cache.get(sentence) {
            CACHE_HITS.inc();
            return Some(cached.clone());
        }
        
        CACHE_MISSES.inc();
        
        // Extract claim...
        let claim = self.do_extract(sentence)?;
        
        // Cache result
        self.cache.insert(sentence.to_string(), claim.clone());
        
        Some(claim)
    }
}
```

---

## 📈 Prometheus Integration

### Metrics Endpoint

```rust
// truthsync-core/src/server.rs

use actix_web::{web, App, HttpServer};
use prometheus::{Encoder, TextEncoder};

async fn metrics_handler() -> String {
    let encoder = TextEncoder::new();
    let metric_families = prometheus::gather();
    
    let mut buffer = vec![];
    encoder.encode(&metric_families, &mut buffer).unwrap();
    
    String::from_utf8(buffer).unwrap()
}

#[actix_web::main]
async fn start_metrics_server() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/metrics", web::get().to(metrics_handler))
    })
    .bind("0.0.0.0:9090")?
    .run()
    .await
}
```

### Prometheus Config

```yaml
# prometheus.yml

global:
  scrape_interval: 1s  # High frequency for real-time

scrape_configs:
  - job_name: 'truthsync'
    static_configs:
      - targets: ['truthsync:9090']
    
    # Relabel for better organization
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'truthsync-core'
```

---

## 📊 Grafana Dashboards

### Real-Time Performance Dashboard

```json
{
  "dashboard": {
    "title": "TruthSync - Real-Time Performance",
    "panels": [
      {
        "title": "Verification Latency (μs)",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, claim_extraction_duration_microseconds)",
            "legendFormat": "p50 - Claim Extraction"
          },
          {
            "expr": "histogram_quantile(0.95, claim_extraction_duration_microseconds)",
            "legendFormat": "p95 - Claim Extraction"
          },
          {
            "expr": "histogram_quantile(0.99, claim_extraction_duration_microseconds)",
            "legendFormat": "p99 - Claim Extraction"
          }
        ]
      },
      {
        "title": "Throughput (claims/sec)",
        "targets": [
          {
            "expr": "rate(claims_verified_total[1m])",
            "legendFormat": "Claims/sec"
          }
        ]
      },
      {
        "title": "Cache Performance",
        "targets": [
          {
            "expr": "rate(cache_hits_total[1m]) / (rate(cache_hits_total[1m]) + rate(cache_misses_total[1m]))",
            "legendFormat": "Hit Rate %"
          }
        ]
      }
    ]
  }
}
```

---

## 🔬 Profiling Tools

### CPU Profiling

```rust
// Enable CPU profiling
use pprof::ProfilerGuard;

#[cfg(feature = "profiling")]
pub fn start_profiling() -> ProfilerGuard<'static> {
    ProfilerGuard::new(100).unwrap()  // 100 Hz sampling
}

#[cfg(feature = "profiling")]
pub fn stop_profiling(guard: ProfilerGuard) {
    if let Ok(report) = guard.report().build() {
        let file = std::fs::File::create("flamegraph.svg").unwrap();
        report.flamegraph(file).unwrap();
    }
}
```

### Memory Profiling

```rust
use jemalloc_ctl::{stats, epoch};

pub fn print_memory_stats() {
    // Refresh stats
    epoch::mib().unwrap().advance().unwrap();
    
    let allocated = stats::allocated::mib().unwrap().read().unwrap();
    let resident = stats::resident::mib().unwrap().read().unwrap();
    
    println!("Allocated: {} MB", allocated / 1024 / 1024);
    println!("Resident: {} MB", resident / 1024 / 1024);
}
```

---

## 🎯 Hardware Optimization Guide

### Benchmarking Different Hardware

```rust
// truthsync-core/benches/hardware_bench.rs

use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_claim_extraction(c: &mut Criterion) {
    let extractor = ClaimExtractor::new();
    let text = load_test_text();
    
    c.bench_function("claim_extraction", |b| {
        b.iter(|| extractor.extract(black_box(&text)))
    });
}

criterion_group!(benches, benchmark_claim_extraction);
criterion_main!(benches);
```

### Hardware Recommendations

```
BASED ON METRICS:

If avg latency > 100μs:
├─ CPU: Upgrade to higher clock speed
├─ RAM: Increase for larger cache
└─ Action: Profile to find bottleneck

If cache hit rate < 80%:
├─ RAM: Increase cache size
├─ Algorithm: Improve cache eviction
└─ Action: Analyze access patterns

If throughput < 10,000/sec:
├─ CPU: More cores for parallelism
├─ Network: Faster NIC for DNS/HTTP
└─ Action: Horizontal scaling

If memory usage > 1GB:
├─ Algorithm: Optimize data structures
├─ Cache: Reduce cache size
└─ Action: Memory profiling
```

---

## 📡 Real-Time Monitoring

### Alerts

```yaml
# alertmanager.yml

groups:
  - name: truthsync
    interval: 10s
    rules:
      # Latency alert
      - alert: HighLatency
        expr: histogram_quantile(0.95, claim_extraction_duration_microseconds) > 500
        for: 1m
        annotations:
          summary: "Verification latency too high"
          description: "p95 latency is {{ $value }}μs (threshold: 500μs)"
      
      # Throughput alert
      - alert: LowThroughput
        expr: rate(claims_verified_total[1m]) < 1000
        for: 5m
        annotations:
          summary: "Throughput below target"
          description: "Only {{ $value }} claims/sec (target: 1000+)"
      
      # Cache alert
      - alert: LowCacheHitRate
        expr: rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.8
        for: 10m
        annotations:
          summary: "Cache hit rate too low"
          description: "Hit rate is {{ $value }}% (target: 80%+)"
```

---

## 🔧 Auto-Tuning

### Dynamic Configuration

```rust
// truthsync-core/src/auto_tune.rs

pub struct AutoTuner {
    metrics: MetricsCollector,
    config: Arc<RwLock<Config>>,
}

impl AutoTuner {
    /// Adjust configuration based on metrics
    pub async fn tune(&self) {
        let avg_latency = self.metrics.get_avg_latency().await;
        let cache_hit_rate = self.metrics.get_cache_hit_rate().await;
        let throughput = self.metrics.get_throughput().await;
        
        let mut config = self.config.write().await;
        
        // If latency too high, reduce batch size
        if avg_latency > 100.0 {
            config.batch_size = (config.batch_size * 0.8) as usize;
            log::warn!("Reduced batch size to {}", config.batch_size);
        }
        
        // If cache hit rate low, increase cache size
        if cache_hit_rate < 0.8 {
            config.cache_size = (config.cache_size as f64 * 1.2) as usize;
            log::warn!("Increased cache size to {}", config.cache_size);
        }
        
        // If throughput low, increase parallelism
        if throughput < 1000.0 {
            config.num_threads += 1;
            log::warn!("Increased threads to {}", config.num_threads);
        }
    }
}
```

---

## 📊 Example Metrics Output

```
# HELP claim_extraction_duration_microseconds Time to extract claims
# TYPE claim_extraction_duration_microseconds histogram
claim_extraction_duration_microseconds_bucket{le="10"} 1234
claim_extraction_duration_microseconds_bucket{le="50"} 5678
claim_extraction_duration_microseconds_bucket{le="100"} 8901
claim_extraction_duration_microseconds_bucket{le="500"} 9234
claim_extraction_duration_microseconds_bucket{le="1000"} 9567
claim_extraction_duration_microseconds_sum 456789.0
claim_extraction_duration_microseconds_count 9567

# HELP claims_verified_total Total claims verified
# TYPE claims_verified_total counter
claims_verified_total 123456

# HELP cache_hits_total Cache hits
# TYPE cache_hits_total counter
cache_hits_total 98765

# HELP cache_misses_total Cache misses
# TYPE cache_misses_total counter
cache_misses_total 12345
```

---

## 🎯 Optimization Workflow

```
1. Deploy TruthSync with metrics
   ↓
2. Monitor real-time performance
   ├─ Latency (p50, p95, p99)
   ├─ Throughput (claims/sec)
   └─ Cache hit rate
   ↓
3. Identify bottlenecks
   ├─ CPU-bound? → More cores
   ├─ Memory-bound? → More RAM
   ├─ I/O-bound? → Faster disk/network
   └─ Cache-bound? → Larger cache
   ↓
4. Apply optimizations
   ├─ Hardware upgrades
   ├─ Algorithm improvements
   └─ Configuration tuning
   ↓
5. Measure improvements
   ├─ Compare before/after metrics
   └─ Validate with A/B testing
   ↓
6. Repeat until targets met
   ✅ Latency < 100μs
   ✅ Throughput > 10,000/sec
   ✅ Cache hit rate > 80%
```

---

**Result**: Real-time telemetry → Data-driven optimization → Perfect hardware sizing 📊⚡
