# Despliegue separado: Fenix y Kingu

## Objetivo

Separar la superficie pública de los servicios internos:

- **Kingu** (`10.88.0.2`): entrada pública, Nginx, TLS y proxy inverso. No aloja contenedores de aplicación ni bases de datos.
- **Kingu**: ejecuta Next.js como servicio systemd, enlazado solo a `127.0.0.1:3001`.
- **Fenix** (`10.88.0.1`): contenedores de aplicación y backend, bases de datos, compilación y servicios internos.
- **WireGuard** (`10.88.0.0/24`): único camino de Kingu a los servicios internos de Fenix.

El navegador solo conecta con Nginx en Kingu. Las rutas web y REST pasan al BFF Next.js local en `127.0.0.1:3001`; `/api/v1/telemetry` se envía como WebSocket a Cortex en Fenix por WireGuard (`10.88.0.1:8001`). El BFF llama a FastAPI en `10.88.0.1:8000`. Ambos puertos de aplicación se publican solo en la IP WireGuard de Fenix y el firewall permite conexiones entrantes únicamente desde Kingu (`10.88.0.2`). Postgres y Redis permanecen privados.

Esta guía aplica a `main` y systemd. No mezclar con `alpine_fenix`/OpenRC.

## Preflight observado el 2026-10-29

Verificado por SSH en Fenix y Kingu; no se modificaron servicios, firewall, DNS ni Nginx:

- **Fenix**: Debian 13, Docker Compose 2.26, `wg0=10.88.0.1`; UFW está activo con políticas de entrada/reenvío `DROP`. No hay stack, contenedores, entorno ni listeners Sentinel en `8000/8001`. Corren contenedores de otros proyectos, que deben permanecer intactos. Hay una base existente que escucha en `10.88.0.1:5432`; la base Sentinel debe quedar ligada solo a `127.0.0.1:5432`.
- **Kingu**: Debian 13, `wg0=10.88.0.2`, Node `20.19.2` y Nginx activo. No hay release instalada, entorno ni unidad `sentinel-frontend`. El bundle está solo en `/tmp` y pasó una prueba temporal en `127.0.0.1:3001`; ese proceso terminó. El virtual host actual de `pinguinoseguro.cl` apunta a `127.0.0.1:3000` y responde HTTP 502; no se debe reutilizar ni alterar para Sentinel.
- `sentinel.pinguinoseguro.cl` resuelve actualmente a la IP pública de Fenix (`64.176.28.233`), no a Kingu (`64.176.8.191`). Nginx en Kingu no tiene virtual host ni certificado para Sentinel. Corregir DNS y preparar TLS antes del cambio público.
- El `docker-compose.fenix.yml` anterior construía el servicio llamado `cortex` con el Dockerfile de FastAPI, no con el servidor Axum, y no publicaba la ruta WebSocket. El Cortex correcto escucha en el puerto de contenedor `8000`; el despliegue lo publicará como `10.88.0.1:8001`, mientras FastAPI conserva `10.88.0.1:8000`.
- Fenix no tiene un Redis Sentinel/shared accesible por host. La instancia activa `impacta-redis` está aislada en la red de su propio Compose. La Compose de Sentinel incluye Redis propio, pero el despliegue debe esperar a confirmar si se usará un servicio multitenant compartido o una instancia dedicada.
- Después del preflight se compilaron en Fenix las imágenes `sentinel-backend:96043b54` y `sentinel-cortex:96043b54`; el bundle Next.js se generó en Fenix, se transfirió a `/tmp` en Kingu, se verificó su SHA-256 y respondió HTTP 200 en una prueba temporal de loopback. El proceso temporal se detuvo. Ningún servicio de Sentinel se inició.

No asumir que un archivo Compose presente equivale a un servicio desplegado o saludable. No activar Guardian/LSM como parte de esta separación frontend/backend.

## Secuencia de despliegue

### 1. Preflight y recuperación

1. Confirmar SSH independiente a ambos nodos y acceso de consola del proveedor a Kingu.
2. Registrar salud HTTP/TLS, estado de Nginx, túnel WireGuard, UFW, servicios de Fenix, contenedores y bases de datos.
3. Confirmar copias de seguridad y espacio de disco. No imprimir valores de archivos de entorno, secretos ni configuración privada en terminales o logs.
4. Desplegar el frontend en una unidad y un virtual host propios. No cambiar los upstreams ni los virtual hosts de `pinguinoseguro.cl`, La Espiguita o Impacta.

### 2. Preparar servicios internos en Fenix

