# 🏗️ TruthSync - Dual-Container Architecture

**Concept**: Separation of Concerns + Predictive Caching  
**Design**: Heavy Core + Lightweight Edge  
**Goal**: <10ms latency with pre-cached responses

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DUAL-CONTAINER DESIGN                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │   CONTAINER 1: TRUTH CORE (Heavy, Isolated)        │    │
│  │   ├─ PostgreSQL (verified facts DB)                │    │
│  │   ├─ Redis (trust scores cache)                    │    │
│  │   ├─ Rust Algorithm (verification engine)          │    │
│  │   ├─ Python ML (complex inference)                 │    │
│  │   └─ Learning System (pattern detection)           │    │
│  │                                                      │    │
│  │   Role: Source of Truth                            │    │
│  │   Latency: ~50-100ms (complex verification)        │    │
│  │   Throughput: 1,000 verifications/sec              │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↕                                   │
│                    gRPC / HTTP/2                            │
│                          ↕                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │   CONTAINER 2: TRUTHSYNC EDGE (Light, Fast)       │    │
│  │   ├─ In-Memory Cache (pre-cached responses)        │    │
│  │   ├─ Predictive Engine (anticipates queries)       │    │
│  │   ├─ DNS Filter (Pi-hole style)                    │    │
│  │   ├─ HTTP Proxy (content filtering)                │    │
│  │   └─ Rust Core (microsecond lookups)               │    │
│  │                                                      │    │
│  │   Role: Fast Edge Layer                            │    │
│  │   Latency: <1ms (cache hit)                        │    │
│  │   Throughput: 100,000+ queries/sec                 │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↕                                   │
│                  [User Devices / Sentinel]                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Container 1: Truth Core (Heavy)

### Purpose
- **Source of Truth**: Authoritative verification
- **Complex Analysis**: ML inference, pattern detection
- **Learning**: Adapts from feedback
- **Isolated**: Protected, no direct user access

### Components

```yaml
# docker-compose.yml

services:
  truth-core:
    build: ./truth-core
    container_name: sentinel-truth-core
    restart: unless-stopped
    
    # Isolated network (no direct external access)
    networks:
      - truth-internal
    
    # Resource limits (heavy workload)
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
    
    environment:
      - POSTGRES_URL=postgresql://truth-db:5432/truth
      - REDIS_URL=redis://truth-redis:6379
      - ML_WORKERS=4
      - RUST_LOG=info
    
    volumes:
      - truth-models:/app/models
      - truth-data:/app/data
    
    depends_on:
      - truth-db
      - truth-redis
    
    # Internal gRPC port only
    expose:
      - "50051"  # gRPC
  
  truth-db:
    image: postgres:16-alpine
    container_name: sentinel-truth-db
    restart: unless-stopped
    
    networks:
      - truth-internal
    
    environment:
      - POSTGRES_DB=truth
      - POSTGRES_USER=truth
      - POSTGRES_PASSWORD=${TRUTH_DB_PASSWORD}
    
    volumes:
      - truth-postgres:/var/lib/postgresql/data
    
    # Optimized for writes (learning data)
    command: >
      postgres
      -c shared_buffers=2GB
      -c effective_cache_size=6GB
      -c maintenance_work_mem=512MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
  
  truth-redis:
    image: redis:7-alpine
    container_name: sentinel-truth-redis
    restart: unless-stopped
    
    networks:
      - truth-internal
    
    # Optimized for large cache
    command: >
      redis-server
      --maxmemory 4gb
      --maxmemory-policy allkeys-lru
      --save ""
      --appendonly no
    
    volumes:
      - truth-redis:/data

volumes:
  truth-postgres:
  truth-redis:
  truth-models:
  truth-data:

networks:
  truth-internal:
    driver: bridge
    internal: true  # No external access
```

### Database Schema

