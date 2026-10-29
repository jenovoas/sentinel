---
title: Auditoría de despliegue Sentinel en Kingu y Fenix
fecha: 2026-10-29
estado: auditada_y_reparada_parcialmente
alcance: Sentinel frontend Kingu, backend Fenix, n8n
---

# Auditoría de despliegue Sentinel — Kingu + Fenix

Fecha de revisión: 2026-10-29 UTC. Diagnóstico inicial de solo lectura; después se aplicaron reparaciones autorizadas para DNS, Nginx/TLS y n8n. Estado actualizado y evidencias detalladas en `~/proyectos/personalvault/SecurePenguin/REPARACION_DESPLIEGUE_SENTINEL_N8N_KINGU_FENIX_2026-10-29.md`.

## Dictamen actualizado

Sentinel ahora está publicado y operativo por el dominio para las comprobaciones no autenticadas. Backend y Cortex funcionan por WireGuard. n8n está instalado en Fenix y publicado mediante Kingu. El login Sentinel autenticado y WebSocket con bearer no se verificaron.

- Kingu: Next.js `sentinel-frontend` activo/enabled en `127.0.0.1:3001`; `https://sentinel.pinguinoseguro.cl/login` responde 200.
- Fenix: FastAPI `sentinel-backend:253a3a47`, Cortex `sentinel-cortex:da843a84`, PostgreSQL y Redis saludables.
- DNS A de Sentinel y n8n ahora resuelven a Kingu `64.176.8.191`; certificados TLS separados y hostname correcto. Nginx `-t` pasa.
- n8n `sentinel-n8n` está healthy en Fenix con DB/rol dedicados; `/healthz` público 200; workflows/credentials/executions en cero.
- Al probar BFF/Auth sin sesión se obtiene 401. WebSocket sin bearer con origen Sentinel 401; origen ajeno 403.

## Estado verificado por componente

| Componente | Estado real | Evidencia / limitación |
|---|---|---|
| Frontend Next.js | Activo en Kingu | Unidad active/enabled; loopback `127.0.0.1:3001`; dominio `/login` 200. |
| Auth/BFF | Responde | `/api/auth/me` sin sesión y login con datos inválidos sintéticos requieren autenticación (401). No se probó credencial humana ni login exitoso. |
| FastAPI | Activo en Fenix | Contenedor healthy; health desde Kingu 200; `/api/v1/auth/me` sin token 401. |
| Cortex Rust | Activo en Fenix | Healthy; `/health`/`/metrics` 200. WebSocket 401 sin bearer, Origin ajeno 403. |
| PostgreSQL Sentinel | Healthy, interno | El contenedor real `sentinel-postgres` tiene binding Docker `127.0.0.1:5432`, IP `172.19.0.3`; backend conecta por red Docker interna. |
| Redis Sentinel | Healthy, loopback | Publicado en loopback; Kingu no alcanza 6379. |
| PostgreSQL en `10.88.0.1:5432` | Listener de otro proyecto | Inspección posterior encontró que `docker-proxy` viejo enruta a `172.17.0.2`, `laespiguita-db`, que declara binding en `10.88.0.1:5432`. No tocar: requiere evaluación separada con dueño de La Espiguita. Desde IP pública Fenix el puerto comprobó cerrado; desde Kingu por WG abre. |
| Primer administrador Sentinel | Existe | 1 usuario/superusuario en DB; login real no probado en esta auditoría. |
| Nginx/DNS/TLS Sentinel | Reparado | Vhosts dedicados en Kingu; DNS A a Kingu; TLS con SAN correcto; `/login` HTTP 200. |
| n8n | Instalado | `sentinel-n8n` healthy, digest fijado, PG DB/schema/rol dedicados, puerto `10.88.0.1:5678` permitido solo desde Kingu por WG; dominio TLS 200. Workflows 0. Primer owner setup aún pendiente (`showSetupOnFirstLoad=true`). |
| Guardian/eBPF | No desplegado | No habilitado; se conserva requisito de whitelist/recovery preflight y autorización separada para enforcement. |
| Observabilidad y auxiliares | No desplegados | Prometheus/exporters, Grafana, Loki/Promtail, Alertmanager, Neural Guard y daemons no se iniciaron. n8n sí se instaló a pedido explícito. |
| Contenedor antiguo | Pendiente | `silly_turing`, unhealthy, imagen antigua y sin label del proyecto; no se eliminó al no confirmar origen seguro. |

## Brechas restantes

### P1 — completar autenticación Sentinel

1. Jaime prueba el login en HTTPS con su credencial, ingresada directamente al navegador; no pasar contraseña por chat ni logs.
2. Con sesión activa, verificar cookies seguras, dashboard, BFF, aislamiento multi-tenant y handshake WebSocket autenticado.
3. Confirmar CSP/cabeceras y revisar errores de aplicación tras uso funcional real.

### P1 — n8n y recuperación

- Jaime completa el onboarding owner en `https://n8n.pinguinoseguro.cl/setup` y guarda las credenciales en un gestor seguro; por ahora el setup inicial está pendiente.
- Crear y probar backups/restore de la DB n8n y respaldar de forma segura `/etc/sentinel/n8n.env`/`N8N_ENCRYPTION_KEY`; sin esa clave no se descifran las credenciales almacenadas.
- No importar workflows hasta revisarlos y aprobarlos individualmente. Actualmente workflows 0.

### P1 — contenedor huérfano

Investigar origen, logs, mounts, dependencias y propietario de `silly_turing` antes de parar o retirar; no borrar volúmenes ni limpiar globalmente Docker.

### Alcance del resto del sistema

Si “todo” significa además observabilidad, Guardian/eBPF, Verifier, SHM/lattice, MycNet o daemons nativos, aún hay que definir el alcance por fases. No iniciar Guardian/enforcement automáticamente: primero whitelist/rutas críticas y recuperación fuera de banda verificada; enforcement requiere autorización explícita.

## Evidencia de cambios

- DNS público/privado de Sentinel y n8n: serial `2026102902`, A de ambos a `64.176.8.191`; NS públicos, secundarios Fenix/Kingu responden el serial nuevo.
- Kingu: `nginx -t` correcto; warning TLSv1.3 duplicado sigue en el vhost preexistente `pinguinoseguro.cl`; vhosts nuevos no aportan warning duplicado. Certificados SAN de ambos hostnames validados.
- Pruebas por dominio: Sentinel `/login` 200; `api/auth/me` 401 sin sesión. n8n `/` y `/healthz` 200. WebSocket Sentinel esperado 401 sin bearer y 403 para origen ajeno.
- Fenix: cuatro servicios core más `sentinel-n8n` healthy. n8n usa digest `sha256:eedb51a7...`; DB/rol PostgreSQL dedicados y no superuser; bind `10.88.0.1:5678`; puerto público directo Fenix cerrado, desde Kingu por WireGuard health 200.
- DNS y vhosts se cambiaron de forma separada sin modificar los otros sitios. Otros stacks `impacta-*` y `laespiguita-db` permanecen activos.

## Estado de cambios locales y límites

`docker-compose.fenix.yml` fue modificado para fijar y configurar n8n; está sin commit. `docs/AUDITORIA_VHOST_DNS_TLS_SENTINEL.md` es nuevo. Se preservaron los cambios anteriores de Sentinel y de la vault; no hubo commit/push. Esta verificación no es pentest integral.