1. Instalar los secretos directamente en Fenix en `/etc/sentinel/backend.env` (`root:docker`, modo `0640`); no versionarlos ni guardarlos en la raíz del repositorio. Pasar ese mismo archivo a `docker compose --env-file` para la interpolación de Compose. Se aprobó Redis dedicado en esta Compose; definir `SENTINEL_REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/0` con una contraseña hexadecimal aleatoria para evitar caracteres que requieran codificación URL.
2. Levantar primero las bases de datos en una red Docker interna, con volúmenes persistentes y healthchecks.
3. Antes de abrir puertos, verificar en Fenix la ruta efectiva del tráfico publicado por Docker: el DNAT puede llevarlo por `FORWARD`/`DOCKER-USER`, no por `INPUT`. La regla nftables adicional no garantiza acceso si otra cadena base posterior de UFW descarta el paquete. Configurar una regla de reenvío limitada a `wg0`, origen `10.88.0.2` y destino/puerto de cada API; comprobar contadores y acceso desde Kingu, y confirmar rechazo desde otra interfaz. No aplicar reglas hasta asegurar SSH independiente y una ruta de recuperación.
4. Construir la imagen FastAPI con `docker build --pull -f backend/Dockerfile --tag sentinel-backend:<commit> .` y la imagen Axum desde el código actual con `scripts/build-sentinel-cortex-image.sh sentinel-cortex:<commit>`; no usar el binario versionado antiguo sin reconstruirlo. Configurar esos tags y `SENTINEL_REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/0` en `/etc/sentinel/backend.env` (usar una contraseña hex aleatoria para evitar caracteres que requieran codificación URL). Tras validar la configuración, iniciar únicamente `postgres`, `redis`, `backend` y `cortex` con `docker compose --no-build --env-file /etc/sentinel/backend.env -f docker-compose.fenix.yml up -d postgres redis backend cortex`. Compose debe esperar a Postgres y Redis saludables antes de iniciar las aplicaciones. Postgres queda en `127.0.0.1:5432`, FastAPI en `10.88.0.1:8000` y Cortex en `10.88.0.1:8001`.
5. Desde Kingu, comprobar por WireGuard FastAPI `/api/v1/health`, `/api/v1/auth/me` (sin token debe responder 401), Cortex `/health` y la conexión WebSocket. Desde una red externa, confirmar que FastAPI, Cortex, Postgres y Redis no son accesibles.

#### Migraciones e identidad inicial

El entrypoint aborta si `alembic upgrade head` falla. La adopción del esquema legacy solo procede cuando las tablas, tipos, restricciones y políticas RLS coinciden exactamente con el baseline conocido; si encuentra un esquema parcial o distinto, detiene el arranque para revisión manual sin continuar con la migración. Después de que Alembic llegue al head esperado y exista una organización y tenant activos, el primer administrador se crea manualmente dentro del contenedor backend con `python -m app.bootstrap_admin`. El comando solicita la contraseña sin eco y se niega a crear otra cuenta superusuario si ya existe una. Acordar el slug y los datos del primer administrador antes de abrir el sitio al público. No habilitar un registro público para sustituir este aprovisionamiento.

### 3. Cambiar la entrada pública en Kingu

1. En Fenix, desde `main`, ejecutar `npm ci` y `npm run build` dentro de `frontend/`; crear el bundle con `scripts/package-frontend.sh /tmp/sentinel-frontend.tar.gz`.
2. Verificar que `/usr/bin/node` en Kingu satisface el engine de `frontend/package.json` (el `20.19.2` instalado cumple Next.js 16). Crear la cuenta de servicio sin login `sentinel-frontend`. Transferir el tarball y su `.sha256` por WireGuard, y verificar `sha256sum -c` antes de extraer. Crear `/opt/sentinel/frontend/releases/<versión>`, extraer ahí y dejar el bundle como `root:sentinel-frontend`, con directorios `0750` y archivos `0640`. Asignar solo `.next/cache` a `sentinel-frontend:sentinel-frontend` modo `0750`, porque Next.js necesita escribir allí. Preparar el enlace con `ln -s /opt/sentinel/frontend/releases/<versión> /opt/sentinel/frontend/.current-<versión>` y reemplazarlo atómicamente con `mv -Tf /opt/sentinel/frontend/.current-<versión> /opt/sentinel/frontend/current`.
3. Crear `/var/lib/sentinel-frontend/host-metrics/{data,reports}` en Kingu, propiedad de `sentinel-frontend`. Configurar allí el colector local de métricas de Kingu; el bundle no incluye directorios de datos.
4. Crear `/etc/sentinel/frontend.env` desde `config/systemd/sentinel-frontend.env.example`, con permisos `root:root 0640`. Solo contiene la URL privada del backend (`http://10.88.0.1:8000`), la ruta de datos local y el puerto; no lleva credenciales ni `SECRET_KEY`.
5. Instalar y habilitar `systemd/sentinel-frontend.service`; confirmar `curl -f http://127.0.0.1:3001/login` y que Node escucha solo en loopback.
6. Crear un virtual host separado para `sentinel.pinguinoseguro.cl`, sin cambiar los otros sitios. Las rutas web/REST van al Next.js local; solo `/api/v1/telemetry` va a Cortex por `10.88.0.1:8001` sobre WireGuard. Mover el registro A de Sentinel de Fenix a Kingu y obtener/instalar certificado TLS para ese hostname.
7. Ejecutar `nginx -t`; solo si pasa, recargar Nginx sin detenerlo. Verificar login, rutas BFF, TLS público, WebSocket y logs.