```sql
-- truth-core/schema.sql

-- Verified facts (source of truth)
CREATE TABLE verified_facts (
    id BIGSERIAL PRIMARY KEY,
    claim TEXT NOT NULL,
    claim_hash BYTEA NOT NULL UNIQUE,  -- Fast lookup
    trust_score REAL NOT NULL CHECK (trust_score >= 0 AND trust_score <= 100),
    sources JSONB NOT NULL,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,  -- Cache expiration
    verification_count INTEGER DEFAULT 1,
    
    -- Indexes for fast queries
    CONSTRAINT valid_trust_score CHECK (trust_score >= 0 AND trust_score <= 100)
);

CREATE INDEX idx_claim_hash ON verified_facts USING hash(claim_hash);
CREATE INDEX idx_trust_score ON verified_facts(trust_score DESC);
CREATE INDEX idx_verified_at ON verified_facts(verified_at DESC);

-- Source trust scores
CREATE TABLE source_trust (
    id BIGSERIAL PRIMARY KEY,
    source_domain TEXT NOT NULL UNIQUE,
    trust_score REAL NOT NULL,
    verification_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Computed accuracy
    accuracy REAL GENERATED ALWAYS AS (
        CASE WHEN verification_count > 0 
        THEN (success_count::REAL / verification_count::REAL) * 100
        ELSE 0 END
    ) STORED
);

CREATE INDEX idx_source_domain ON source_trust USING hash(source_domain);
CREATE INDEX idx_source_trust_score ON source_trust(trust_score DESC);

-- Learning history (for self-improvement)
CREATE TABLE verification_history (
    id BIGSERIAL PRIMARY KEY,
    claim_hash BYTEA NOT NULL,
    result JSONB NOT NULL,
    user_feedback JSONB,
    latency_ms REAL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_verification_claim ON verification_history(claim_hash);
CREATE INDEX idx_verification_created ON verification_history(created_at DESC);
```

---

## 📦 Container 2: TruthSync Edge (Light)

### Purpose
- **Fast Edge**: Microsecond responses
- **Predictive Cache**: Pre-loads likely queries
- **Network Filter**: DNS + HTTP like Pi-hole
- **User-Facing**: Direct interaction

### Components

```yaml
# docker-compose.yml (continued)

services:
  truthsync-edge:
    build: ./truthsync-edge
    container_name: sentinel-truthsync-edge
    restart: unless-stopped
    
    # Public-facing network
    networks:
      - sentinel-network
      - truth-internal  # Can talk to truth-core
    
    # Lightweight (mostly cache)
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    
    ports:
      - "53:53/udp"      # DNS
      - "8053:8053/tcp"  # DNS over HTTPS
      - "3128:3128/tcp"  # HTTP proxy
      - "9090:9090/tcp"  # Metrics
      - "8080:8080/tcp"  # Admin UI
    
    environment:
      - TRUTH_CORE_URL=truth-core:50051
      - CACHE_SIZE=1000000  # 1M entries
      - PREFETCH_ENABLED=true
      - RUST_LOG=info
    
    volumes:
      - truthsync-cache:/app/cache
    
    depends_on:
      - truth-core
    
    cap_add:
      - NET_ADMIN  # For DNS/proxy

volumes:
  truthsync-cache:

networks:
  sentinel-network:
    external: true
```

### In-Memory Cache (Rust)

```rust
// truthsync-edge/src/cache.rs

use dashmap::DashMap;
use lru::LruCache;
use std::sync::Arc;
use tokio::sync::RwLock;

pub struct PredictiveCache {
    // Hot cache (most frequently accessed)
    hot: Arc<DashMap<String, CachedResponse>>,
    
    // Warm cache (LRU for less frequent)
    warm: Arc<RwLock<LruCache<String, CachedResponse>>>,
    
    // Prefetch queue (predicted queries)
    prefetch_queue: Arc<DashMap<String, PrefetchPriority>>,
}

impl PredictiveCache {
    pub fn new(size: usize) -> Self {
        Self {
            hot: Arc::new(DashMap::new()),
            warm: Arc::new(RwLock::new(LruCache::new(size))),
            prefetch_queue: Arc::new(DashMap::new()),
        }
    }
    
    /// Get from cache (microsecond lookup)
    pub async fn get(&self, key: &str) -> Option<CachedResponse> {
        // Try hot cache first (lockless)
        if let Some(response) = self.hot.get(key) {
            return Some(response.clone());
        }
        
        // Try warm cache (locked, but rare)
        let mut warm = self.warm.write().await;
        if let Some(response) = warm.get(key) {
            // Promote to hot if accessed frequently
            if response.access_count > 10 {
                self.hot.insert(key.to_string(), response.clone());
            }
            return Some(response.clone());
        }
        
        None
    }
    
    /// Prefetch likely queries
    pub async fn prefetch(&self, context: &UserContext) {
        // Predict next queries based on context
        let predictions = self.predict_queries(context);
        
        for query in predictions {
            // Add to prefetch queue
            self.prefetch_queue.insert(
                query.clone(),
                PrefetchPriority::High
            );
            
            // Fetch from truth-core in background
            let cache = self.clone();
            tokio::spawn(async move {
                if let Ok(response) = fetch_from_core(&query).await {
                    cache.insert(&query, response).await;
                }
            });
        }
    }
    
    fn predict_queries(&self, context: &UserContext) -> Vec<String> {
        // Predict based on:
        // - User's browsing history
        // - Current page content
        // - Common patterns
        // - Time of day
        
        vec![
            // Example predictions
            "unemployment rate".to_string(),
            "covid vaccine safety".to_string(),
            // ... more predictions
        ]
    }
}
```

