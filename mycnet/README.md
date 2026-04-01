# MycNet: Red Mesh Bio-Inspirada con Extensiones Sentinel

**Fecha:** 2026-01-14  
**Objetivo:** Red mesh WiFi/Ethernet inspirada en micelio con métricas Base-60, modulación YHWH y auto-reparación.

---

## Plan de Implementación Híbrido

### **Fase 1-4: MinIO (Validación Rápida - 7 días)**

- Setup mesh batman-adv
- Storage distribuido con MinIO (EC 4+2)
- Validación convergencia y resiliencia
- **Objetivo**: Métricas de red estables

## Inventario y costos

### 2.1 Hardware mínimo (4 nodos iniciales)

- **4× PCs viejas** (reutilización, costo $0)
  - CPU: Dual-core+ (Intel/AMD post-2010)
  - RAM: 4GB mínimo (8GB ideal para Ceph)
  - Storage: HDD 500GB+ o SSD 128GB+ (SATA nativo)
  - Red: Ethernet Gigabit integrado
- Switch Gigabit Ethernet (5 puertos)
- Cables Ethernet Cat5e/Cat6

**Estimación costo**

- PCs: $0 (reutilización)
- Switch: ~$20-30 USD
- Cables: ~$10 USD
- **Total: ~$30-40 USD**

**Escalado futuro**: 6-8 nodos cuando consigas más PCs estables

### **Fase 5: Ceph (Full Micelio - 8 días)**

- Migración MinIO → Ceph
- Auto-reparación nativa (CRUSH)
- Integración S60 + YHWH modulation
- **Objetivo**: Isomorfismo micelio completo

---

## Decisiones Cerradas

1. **Backhaul**: Ethernet (Fase 1-4), WiFi opcional (Fase 5)
2. **Storage**: MinIO → Ceph (híbrido)
3. **Precisión S60**: Hasta segundos (3 niveles)
4. **Convergencia**: 5 pings consecutivos sin pérdida

---

## Estructura del Proyecto

```
mycnet/
├── scripts/
│   ├── mesh_setup.sh          # Setup batman-adv por nodo
│   ├── minio_deploy.sh        # Deploy MinIO cluster
│   ├── ceph_deploy.sh         # Deploy Ceph (Fase 5)
│   ├── mycnet_s60_monitor.py  # Métricas S60
│   └── ceph_yhwh_tuner.sh     # Modulación YHWH
├── configs/
│   ├── systemd/               # Units para servicios
│   └── grafana/               # Dashboards
├── docs/
│   └── IMPLEMENTATION_PLAN.md # Plan completo
└── results/
    ├── phase1-4/              # Resultados MinIO
    └── phase5/                # Resultados Ceph
```

---

## Próximos Pasos

1. ✅ Guardar plan completo
2. ✅ Crear scripts de deployment
3. ⏸️ Adquirir hardware (6x RPi4 + SSDs)
4. ⏸️ Ejecutar Fase 1-4 (MinIO)
5. ⏸️ Evaluar resultados y decidir Fase 5 (Ceph)

---

**Ver**: [`MYCNET_IMPLEMENTATION_PLAN.md`](file:///home/jnovoas/dev/sentinel/mycnet/docs/MYCNET_IMPLEMENTATION_PLAN.md) para detalles completos.
