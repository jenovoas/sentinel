# TODO — Próximos Pasos para Sentinel

> **Última actualización:** 2026-07-28
> Basado en el estado actual del despliegue.

---

## P0 — Urgente (Esta Semana)

### [ ] Iniciar Cortex API en laptop
- **Archivo:** `sentinel-cortex/target/release/sentinel-cortex`
- **Acción:** Ejecutar `./target/release/sentinel-cortex` o instalar systemd
- **Verificar:** `curl http://localhost:8000/health` debe responder
- **Dependencias:** Redis debe estar disponible (`REDIS_URL`)

### [ ] Instalar systemd services en laptop
- **Archivos:** `systemd/sentinel-*.service`
- **Acción:** Copiar a `/etc/systemd/system/`, `daemon-reload`, `enable --now`
- **Servicios:** sentinel-cortex, sentinel-ebpf-forwarder, sentinel-qhc-agent

### [ ] Restaurar conectividad con Fan
- **Síntoma:** `ssh fan.local` no resuelve
- **Acción:** Verificar WireGuard (`sudo wg show wg0`), posible handshake caído
- **Verificar:** `ping 10.88.0.1` desde laptop

### [ ] Iniciar daemons me-60os en laptop
- **Binarios:** `qhc_agent`, `adm_agent`, `pai_neural_daemon`, `vid_agent`
- **Acción:** Arrancar manualmente o via systemd
- **Verificar:** `ps aux | grep -E '(qhc|adm|pai|vid)_agent'`

---

## P1 — Alta Prioridad (Próximo Sprint)

### [ ] Verificar stack de observabilidad en Fan
- Confirmar que Loki, Mimir, Grafana, promtail y node_exporter están activos
- Verificar que el dashboard "SecurePenguin — Monitoreo" tenga datos
- Probar query de logs desde laptop: `curl http://fan:3100/loki/api/v1/query_range`

### [ ] Validar modo dios y whitelist eBPF
- Verificar que UID 1000 está en modo dios: `sudo bpftool map dump name god_mode_uids`
- Contar entradas en whitelists
- Verificar que no hay falsos positivos bloqueando bins legítimos

### [ ] Desplegar eBPF forwarder en Fan
- Copiar `systemd/sentinel-ebpf-forwarder.service` a Fan
- Asegurar que `/var/log/sentinel/` existe
- Verificar que promtail está ingiriendo los logs

### [ ] Prueba de concepto: WebSocket telemetría
- Conectar vía `wscat` al endpoint `/api/v1/telemetry`
- Verificar que eventos eBPF fluyen en tiempo real

### [ ] Actualizar scripts de health check
- `scripts/observability-health.sh`
- `scripts/startup.sh` (obsoleto — usa Docker, no mesh actual)
- Crear script unificado en `scripts/sentinel-health.sh`

---

## P2 — Mejoras Planificadas

### [ ] Integración completa Cortex ↔ QHC Agent
- Conectar el bus de Redis `sentinel:bio_pulse`
- Verificar que QHC recibe pulsos del Cortex
- Validar patrón YHWH (10-5-6-5)

### [ ] Dashboard de estado unificado
- Dashboard en Grafana que muestre:
  - Estado de la mesh (laptop + Fan)
  - Programas eBPF cargados
  - Métricas de resonancia S60
  - Logs de eventos de seguridad

### [ ] Zero-init hardening (P0 eBPF — ya documentado)
- Verificar que todos los programas eBPF tienen memset de estructuras
- Kani verification harness para ebpf_cortex_bridge (ver PLAN_MEJORAS.md)

### [ ] Decision tree embebido en eBPF
- Clasificar amenazas directamente en kernel
- Reducir falsos positivos

### [ ] FFT + Q-factor detector
- Detección de beaconing/DNS tunneling/C2
- Ver papers de referencia en QUICK_REF.md

---

## P3 — Visión a Futuro

### [ ] Tercer nodo mesh (Kingu/Centurion)
- Expandir la mesh batman-adv a un tercer nodo
- Configurar balanceo de carga y failover

### [ ] Cortex federado multi-nodo
- Compartir eventos eBPF entre nodos via Redis bus
- Estado global de resonancia

### [ ] Backup y disaster recovery
- Automatizar backup de PostgreSQL
- Configurar replicación de logs a segundo Loki
- Scripts en `scripts/backup/`

### [ ] Documentación y monitoreo
- Alertas en Grafana para:
  - Caída de mesh (WG handshake timeout)
  - Programa eBPF descargado
  - Daemon me-60os caído
  - Coherencia de cristal por debajo de umbral

---

## 📋 Issues Conocidos

| # | Problema | Estado | Notas |
|---|----------|--------|-------|
| 1 | `ssh fan.local` no resuelve | 🔴 Abierto | Handshake WG posiblemente caído |
| 2 | Cortex API no corre en laptop | 🔴 Abierto | Binario compilado, systemd no instalado |
| 3 | Daemons me-60os no activos en laptop | 🟡 Pendiente | Binarios compilados, no en ejecución |
| 4 | Systemd no instalado en laptop | 🟡 Pendiente | Servicios existen en `systemd/` |
| 5 | startup.sh desactualizado | 🟡 Pendiente | Usa Docker compose, no mesh actual |
| 6 | mycnet-interceptor no activo | 🟡 Pendiente | systemd existe pero no instalado |

---

*Ver también:*
- `PLAN_MEJORAS.md` — Plan detallado de mejoras de eBPF
- `MEJORAS_PLANIFICADAS.md` — Lista completa de mejoras planificadas
- `DEPLOYMENT_STATUS.md` — Estado actual del despliegue
- `OPS.md` — Comandos de operación
