---
title: Auditoría de despliegue Sentinel en Kingu y Fenix
fecha: 2026-10-29
estado: auditoria_runtime_verificada_con_bloqueos
alcance: Sentinel frontend Kingu, backend Fenix
---

# Auditoría de despliegue Sentinel — Kingu + Fenix

Fecha de revisión: 2026-10-29 UTC. Auditoría de solo lectura, salvo sondas HTTP/DB de lectura. No se reiniciaron ni cambiaron servicios, firewall, DNS, Nginx o datos. No se leyeron valores secretos.

## Dictamen ejecutivo

**Sentinel está desplegado parcialmente y el plano de servicios funciona en privado, pero no está publicado/operativo de extremo a extremo por el dominio.**

- **Kingu:** Next.js `sentinel-frontend` está `active/enabled`; responde HTTP 200 en `127.0.0.1:3001/login`, limitado a loopback.
- **Fenix:** backend FastAPI `sentinel-backend:253a3a47`, Cortex Rust `sentinel-cortex:da843a84`, PostgreSQL y Redis dedicados están `healthy`. Migración en head; DB contiene 1 usuario y 1 superusuario.
- **Red privada:** desde Kingu responden FastAPI health 200, Cortex health 200 y autenticación sin credenciales 401. WebSocket rechaza origen ajeno (403), y el origen configurado del frontend llega a la validación de autenticación (401); no se pudo probar upgrade autenticado porque no se usó token.
- **Bloqueo crítico de publicación:** DNS público `sentinel.pinguinoseguro.cl` sigue en `64.176.28.233` (Fenix), mientras Kingu es `64.176.8.191`. Kingu no tiene vhost ni certificado para Sentinel. El 443 en Kingu sirve actualmente el sitio Impacta/default, no el frontend Sentinel. Acceder al dominio por la resolución actual no llega a Kingu.
- **Riesgo crítico adicional:** PostgreSQL de Sentinel está publicado en `10.88.0.1:5432` (WireGuard) y es accesible desde Kingu, aunque la guía declara que debe quedar solo en `127.0.0.1`. No se comprobó acceso desde otro peer VPN.
- **Deriva de ejecución:** hay un contenedor huérfano `silly_turing` con imagen antigua `sentinel-backend:c59f9840`, en estado `unhealthy`, fuera del proyecto Compose `sentinel`.

## Estado verificado por componente

| Componente | Estado real | Evidencia / limitación |
|---|---|---|
| Frontend Next.js | Activo en Kingu | `systemctl` active/enabled; `127.0.0.1:3001/login` = 200; título `Sentinel — Panel de control`; Node solo en loopback. |
| Auth/BFF | Parcialmente funcional | `POST /api/auth/login` con origen simulado permitido y credenciales sintéticas inválidas llega a FastAPI y devuelve 401. No se intentó una contraseña real ni se comprobó login exitoso en esta auditoría. |
| FastAPI | Activo en Fenix | Contenedor healthy; desde Kingu `/api/v1/health` = 200 y `/api/v1/auth/me` sin token = 401. |
| Cortex Rust | Activo en Fenix | Contenedor healthy; `/health` y `/metrics` = 200. `/api/v1/telemetry` sin token: origen esperado 401; origen no permitido 403. |
| PostgreSQL Sentinel | Activo, exposición más amplia que lo documentado | Healthy y persistente; `10.88.0.1:5432` escucha y conexión TCP desde Kingu abre. Compose de runtime le asigna publicación a `127.0.0.1:5432`; runtime efectivo contradice ese archivo. |
| Redis Sentinel | Activo y sin puerto público | Healthy; mapeo Docker `127.0.0.1:6379`; TCP 6379 desde Kingu cerrado. |
| Primer administrador | Existe | Consulta de solo lectura en DB: 1 usuario, 1 superusuario. No se realizó login válido ni se leyó el hash/contraseña. |
| Nginx/DNS/TLS Sentinel | No desplegado | Nginx `nginx -t` pasa, pero no hay `server_name sentinel.pinguinoseguro.cl`; certificados presentes no incluyen ese nombre. DNS A resuelve a Fenix. |
| Guardian/eBPF | No desplegado/activado | No forma parte de este despliegue. No se verificó de nuevo whitelist. No activar sin preflight de recuperación fuera de banda y autorización correspondiente. |
| Observabilidad/automatización Sentinel | No desplegada en runtime | Solo están levantados los 4 servicios core de Sentinel. Compose define otros servicios pero no están en ejecución: Prometheus, exporters, Grafana, Loki, Promtail, Alertmanager, n8n y neural-guard. |

## Brechas y hallazgos

### P0 — publicar correctamente el sitio

1. Cambiar el DNS A de `sentinel.pinguinoseguro.cl` de Fenix a Kingu, solo con autorización y ventana acordada.
2. Instalar un vhost Nginx independiente para Sentinel y su certificado TLS. No editar los vhosts existentes de otros sitios; revisar `nginx -t` y probar rollback antes de recargar.
3. Configurar rutas: Next local para web/BFF y `/api/v1/telemetry` a Cortex `10.88.0.1:8001` con WebSocket/Upgrade. FastAPI queda accesible vía BFF por WireGuard, no desde el navegador.
4. Verificar por DNS público que `/login` sirve el HTML Sentinel, certificado válido para Sentinel y que las rutas web/API/WebSocket se comportan correctamente. Hoy las pruebas de dominio en el endpoint actual de Kingu devolvieron el contenido de Impacta con certificado de Impacta; no exponer como terminado.

