# Despliegue separado: Fenix y Kingu

## Objetivo

Separar la superficie pública de los servicios internos:

- **Kingu** (`10.88.0.2`): entrada pública, Nginx, TLS y proxy inverso. No aloja contenedores de aplicación ni bases de datos.
- **Kingu**: ejecuta Next.js como servicio systemd, enlazado solo a `127.0.0.1:3001`.
- **Fenix** (`10.88.0.1`): contenedores de aplicación y backend, bases de datos, compilación y servicios internos.
- **WireGuard** (`10.88.0.0/24`): único camino de Kingu a los servicios internos de Fenix.

El navegador solo conecta con Nginx en Kingu. Nginx envía todas las rutas, incluidas `/api/*`, al BFF Next.js local. El BFF conecta al backend Python por WireGuard. Fenix publica FastAPI solo en `10.88.0.1:8000`; el firewall debe aceptar ese puerto únicamente desde Kingu (`10.88.0.2`). Cortex, Postgres y Redis permanecen sin puertos publicados.

Esta guía aplica a `main` y systemd. No mezclar con `alpine_fenix`/OpenRC.

## Estado observado el 2026-10-29

La última observación registrada no coincide con el objetivo y debe actualizarse en el preflight antes del despliegue:

- Kingu ejecuta Nginx en `:80/:443` y un contenedor `pinguinoseguro-web` en `127.0.0.1:3000`; Nginx envía el tráfico a ese puerto local.
- Fenix tiene Docker y los artefactos `.next`, pero no hay contenedores activos ni listeners en `3000`, `5432` o `6379`. Faltan los archivos de entorno requeridos por los Compose observados.
- La unidad `sentinel-ebpf.service` está enmascarada en Kingu. No hay un Guardian fijado en bpffs actualmente.

No asumir que un archivo Compose presente equivale a un servicio desplegado o saludable.

## Secuencia de despliegue

### 1. Preflight y recuperación

1. Confirmar SSH independiente a ambos nodos y acceso de consola del proveedor a Kingu.
2. Registrar salud HTTP/TLS pública, estado de Nginx, túnel WireGuard, servicios de Fenix, contenedores y bases de datos.
3. Confirmar copias de seguridad y espacio de disco. No imprimir valores de `.env`, secretos ni configuración privada en terminales o logs. Rotar las credenciales del frontend expuestas durante el diagnóstico antes de recrearlo o migrar su entorno.
4. Mantener disponible el frontend actual de Kingu hasta que el servicio systemd nuevo pase los chequeos de salud.

### 2. Preparar servicios internos en Fenix

1. Instalar los secretos directamente en Fenix mediante un canal seguro; no versionarlos ni copiarlos a salidas de comandos.
2. Levantar primero las bases de datos en una red Docker interna, con volúmenes persistentes y healthchecks.
3. Integrar y validar `config/nftables/sentinel-backend-acl.nft` en el ruleset existente de Fenix antes de exponer el backend. Debe aceptar TCP/8000 solo desde `10.88.0.2` hacia `10.88.0.1` y rechazar el resto, tanto en tráfico local como en el reenviado por Docker.
4. Levantar FastAPI y Cortex en la red Docker interna. Compose publica FastAPI únicamente en `10.88.0.1:8000`; no publica Cortex.
5. Desde Kingu, comprobar por WireGuard `/api/v1/health` y `/api/v1/auth/me` (sin token debe responder 401). Desde una red externa, confirmar que FastAPI, Cortex, Postgres y Redis no son accesibles.

#### Migraciones e identidad inicial

El entrypoint aborta si `alembic upgrade head` falla. La adopción del esquema legacy solo procede cuando las tablas, tipos, restricciones y políticas RLS coinciden exactamente con el baseline conocido; si encuentra un esquema parcial o distinto, detiene el arranque para revisión manual sin continuar con la migración. Después de que Alembic llegue al head esperado y exista una organización activa, el primer administrador se crea manualmente dentro del contenedor backend con `python -m app.bootstrap_admin`. El comando solicita la contraseña sin eco y se niega a crear otra cuenta superusuario si ya existe una. No habilitar un registro público para sustituir este aprovisionamiento.

### 3. Cambiar la entrada pública en Kingu

