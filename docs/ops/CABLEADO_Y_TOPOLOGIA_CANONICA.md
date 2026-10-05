# Cableado y Topología Canónica del Sistema — Sentinel (Nodo Fenix)

**Fecha de vigencia**: Octubre 2026  
**Servidor**: `fenix` (Alpine Linux v3.24, Kernel 6.18.40-0-virt, arquitectura x86_64)  
**Rama Git**: `alpine_fenix`  
**Propósito**: Fuente de verdad explícita sobre la interconexión, flujo de datos y dependencias encadenadas entre todos los módulos del sistema.

---

## 1. Reglas de Oro de Red y Conectividad (Sin IPs Históricas)

> [!CAUTION]
> **PROHIBICIÓN DE IPs ANTIGUAS**: Las direcciones `10.88.0.1`, `172.18.0.1` fija o rangos de servidores anteriores (Fan, Kingu) están OBSOLETAS.  
> Los agentes de IA **NUNCA** deben asumir IPs fijas en configuraciones ni código.

* **Entre contenedores Docker (red `sentinel_internal`)**: La comunicación se realiza **exclusivamente por nombres de servicio DNS de Docker Compose**:
  * `postgres` (puerto 5432)
  * `redis` (puerto 6379)
  * `prometheus` (puerto 9090)
  * `loki` (puerto 3100)
  * `alertmanager` (puerto 9093)
  * `n8n` (puerto 5678)
  * `node-exporter` (puerto 9100)
  * `postgres-exporter` (puerto 9187)
  * `redis-exporter` (puerto 9121)
  * `neural-guard` (procesamiento continuo)
  * `frontend` (puerto 3000 interno, 3100 publicado en host)
* **Entre el host y Cortex**: Cortex corre como proceso nativo en el host y escucha en `0.0.0.0:8000`. Los proxies y servicios locales lo acceden en `127.0.0.1:8000`.
* **Perímetro público TLS (Nginx del Host)**:
  * `cortex.pinguinoseguro.cl` ➔ Proxy a `http://127.0.0.1:8000`
  * `sentinel.pinguinoseguro.cl/api/v1/` ➔ Proxy a `http://127.0.0.1:8000`
  * `sentinel.pinguinoseguro.cl/` ➔ Proxy a `http://127.0.0.1:3100` (Frontend)
  * `grafana.pinguinoseguro.cl` ➔ Proxy a `http://127.0.0.1:3001` (Grafana)
  * `prometheus.pinguinoseguro.cl` ➔ Proxy a `http://127.0.0.1:9090` (Prometheus con Basic Auth)
  * `n8n.pinguinoseguro.cl` ➔ Proxy a `http://127.0.0.1:5678` (n8n)

---

## 2. Mapa de Conexión Encadenada (Causalidad y Flujo de Datos)

El sistema opera como una cadena biológica y física donde cada módulo alimenta al siguiente:

```
[1. KERNEL LINUX RING-0]
   │  Intercepta execve, apertura de archivos, float contamination y paquetes de red.
   ▼
[2. GUARDIANES eBPF (guardian_execve, float_detector, xdp_firewall)]
   │  Calculan señal de entropía en Base-60 (entropy_s60_raw).
   │  Escriben al RingBuffer del kernel en /sys/fs/bpf/sentinel/events.
   ▼
[3. PUENTE eBPF CORTEX (sentinel-cortex / EbpfBridge)]
   │  Drena el RingBuffer con reconexión continua y backoff automático.
   │  Convierte bytes crudos a CortexEvent estructurado.
   │  Emite al canal broadcast tx_bpf.
   ▼
[4. SOMA OSCILLATOR & QHC AGENT (sentinel-qhc-agent)]
   │  Mantiene el pulso temporal de 23,939,835 ns (≈ 41.77 Hz).
   │  Calcula modulación de fase 10;5,6,5 y corrección de deriva.
   │  Expone socket IPC Unix en /run/soma/qhc.sock.
   ▼
[5. RED CRISTALINA RESONANTE (ResonantLatticeBridge & LiquidLattice 3x3)]
   │  Recibe inyección de entropía de eBPF por nodo (pid % 64).
   │  Recibe tick térmico de CPU derivado con pai60_divide(sample, 60).
   │  Sincroniza fase con el QHC Agent cada segundo.
   │  Calcula la ENERGÍA TOTAL DEL LATTICE (total_energy_raw).
   ▼
[6. RED NEURONAL LIF (NeuralMemory SNN)]
   │  Recibe eventos y corriente de entrada.
   │  Integra en las 64 neuronas LIF y genera spikes de aprendizaje Hebbiano.
   │  Persiste estado continuo en /var/lib/sentinel/snn_weights.crystal.
   ▼
[7. MOTOR DE VERIFICACIÓN (TruthSync Core)]
   │  Recibe textos o claims para auditar (ej. en /api/v1/truth_claim).
   │  Vincula el hash SHA3-512 a la ENERGÍA FÍSICA VIVA del lattice.
   │  Aplica penalizaciones SPA por desinformación.
   │  Ante ataque crítico (rm -rf, drop database): bloquea y escribe a SecurityWal.
   ▼
[8. LOGS DEL SISTEMA Y OBSERVABILIDAD]
   │  Promtail lee /var/log/messages y auth.log (OpenRC syslog).
   │  Envía streams de logs a Loki (puerto 3100).
   │  Exporters exponen métricas de Host (9100), Postgres (9187) y Redis (9121).
   │  Prometheus raspa métricas y evalúa reglas de alerta.
   ▼
[9. MOTOR DE CORRELACIÓN COGNITIVA (Neural Guard)]
   │  Consulta métricas a Prometheus (http://prometheus:9090).
   │  Consulta logs a Loki (http://loki:3100).
   │  Correlaciona Nervio A (intrusión/syscalls) con Nervio B (integridad/respaldos).
   │  Ajusta umbrales con acoplamiento térmico S60.
   │  Aplica debounce de 5 min para evitar tormentas de alertas.
   │  Envía webhook a n8n (http://n8n:5678/webhook/{playbook}).
   ▼
[10. RESPALDO Y PERSISTENCIA (Sentinel Backup Daemon)]
   │  Ejecuta volcado estructurado de Postgres y Redis.
   │  Guarda artefactos sentinel_backup_*.sql.gz en /var/lib/sentinel/backups.
   │  Cortex lee metadatos y expone estado en /api/v1/backup/status.
   ▼
[11. OPERADOR / DASHBOARD FRONTEND]
      Consume telemetría real en vivo consolidada por Cortex.
```

---

## 3. Matriz de Dependencias de Arranque

| Servicio | Requiere para operar | Qué pasa si el precedente falla |
| :--- | :--- | :--- |
| `sentinel-ebpf-load` | Kernel con soporte LSM y BPF | Sin monitor Ring-0 (Cortex opera en fallback). |
| `sentinel-qhc-agent` | Directorio `/run/soma/` accesible | Cortex entra en tick local y marca `qhc.stale = true`. |
| `sentinel-cortex` | Socket QHC y `/sys/fs/bpf/sentinel/events` | El puente eBPF reintenta cada 2s hasta que el mapa aparezca. |
| `sentinel-postgres` | Volumen `postgres_data` y contraseña en `.env` | Contenedor se detiene. Exporter reporta error. |
| `sentinel-redis` | Contraseña en `.env` | Neural Guard y SOMA no pueden leer streams. |
| `sentinel-prometheus` | Red `sentinel_internal` | Alertmanager y Neural Guard quedan sin telemetría de series temporales. |
| `sentinel-loki` | Volumen `loki_data` | Promtail reintenta en buffer; Neural Guard no ve logs. |
| `sentinel-neural-guard` | Prometheus, Loki y Redis | Bucle de recolección ignora orígenes caídos sin crashear. |
| `sentinel-backup` | Directorio `/var/lib/sentinel/backups` (modo 0755) | Cortex reporta advertencia de respaldo no disponible. |

---

## 4. Archivos Clave del Sistema

* **Configuración del stack**: `/opt/sentinel/docker-compose.fenix.yml`
* **Secretos de entorno**: `/opt/sentinel/.env` (permisos `0600`)
* **Servicios nativos de init**: `/etc/init.d/sentinel-*` (OpenRC)
* **Logs de auditoría y WAL**: `/var/log/sentinel/security_wal.log` (fallback `/tmp/sentinel_security_wal.log`)
* **Pesos persistentes de SNN**: `/var/lib/sentinel/snn_weights.crystal`
* **Directorio de respaldos**: `/var/lib/sentinel/backups/`
* **Socket IPC QHC**: `/run/soma/qhc.sock` (permisos `0660`)