## Criterios de aceptación

- La web pública sigue respondiendo con TLS a través de Nginx en Kingu.
- Next.js corre en Kingu y escucha únicamente en `127.0.0.1:3001`; se conecta a FastAPI por WireGuard.
- FastAPI acepta TCP/8000 y Cortex TCP/8001 solo desde Kingu por WireGuard; no existe ruta pública directa a esos servicios.
- Las bases de datos solo aceptan conexiones desde servicios autorizados dentro de Fenix.
- Solo los contenedores `postgres`, `redis`, `backend` y `cortex` de Sentinel se inician en Fenix; los otros stacks permanecen activos e intactos.
- FastAPI y Cortex solo son accesibles desde Kingu por WireGuard; la web pública sirve TLS desde Kingu.

## Rollback

1. Si falla salud o acceso tras el cambio, restaurar el upstream Nginx anterior, ejecutar `nginx -t` y recargar; Node permanece limitado a loopback.
2. Si falla la API, parar únicamente los servicios Sentinel iniciados en Fenix; conservar volúmenes y otros proyectos.
3. Mantener las bases de datos y sus volúmenes intactos durante el rollback de frontend.
4. Registrar versión, hora, chequeos y resultado en el registro de cambios antes de cerrar la ventana.

## Regla de producción

La preparación y compilación se hacen en Fenix. Los únicos nodos de despliegue de esta guía son Fenix y Kingu. Todo cambio público en Kingu se aplica después de los chequeos privados y con rollback preparado.

## Registro de preflight Kingu-only — 2026-10-29

- Se publicaron `cdb4e8c7` (Sentinel) y `fc2bb06` (personalvault) en `main`. El frontend y su empaquetador no cambiaron desde el bundle preexistente `sentinel-frontend-96043b54.tar.gz` en `/tmp` de Kingu; `sha256sum -c` y la lectura íntegra del tarball pasaron.
- Preflight de solo lectura por SSH: Kingu es Debian 13, `wg0` tiene `10.88.0.2/24`, Nginx está activo y el filesystem raíz dispone de 122 GB libres. `sudo -n nginx -t` pasa. No hay cuenta/unidad/release Sentinel frontend ni `/etc/sentinel/frontend.env`.
- Desde Kingu, `http://10.88.0.1:8000/api/v1/health` y `http://10.88.0.1:8001/health` agotaron el timeout; backend y Cortex no son alcanzables en esta comprobación.
- `sentinel-ebpf.service` está inactivo y enmascarado; bpffs está montado y no hay mapas Sentinel fijados bajo `/sys/fs/bpf/sentinel` ni Guardian bajo `/sys/fs/bpf/guardian_alpha`.
- `scripts/bootstrap-sentinel-ebpf.sh` inventaría ejecutables, llena y verifica la whitelist y los comandos de recuperación antes de adjuntar Guardian en modo auditoría. No tiene modo solo-poblar. No se ejecutó: no está confirmada una consola de proveedor/recuperación fuera de banda. No se habilitó Guardian ni enforcement.
- Después del preflight se instaló en Kingu la release privada `96043b54` bajo `/opt/sentinel/frontend/releases/96043b54`, con usuario/grupo de sistema `sentinel-frontend`, datos locales y unidad `sentinel-frontend.service` habilitada y activa. `/etc/sentinel/frontend.env` se creó desde la plantilla versionada, sin credenciales. `curl http://127.0.0.1:3001/login` respondió HTTP 200; `ss` confirmó que Node escucha solo en `127.0.0.1:3001`.
- El despliegue del frontend no necesitó tocar Nginx público ni la configuración de DNS/TLS/firewall; tampoco se modificó Fenix. FastAPI y Cortex siguen inaccesibles desde Kingu, por lo que no se validaron autenticación, BFF ni WebSocket extremo a extremo. La unidad frontend está operativa, pero la integración con APIs queda pendiente.
- Guardian/eBPF permanece inactivo y la whitelist sigue sin poblarse. La comprobación de recuperación fuera de banda aplica al bootstrap eBPF, que llena/verifica whitelist y adjunta Guardian en auditoría; no es un requisito para la instalación independiente del frontend. No se ejecutó el bootstrap ni se habilitó enforcement.

