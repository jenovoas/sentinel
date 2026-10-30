# Backend de seguridad y observabilidad de Marte

El stack se aloja en Marte (`10.88.0.6`); Fenix (`10.88.0.1`) sigue como backend central. SOMA no forma parte de este stack. Prometheus obtiene las métricas de FastAPI y Cortex por WireGuard; Prometheus conserva 30 días localmente y las envía a Mimir. Grafana consulta Prometheus, Mimir y Loki. Alloy en ambos nodos entrega journald/auditd; Alloy de Fenix también sigue los logs JSON de Docker sin montar el socket del daemon.

## Procedimiento aplicado

1. Verificar nodo, WireGuard, disco, Firewalld y acceso administrativo; instalar Docker Engine y Compose v2 en Marte.
2. Copiar este directorio a `/opt/sentinel-marte`; crear allí `.env` con `GF_SECURITY_ADMIN_PASSWORD`, dueño `root:root`, modo `0600`. No versionar ni imprimir el secreto.
3. En Marte ejecutar `docker compose config --quiet`, revisar bindings y luego `docker compose up -d`. Confirmar salud HTTP y estado de cada contenedor.
4. Permitir TCP 3100 desde Fenix (`10.88.0.1`) y TCP 3000 desde los nodos administrativos autorizados. Prometheus/Mimir permanecen sin puertos publicados en el host.
5. En Fenix validar que Loki responde por `http://10.88.0.6:3100/ready`, y aplicar `compose.fenix-agent.yaml`. El agente usa `network_mode: host` para que sus conexiones a Loki salgan por WireGuard con la IP de Fenix que permite Firewalld; Alloy escucha su diagnóstico solo en `127.0.0.1:12345`. No monta el socket Docker.
6. Aceptar telemetría solo al confirmar objetivos Prometheus `up`, `remote_write` sin errores, etiquetas y entradas consultables en Loki y datasources provisionados en Grafana. `/-/healthy` del agente por sí solo no prueba ingesta.

La API de Loki se publica únicamente en la IP WireGuard de Marte, puerto 3100. Grafana se publica en la IP WireGuard, puerto 3000. La política Firewalld permite Loki solo desde Fenix y Grafana desde los nodos administrativos autorizados. Prometheus y Mimir no publican puertos en el host.

## Límites funcionales

- Los paneles existentes de Sentinel se provisionan sin alterar sus consultas. Los que dependan de métricas no exportadas por Cortex seguirán sin datos.
- El almacenamiento Mimir es monolítico en disco local, con retención de 30 días. No brinda alta disponibilidad ni reemplaza una política de backup.
- Promtail no se usa: alcanzó EOL el 2026-03-02; Alloy es el agente de logs vigente.
- TruthSync Core no se arranca como servicio con el score fijo/procesamiento simulado histórico. El filtro de entropía integrado en Fenix permanece separado del verificador/score de contenidos pendiente de recuperar y corregir.
- Guardian Alpha/eBPF está adjunto en Marte en modo auditoría tras comprobar whitelist, acceso administrativo y recuperación. El `sentinel-security-gateway` consume su ring buffer, sanitiza telemetría y mantiene WAL local; la recepción final en Fenix sigue pendiente de corregir la serialización exacta de scores SPA en el backend. No se activa enforcement.
- AIOpsShield/TelemetrySanitizer corren en el gateway de Marte. AIOpsDoom se trata como clase de amenaza; no se atribuye equivalencia al paper sin evaluar el flujo estructurado completo.
- Guardian Beta/Cortex y Gamma/API permanecen en Fenix; la UI de aprobación corresponde a Kingu. La GUI Tauri histórica fue un prototipo con métricas simuladas, retirada del árbol activo. No empaquetar hasta recuperar/revisar y conectar sus datos reales.