### DNS Filter (Rust)

```rust
// truthsync-edge/src/dns_filter.rs

use trust_dns_server::ServerFuture;
use tokio::net::UdpSocket;

pub struct DnsFilter {
    cache: Arc<PredictiveCache>,
    truth_core_client: TruthCoreClient,
}

impl DnsFilter {
    pub async fn handle_query(&self, domain: &str) -> DnsResponse {
        // Fast path: check cache (<1μs)
        if let Some(cached) = self.cache.get(domain).await {
            return cached.into_dns_response();
        }
        
        // Slow path: query truth-core (~50ms)
        let verification = self.truth_core_client
            .verify_domain(domain)
            .await?;
        
        // Cache result
        self.cache.insert(domain, verification.clone()).await;
        
        // Return response
        if verification.trust_score < 50.0 {
            DnsResponse::Blocked
        } else {
            DnsResponse::Allow
        }
    }
}
```

---

## 🔄 Communication Flow

### Cache Hit (Fast Path)

```
User → TruthSync Edge → In-Memory Cache → Response
                         <1ms total
```

### Cache Miss (Slow Path)

```
User → TruthSync Edge → gRPC → Truth Core → DB/Redis → Response
                                ~50-100ms total
       
       Then: Cache result for future queries
```

### Prefetch (Predictive)

```
User browsing → TruthSync Edge predicts next queries
              → Background fetch from Truth Core
              → Pre-populate cache
              
Result: Next query is cache hit (<1ms)
```

---

## ⚡ Performance Characteristics

### TruthSync Edge (Container 2)

```
Cache Hit:
├─ Latency: <1ms
├─ Throughput: 100,000+ queries/sec
└─ Memory: ~2GB (1M cached responses)

Cache Miss:
├─ Latency: ~50-100ms (truth-core query)
├─ Throughput: 1,000 queries/sec
└─ Fallback: Queue for background fetch
```

### Truth Core (Container 1)

```
Verification:
├─ Latency: 50-100ms (complex analysis)
├─ Throughput: 1,000 verifications/sec
└─ Accuracy: 8-0 vs Perplexity (proven)

Learning:
├─ Updates: Real-time from feedback
├─ Pattern Detection: Continuous
└─ Trust Scores: Dynamic adjustment
```

---

## 🎯 Deployment Strategy

```yaml
# Production deployment

version: '3.8'

services:
  # Heavy core (1 instance, powerful hardware)
  truth-core:
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.type == compute-optimized
      resources:
        limits:
          cpus: '8.0'
          memory: 16G
  
  # Light edge (multiple instances, load balanced)
  truthsync-edge:
    deploy:
      replicas: 3  # Scale horizontally
      placement:
        constraints:
          - node.labels.type == edge
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
      
      # Load balancing
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.truthsync.rule=Host(`truthsync.local`)"
```

---

## 📊 Expected Results

### Latency Distribution

```
90% of queries: <1ms (cache hit)
9% of queries: <10ms (warm cache)
1% of queries: <100ms (truth-core verification)

Average: <5ms
p99: <100ms
```

### Resource Usage

```
Truth Core:
├─ CPU: 4-8 cores
├─ RAM: 8-16GB
└─ Disk: 100GB SSD

TruthSync Edge (per instance):
├─ CPU: 1-2 cores
├─ RAM: 1-2GB
└─ Disk: 10GB SSD
```

---

**Architecture**: Dual-container = Heavy Core (truth) + Light Edge (speed) = <10ms latency 🚀
