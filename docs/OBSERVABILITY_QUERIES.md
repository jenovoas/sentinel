# 📊 Sentinel Cortex - Observability Runbook

## Golden Signals (Loki & Prometheus)

Estos queries están diseñados para ser importados en Grafana para el dashboard "Sentinel Truth Live".

### 1. Truth Integrity Monitor
**Description**: Detección de brechas en la integridad del timeline de eventos.
**Alert Threshold**: < 95% (Trigger ARMOR_MODE)
```logql
{job="sentinel-guardian"} | json | truth_integrity < 95
```

### 2. XDP Packet Drops (Performance)
**Description**: Volumen de paquetes purgados en capa física (NIC).
**Validation Goal**: > 1000 drops/24h (Under Attack)
```logql
{job="xdp-sentry"} | json | drops > 1000
```

### 3. Cortex Decision Latency (P99)
**Description**: Latencia de end-to-end desde kernel hook hasta decisión AI.
**SLA**: < 1.25µs
```promql
histogram_quantile(0.99, rate(cortex_latency_bucket[5m]))
```

### 4. Neural Reflex Triggers
**Description**: Activaciones automáticas del sistema inmune (bypass de intervención humana).
```logql
{job="cortex-engine"} | json | event_type="NEURAL_REFLEX"
```

---
**Note for SRE**: Import dashboard via `configs/grafana-provisioning.json` (Phase 2).