## Despliegue backend privado en Fenix — 2026-10-29

- Alcance autorizado posteriormente por el usuario: backend FastAPI, Cortex y dependencias en Fenix; no replicar el frontend, que sigue en Kingu. No se modificaron Nginx, DNS, TLS ni servicios de otros proyectos.
- Commits publicados en `main`: `96f28b7b` corrige bindings PyO3 duplicados y el empaquetado del módulo; `b96a6708` añade `psycopg` para Alembic y el constructor reproducible `scripts/build-sentinel-backend-image.sh`; `cb5ce0c7` añade merge de revisiones Alembic; `6b0b2ce6` actualiza Prometheus FastAPI Instrumentator; `3b89c13f` conecta Cortex a `backend_egress` para que Docker publique su puerto; `4ceaf78d` alinea el guard de autenticación con el head canónico de Alembic.
- Imagen inicial de FastAPI: `sentinel-backend:6b0b2ce6`. El módulo `me60os_core.so` se compiló contra Python 3.11 en `rust:bookworm`; no se usa el `.so` legacy de `quantum/` ni el build del host Python 3.13 de Fenix. `docker run` confirmó importación de `quantum.yatra_core`, `SPA` y `psycopg`.
- Alembic detectó dos heads históricos; se creó una migración merge no-op que los une sin reescribir revisiones anteriores. En Fenix `alembic current` y `heads` reportan `20261029_merge_all_heads (head)`; el esquema migró y el backend inició.
- Estado comprobado en Fenix: `sentinel-backend` healthy; `sentinel-postgres`, `sentinel-redis` y `sentinel-cortex` healthy. FastAPI `10.88.0.1:8000/api/v1/health` devuelve HTTP 200 con DB/Redis healthy; Cortex `10.88.0.1:8001/health` devuelve HTTP 200. Desde Kingu `/api/v1/auth/me` devuelve HTTP 401 sin token. WebSocket `/api/v1/telemetry` devuelve 401 sin credenciales; no se validó handshake autenticado porque aún no se ha creado el administrador inicial.
- Puertos FastAPI/Cortex publicados en `10.88.0.1:8000/8001`; `SENTINEL-DOCKER-USER` registró paquetes permitidos de Kingu (`10.88.0.2`) por `wg0` en ambos puertos. PostgreSQL y Redis no tienen publicación activa de host. Desde Kingu, con ruta pública por `enp1s0` (no WireGuard), las conexiones TCP a la IP pública de Fenix agotaron timeout en 8000, 8001, 5432 y 6379.
- Los contenedores `impacta-backend`, `impacta-redis`, `impacta-db` y `laespiguita-db` permanecieron activos. `/etc/sentinel/backend.env` sigue `root:docker`, modo `0640`; no se copiaron ni imprimieron secretos.
- Pendiente antes de abrir el sitio: crear el primer administrador con `python -m app.bootstrap_admin`; luego validar login y WebSocket autenticado desde Kingu. El frontend sigue privado en loopback; no se cambiaron DNS ni vhost público. Guardian/eBPF sigue inactivo y whitelist no poblada.
- El primer intento de bootstrap no creó filas: `ensure_schema_current()` comparaba la base en `20261029_merge_all_heads` con el head obsoleto `dd222c78d329` y lanzó `HTTPException` antes de validar los campos y añadir el usuario. Se corrigió en `4ceaf78d` para exigir el head canónico actual; se añadieron pruebas y las pruebas enfocadas de auth/bootstrap pasaron (12). La entrada de nombre también debe completarse en los dos campos obligatorios, `first_name` y `last_name`.
- Despliegue de corrección comprobado en Fenix: imagen `sentinel-backend:4ceaf78d`, reconstruida con `scripts/build-sentinel-backend-image.sh`; se recreó solo `sentinel-backend` con `--no-deps`. El contenedor quedó `healthy`, `/api/v1/health` respondió HTTP 200 y la llamada directa a `ensure_schema_current()` pasó contra la DB real en `20261029_merge_all_heads`. Postgres/Redis/Cortex siguieron `healthy`; DB mantiene 0 usuarios y 0 superusuarios. La cuenta de administrador aún no existe; no se volvió a ejecutar el bootstrap.
