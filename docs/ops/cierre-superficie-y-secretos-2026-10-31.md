# Cierre operativo: frontend, Gamma y credenciales — 2026-10-31

## Alcance y autorización

Jaime autorizó continuar el despliegue en el orden recomendado. Este bloque corrige superficie operativa y seguridad; no activa enforcement eBPF ni altera AD, firewall, MyCNet, Docker global o topología. Kingu conserva edge/BFF; no se realizó aquí la separación física pendiente del frontend del portal.

## Frontend

`fenix-front-1` pertenecía al Compose del portal, no al de Sentinel. Era un falso unhealthy: `wget` no existe en `node:22-bookworm-slim`; HTTP interno respondía200. Se reemplazó la sonda por HTTP nativo Node sobre el mismo `/api/health`, manteniendo tiempos y rechazo de respuestas distintas de200/error/timeout. SRP: vitalidad sin añadir herramientas al runtime.

La primera validación Compose detectó `BACKEND_IMAGE` ausente antes de modificar runtime. Se interpoló con el tag existente `localhost/pinguinoseguro-web:7e88dd7-20261029`, sin recrear API. Se recreó únicamente `front`, terminó healthy; portada y login públicos devolvieron HTTPS200 desde Kingu con TLS verificado. Registro CHG-0025 en el repo portal. No acredita login humano/MFA.

## Gamma

Las cinco operaciones de `backend/app/routers/gamma.py` requieren la dependencia existente `get_current_superuser`: JWT válido, identidad/organización activas e `is_superuser=true`. La cola es global sin tenant: un administrador de organización no está autorizado. Token de ingesta no es sesión humana. Servicio y datos intactos; no se añadió UI ni BFF y la fuente ALPHA fija sigue pendiente del ciclo de decisiones.

58 pruebas de Gamma/auth/identidad pasan dentro de imagen backend compatible, con red deshabilitada, app/tests montados read-only y sin caché. Python local falló primero por rutas y después por ABI de la extensión nativa (`PyErr_GetRaisedException`); no se sustituyó por mock ni se modificó producción para ocultarlo. Avisos de deprecación no suprimidos.

Imagen inicial `sentinel-backend:37cacce7-gamma-admin-1` (`sha256:b65c6efef4d1cf6f1b158cc51f94e8ff8cb655491b4bea2a0c6437ca937edcac`) sustituida por la restricción final de plataforma: `sentinel-backend:37cacce7-gamma-superuser-2`, digest `sha256:aa8e2ab6b15fc968f1591fd77ef07d01e608804f30d19439c03423ca79123d0d`. Las58 pruebas volvieron a pasar con el contrato final; backend healthy y Gamma sin sesión401 tras recreación exclusiva. Backup final `/etc/sentinel/backend.env.pre-backend-image-20261031T053850Z`.
Solo backend recreado, healthy. GET privado Gamma pendiente sin sesión: HTTP401. El acceso autorizado de producción no se ejercitó fabricando JWT.

Configuración protegida con `scripts/configure-backend-image.sh`; backup `/etc/sentinel/backend.env.pre-backend-image-20261031T053112Z`. Retirado override con credencial heredada en `backend/scripts/verify_gamma_flow.py`; usa configuración aprobada.

## Rotación coordinada

`scripts/rotate-backend-secrets.py` genera nuevos secretos sin valores en argv/salida. Cambia contraseña del rol PostgreSQL, contraseña Redis, clave JWT, token de telemetría Fenix/gateway Marte, URLs derivadas y contraseña Grafana reservada de Fenix. Preserva clave de firma WAL independiente. Sesiones JWT anteriores quedan invalidadas por cambio de clave; no se usó una sesión humana real para comprobar revocación.

Primer intento se detuvo antes del backup y de cambios por identidad SSH root sin alias Marte; se corrigió uso de la identidad SSH del operador vía runuser. Ejecución posterior completada: backup protegido `/etc/sentinel/backend.env.pre-secret-rotation-20261031T053404Z`, Redis/backend/Cortex healthy y gateway Marte active. PostgreSQL no se reinició; ni MyCNet ni Docker global se reiniciaron. Fallos posteriores no autorizan rerun ciego: comprobar stores/config y backups protegidos primero.

Comprobación real desde backend: las contraseñas ANTERIORES de PostgreSQL y Redis son rechazadas. Health backend200; Cortex200, QHC conectado/no obsoleto, DTC ticks4955, checkpoint crítico1, fallos0. MyCNet health200. Latch de presencia sigue activo con BIO0, no es fallo de vitalidad.

## Grafana Marte

`scripts/rotate-grafana-admin.py`, ejecutado por stdin en Marte, rotó la contraseña persistida usando CLI `--password-from-stdin`. Cambió configuración a `GF_SECURITY_ADMIN_PASSWORD__FILE` con fichero protegido `/etc/sentinel/grafana-admin-password`, propiedad del UID/GID efectivo de Grafana y modo0400. El Compose ya no contiene la variable de contraseña plana. Plantilla versionada alineada en `service-operation/deploy/marte/compose.yaml`.

Recreado solo Grafana. La nueva credencial autenticó `/api/user` como administrador real; no se imprimió contraseña ni respuesta de identidad. Backup protegido: `/opt/sentinel-marte/compose.yaml.pre-secret-rotation-20261031T053556Z`. Esto acredita rotación/acceso, no aceptación de dashboards, alertas o aislamiento de tenants.

## Reversión y límites

Conservar imágenes y backups protegidos. No restaurar solo el env antiguo después de rotar stores: se desalinearían clientes/servidores y se reintroducirían credenciales expuestas. Recuperar mediante acceso administrativo aprobado y coordinar cambios en ambos extremos. No publicar backups o secretos en Git/vault.

Pendientes siguientes: inventario Guardian/eBPF/watchdog/XPS, época/tick compartidos, flujo Gamma humano autorizado, observabilidad extremo a extremo y recuperación/HA. No se declara cerrada esa cadena por tener servicios activos. El grafo MCP sigue vacío y el índice Graphify previo no completó su actualización; fuente y pruebas runtime prevalecen.