1. En Fenix, desde `main`, ejecutar `npm ci` y `npm run build` dentro de `frontend/`; crear el bundle con `scripts/package-frontend.sh /tmp/sentinel-frontend.tar.gz`.
2. Instalar Node.js 22 en Kingu (`/usr/bin/node`) y crear la cuenta de servicio sin login `sentinel-frontend`. Transferir el tarball y su `.sha256` por WireGuard, y verificar `sha256sum -c` antes de extraer. Crear `/opt/sentinel/frontend/releases/<versión>`, extraer ahí y dejar el bundle legible por `sentinel-frontend` (por ejemplo `root:sentinel-frontend`, directorios `0750`, archivos `0640`). Preparar el enlace con `ln -s /opt/sentinel/frontend/releases/<versión> /opt/sentinel/frontend/.current-<versión>` y reemplazarlo atómicamente con `mv -Tf /opt/sentinel/frontend/.current-<versión> /opt/sentinel/frontend/current`.
3. Crear `/var/lib/sentinel-frontend/host-metrics/{data,reports}` en Kingu, propiedad de `sentinel-frontend`. Configurar allí el colector local de métricas de Kingu; el bundle no incluye directorios de datos.
4. Crear `/etc/sentinel/frontend.env` desde `config/systemd/sentinel-frontend.env.example`, con permisos `root:root 0640`. Solo contiene la URL privada del backend, la ruta de datos local y el puerto; no lleva credenciales ni `SECRET_KEY`.
5. Instalar y habilitar `systemd/sentinel-frontend.service`; confirmar `curl -f http://127.0.0.1:3001/login` y que Node escucha solo en loopback, dejando disponible el frontend anterior en `:3000` para rollback.
6. Incluir `config/nginx/sentinel-frontend-location.conf` en el virtual host HTTPS existente. Todas las rutas, incluidas `/api/*`, deben ir al Next.js local; no agregar proxy directo al backend.
7. Ejecutar `nginx -t`; solo si pasa, recargar Nginx sin detenerlo. Verificar login, rutas BFF, TLS público y logs. Mantener el upstream y contenedor antiguos durante la ventana de validación; retirarlos después de confirmar.

### 4. Activar Sentinel en Kingu

No activar el LSM fail-closed hasta terminar el cambio de topología y tener un canal de recuperación comprobado.

1. En Fenix, construir un paquete versionado: `scripts/package-sentinel-ebpf.sh /tmp/sentinel-ebpf-bundle.tar.gz`. Transferir el paquete a Kingu, extraerlo en un directorio temporal y ejecutar su `install-sentinel-ebpf.sh`. El instalador verifica arquitectura y archivos, instala juntos objeto, bootstrap, modo, rollback y unidad systemd; no habilita ni inicia servicios.
2. El bootstrap inventaría ejecutables del host, procesos activos y raíces Docker montadas. Valida rutas críticas de SSH, shells, `sudo`, consola, Nginx y herramientas de contenedores; no depende de una lista estática.
3. Poblar la whitelist antes del attach y comprobar que `bpftool` aceptó el lote, el número de entradas y las claves críticas. Si la población o validación falla, abortar sin adjuntar.
4. El mapa `guardian_mode_map` parte en modo auditoría: el attach permite ejecutables desconocidos y los registra. El arranque de systemd y los reinicios permanecen en este modo.
5. Tras autorizar la ventana de producción, quitar la máscara de `sentinel-ebpf.service` y habilitarlo. El inicio normal solo adjunta en auditoría; no activa enforcement.
6. Solo para una prueba explícita de enforcement, ejecutar `/usr/local/libexec/sentinel-guardian-mode enforce`. Esta acción vuelve a validar las rutas críticas y arma primero un rollback automático de cinco minutos.
7. Con una segunda estación, probar una conexión SSH nueva, `sudo`, `systemctl`, el acceso por WireGuard y la página pública. Ejecutar `/usr/local/libexec/sentinel-guardian-mode confirm` únicamente después de pasar esas comprobaciones; si no se confirma, el timer vuelve a auditoría.
8. `systemctl stop sentinel-ebpf.service` pone el mapa en auditoría y quita el enlace BPF y sus mapas fijados. La unidad nunca persiste el enforcement por sí sola.

## Criterios de aceptación

- La web pública sigue respondiendo con TLS a través de Nginx en Kingu.
- Next.js corre en Kingu y escucha únicamente en `127.0.0.1:3001`; se conecta a FastAPI por WireGuard.
- FastAPI acepta TCP/8000 solo desde Kingu; no existe ruta pública directa a FastAPI ni Cortex.
- Las bases de datos solo aceptan conexiones desde servicios autorizados dentro de Fenix.
- Un reinicio de un contenedor de aplicación en Fenix y una recarga de Nginx en Kingu no dependen de rutas ausentes de la whitelist.
- El mapa de Guardian se valida antes del attach; una whitelist incompleta aborta el despliegue.
- Un attach normal o reinicio deja Guardian en auditoría y no bloquea rutas desconocidas.
- Una segunda sesión SSH y la ruta de rollback funcionan durante la prueba de enforcement.

## Rollback

1. Si falla salud o acceso tras el cambio, restaurar el upstream Nginx anterior, ejecutar `nginx -t` y recargar; Node permanece limitado a loopback.
2. Si falla el acceso después del attach LSM, dejar que opere el rollback automático o usar la consola del proveedor para retirar el pin del enlace Guardian.
3. Mantener las bases de datos y sus volúmenes intactos durante el rollback de frontend.
4. Registrar versión, hora, chequeos y resultado en el registro de cambios antes de cerrar la ventana.

## Regla de producción

La preparación, compilación y validación se hacen en Fenix. Cualquier cambio de producción en Kingu requiere orden explícita de despliegue y una ventana con rollback preparado.
