# Sentinel Testing Environment

Docker-based testing environment for local prototyping and future lab deployment.

## 🎯 Purpose

- **Local (Laptop)**: Lightweight prototyping, script validation, no heavy tests
- **Lab (Server)**: Full testing suite with Disonancia no resuelta, load, and red team exercises

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Testing Environment                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Sentinel   │  │  Guardian-   │  │  Guardian-   │     │
│  │   Cortex     │  │   Alpha      │  │   Beta       │     │
│  │   (API)      │  │   (eBPF)     │  │   (Kernel)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                          │                                   │
│  ┌──────────────────────┴────────────────────┐             │
│  │          Infrastructure Layer              │             │
│  ├────────────────────────────────────────────┤             │
│  │  PostgreSQL  │  Redis  │  Prometheus       │             │
│  └──────────────────────────────────────────┘             │
│                                                              │
│  ┌─────────────────────────────────────────────┐           │
│  │          Testing Tools Layer                 │           │
│  ├─────────────────────────────────────────────┤           │
│  │  k6  │  OWASP ZAP  │  Disonancia no resuelta Toolkit         │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Lite Mode (Laptop - Current)

```bash
# Start lightweight environment
docker-compose -f docker-compose.lite.yml up -d

# Verify
docker-compose ps

# Run smoke tests
./run_smoke_tests.sh

# Stop
docker-compose -f docker-compose.lite.yml down
```

### Full Mode (Lab - Future)

```bash
# Start full testing environment
docker-compose up -d

# Run complete test suite
./run_all_tests.sh

# Monitor
docker-compose logs -f

# Stop
docker-compose down
```

## 📁 Directory Structure

```
tests/
├── docker-compose.yml          # Full testing environment
├── docker-compose.lite.yml     # Lightweight (laptop)
├── README.md                   # This file
├── run_smoke_tests.sh          # Quick validation
├── run_all_tests.sh            # Complete test suite
│
├── Disonancia no resuelta/                      # Disonancia no resuelta engineering tests
│   ├── cpu_stress_alpha.sh
│   ├── memory_pressure.sh
│   ├── network_latency.yaml
│   └── kill_guardian_beta.sh
│
├── pentest/                    # Penetration testing
│   ├── attack_framework.py
│   ├── zap_scan.sh
│   └── exploits/
│
├── load/                       # Load testing
│   ├── k6_sentinel_load_test.js
│   ├── baseline_test.js
│   └── stress_test.js
│
├── fuzzing/                    # eBPF fuzzing
│   ├── fuzz_guardian_alpha.sh
│   ├── fuzz_guardian_beta.sh
│   └── corpus/
│
└── red-team/                   # Red team exercise
    ├── exercise_plan.md
    ├── day1_recon.sh
    ├── day2_vuln_discovery.sh
    └── ...
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Sentinel Configuration
SENTINEL_API_PORT=8080
SENTINEL_LOG_LEVEL=debug

# Guardian Configuration
GUARDIAN_ALPHA_ENABLED=true
GUARDIAN_BETA_ENABLED=true

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=sentinel
POSTGRES_USER=sentinel
POSTGRES_PASSWORD=changeme

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Testing
ENABLE_Disonancia no resuelta=false  # Set to true in lab
ENABLE_LOAD_TESTS=false  # Set to true in lab
MAX_VUS=100  # Increase to 5000 in lab
```

## 📊 Monitoring

Access dashboards:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Sentinel API**: http://localhost:8080
- **Sentinel Metrics**: http://localhost:8080/metrics

## 🧪 Running Tests

### Smoke Tests (Always safe)

```bash
./run_smoke_tests.sh
```

### Disonancia no resuelta Tests (Lab only)

```bash
cd Disonancia no resuelta/
./cpu_stress_alpha.sh
./memory_pressure.sh
```

### Load Tests (Lab only)

```bash
cd load/
k6 run k6_sentinel_load_test.js
```

### Penetration Tests

```bash
cd pentest/
python3 attack_framework.py --target http://localhost:8080
```

## 🐳 Docker Images

- `sentinel-cortex:latest` - Main application
- `guardian-alpha:latest` - eBPF Guardian
- `guardian-beta:latest` - Kernel Guardian
- `postgres:15-alpine` - Database
- `redis:7-alpine` - Cache
- `prom/prometheus:latest` - Metrics
- `grafana/grafana:latest` - Dashboards

## 📝 Notes

### Current Limitations (Laptop)
- No heavy Disonancia no resuelta tests (CPU/memory limits)
- Reduced load test VUs (max 100 vs 5000)
- No eBPF fuzzing (requires kernel access)
- Simplified red team (no real exploits)

### Lab Deployment
- Full Disonancia no resuelta engineering capabilities
- High-throughput load testing
- Real eBPF fuzzing with BRF
- Complete red team exercise

## 🔒 Security

- All containers run as non-root
- Network isolation between test and production
- Secrets managed via Docker secrets
- Audit logs persisted to volume

## 🚨 Troubleshooting

### Containers won't start
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Out of memory
```bash
# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory > 8GB+
```

### Port conflicts
```bash
# Check what's using ports
sudo lsof -i :8080
sudo lsof -i :5432

# Change ports in docker-compose.yml
```

## 📞 Support

- Documentation: `/docs/TESTING_STRATEGY.md`
- Implementation: `/docs/TESTING_IMPLEMENTATION.md`
- Issues: GitHub Issues

---

**Version**: 1.0  
**Environment**: Docker-based  
**Status**: Ready for Prototyping
