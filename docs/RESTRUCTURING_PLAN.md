# Sentinel Repository Restructuring Plan

**Objetivo**: Reorganizar el repositorio para escalar a nivel empresarial y acomodar nuevas tecnologías.

---

## Estructura Actual (Análisis)

El repositorio tiene **127 archivos** y **35 directorios** en la raíz, incluyendo:
- 80+ archivos .md mezclados en raíz
- Múltiples carpetas de workflows (n8n-*)
- Código disperso (backend/, frontend/, src/, ebpf/, cortex/)
- POCs aislados (truthsync-poc/, sentinel-wasm/)
- Documentación sin organizar (docs/ con 239 items)

**Problema**: Difícil navegar, mantener y escalar.

---

## Estructura Propuesta (Profesional)

```
sentinel/
├── core/                        # Motor principal
│   ├── cortex/                  # IA (Cerebro)
│   ├── musculo/                 # eBPF/Rust (Ejecución)
│   ├── telemetry/               # Monitoreo
│   └── fsu/                     # Flow Stabilization
│
├── cluster/                     # Gestión distribuida
│   ├── load_balancer/
│   ├── mesh/
│   ├── autoscaler/
│   └── node/
│
├── observability/               # Stack LGTM
│   ├── loki/
│   ├── grafana/
│   ├── tempo/
│   ├── mimir/
│   └── aiops_shield/
│
├── deploy/                      # Deployment
│   ├── kubernetes/
│   ├── docker/
│   └── terraform/
│
├── docs/                        # Documentación organizada
│   ├── architecture/
│   ├── hardware/
│   ├── research/
│   ├── implementation/
│   └── patents/
│
├── tests/                       # Testing
│   ├── unit/
│   ├── integration/
│   ├── benchmarks/
│   └── demos/
│
└── tools/                       # Herramientas
```

---

## Migración Fase 1: Limpiar Raíz (AHORA)

**Mover archivos .md a docs/**:
- Todos los .md de raíz → `docs/archive/`
- Mantener solo: README.md, LICENSE, CONTRIBUTING.md

**¿Procedo con Fase 1?**