### P0 — corregir la exposición de PostgreSQL

El socket publicado está en `10.88.0.1:5432`, no en `127.0.0.1`. Kingu lo alcanza por WireGuard. Confirmar la causa (configuración Compose efectiva, socket proxy/iptables y reglas de firewall) y rebindear solo Sentinel a loopback; después comprobar que aplicaciones acceden por red interna Docker y que TCP desde Kingu y desde fuera queda cerrado. No aplicar reglas ni reiniciar antes de revisar el estado Compose y preparar recuperación.

### P1 — limpiar deriva de contenedores

Inspeccionar procedencia y logs del contenedor `silly_turing` (`sentinel-backend:c59f9840`, unhealthy, sin label de proyecto Compose) y confirmar que es residuo Sentinel. Solo entonces retirarlo/pararlo con autorización; no borrar volúmenes ni tocar otros proyectos. Confirmar luego que `docker ps` muestra únicamente los cuatro servicios core esperados.

### P1 — completar autenticación e integración frontend

1. Probar login exitoso usando credencial ingresada de forma segura por Jaime, sin pasarla por logs ni chat; verificar cookie segura/HttpOnly y `/api/auth/me`.
2. Con sesión real, validar dashboard, BFF a FastAPI, endpoints de métricas/telemetría y handshake WebSocket autenticado. La ruta WebSocket aún no tiene handshake autorizado verificado.
3. Verificar autorización/aislamiento multi-tenant y flujos funcionales (no basta con HTTP 200 de salud).
4. Probar desde la web TLS real, no solo `localhost:3001`; confirmar CSP, cabeceras, cookies Secure/SameSite y logs.

### P1 — comprobar el alcance operativo, persistencia y recuperación

- Validar backups de PostgreSQL/volúmenes, procedimiento de restauración, retención y prueba de restore.
- Confirmar si Redis debe persistir y revisar política de backup/recuperación.
- Revisar monitoreo y alertas de salud/espacio/reinicios; ahora no hay stack Sentinel de observabilidad ejecutándose.
- Verificar almacenamiento local de métricas de Kingu: los directorios existen y el usuario de servicio puede escribir, pero no se hallaron ficheros de métricas/reportes durante la auditoría.
- Si el alcance de «sistema completo» incluye protección eBPF, daemons nativos, Verifier, SHM/lattice, MycNet, Neural Guard, n8n y dashboards de observabilidad, esas capas no están desplegadas/activas según la verificación actual. Definir cuáles son requisitos de producción y desplegar por fases; no activar Guardian/enforcement de forma implícita.

## Evidencia de ejecución

- SSH por alias `fenix` y `kingu`, fecha/hora remota 2026-10-29 alrededor de 20:41–20:48 UTC; Fenix `10.88.0.1/24`, Kingu `10.88.0.2/24` por `wg0`.
- Fenix: imágenes activas `sentinel-backend:253a3a47` y `sentinel-cortex:da843a84`; los cuatro contenedores core healthy y sin reinicios reportados. `alembic current`: `20261029_user_timestamp_defaults (head)`.
- Kingu: unidad `sentinel-frontend.service` activa/habilitada; Next.js 16.4.3, HTTP loopback 200 y bind `127.0.0.1:3001`.
- Health FastAPI/Cortex desde Kingu: 200. `/api/v1/auth/me` sin token: 401. Prueba WebSocket con Origin exacto permitido: 401 por falta de bearer; Origin ajeno: 403.
- DNS público desde resolver local, 1.1.1.1 y 8.8.8.8: Sentinel → `64.176.28.233`; IP pública de Kingu observada como `64.176.8.191`. Petición con IP de Kingu forzada sirvió default vhost Impacta y presentó certificado `impacta.pinguinoseguro.cl`.
- PostgreSQL TCP desde Kingu a `10.88.0.1:5432`: abierto; Redis 6379: cerrado. FastAPI/Cortex 8000/8001 accesibles por WireGuard; comprobaciones a puertos API en IP pública de Fenix agotaron timeout.
- No se verificó el rechazo desde un peer VPN distinto de Kingu; la política de firewall declarada permite solo Kingu, pero el control efectivo de PostgreSQL debe comprobarse con segundo peer autorizado.

## Próxima secuencia recomendada

1. Atender primero P0 PostgreSQL y conservar evidencia/rollback.
2. Validar la release frontend, auth y WebSocket con credenciales seguras antes de publicación.
3. Cambiar DNS/vhost/TLS de Sentinel en cambio coordinado; no alterar otros sitios.
4. Resolver contenedor huérfano y decidir alcance de servicios restantes (observabilidad, eBPF y daemons) con criterios de aceptación claros.
5. Repetir smoke tests y registrar resultados antes de declarar despliegue completo.

## Estado de cambios locales y límites

En el checkout local de Sentinel, rama `main`, permanecen modificaciones sin commit en `docker-compose.fenix.yml`, `sentinel-cortex/src/main.rs`, `sentinel-cortex/src/memory/crystal_runtime.rs` y `systemd/sentinel-cortex.service`. No se atribuye que esos cambios estén incluidos en los bins/imágenes activos de Fenix: el backend activo etiqueta `253a3a47`, Cortex `da843a84`; hay que cotejar commit/digest de build antes de reemplazar. En la vault también hay cambios ajenos sin commit; no se modificaron.

Esta auditoría es observación puntual, no pentest integral ni verificación de todos los endpoints, permisos y secretos. La publicación pública de Sentinel no se considera completada.
