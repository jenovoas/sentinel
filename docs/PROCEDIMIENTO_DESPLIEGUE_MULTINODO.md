# Procedimiento estándar de despliegue multi-nodo de Sentinel

## Alcance y topología

Este procedimiento aplica a `main` y al entorno systemd:

- **Fenix (`10.88.0.1`)**: build, Docker Compose, FastAPI, Cortex, PostgreSQL y Redis.
- **Kingu (`10.88.0.2`)**: Next.js bajo systemd, Nginx y TLS público.
- **WireGuard (`10.88.0.0/24`)**: transporte privado entre ambos nodos. Los puertos FastAPI/Cortex/n8n se publican en la IP WireGuard de Fenix; `DOCKER-USER` debe limitar el origen a Kingu.
- **Hercules/DNS**: solo se modifica si el alcance incluye explícitamente un cambio DNS.

No mezclar con `alpine_fenix`/OpenRC. No activar Guardian/eBPF ni enforcement como parte implícita del despliegue de la aplicación; su whitelist y recuperación fuera de banda tienen un preflight separado.

## 1. Fijar alcance, versión y aceptación

Antes de cambiar un nodo, registrar:

1. Componentes y nodos autorizados, dominios y rutas que se esperan modificar.
2. SHA de Git que se desplegará; rama `main`, árbol limpio y relación con `origin/main`.
3. Checks de aceptación por capa: build, servicio local, WireGuard, proxy/TLS, autenticación, WebSocket y aislamiento de puertos.
4. Responsable disponible para credenciales humanas y pasos manuales, como alta de owner n8n.
5. Qué no forma parte del alcance. DNS, firewall compartido, DB/migraciones, eBPF y servicios de otros proyectos no se cambian por inferencia.

## 2. Preflight de solo lectura

1. Desde el equipo de trabajo:

   ```sh
   git fetch origin
   git status --short --branch
   git branch --show-current
   git rev-parse HEAD
   git rev-parse origin/main
   ```

   Detenerse si la rama no es `main`, el árbol no está limpio o la versión objetivo no está publicada.
2. Confirmar SSH por el puerto operativo 4222 a ambos nodos y que Fenix conserva una ruta de recuperación independiente antes de tocar firewall, SSH, WireGuard o entrada pública.
3. Registrar en cada nodo: fecha UTC, hostname, OS/runtime, interfaces y rutas WireGuard, espacio libre, estado de Nginx/systemd/Firewalld y servicios Sentinel.
4. En Fenix, registrar contenedores, etiquetas Compose, imágenes/digests, bindings y redes. Comparar el estado real con `docker-compose.fenix.yml`; no inferir propiedad por el nombre de un puerto. Identificar qué contenedor escucha en cada puerto.
5. Guardar el head de Alembic y confirmar backup reciente/restore probado antes de cualquier migración o cambio de datos. No leer ni imprimir archivos de secretos.
6. Verificar reglas efectivas `DOCKER-USER`/nftables y sus contadores. Las reglas `INPUT` o la zona Firewalld por sí solas no prueban aislamiento de puertos DNAT de Docker.
7. Registrar DNS A/AAAA, vhost, certificado/SAN, upstreams y salud pública existentes. Conservar nombres y sitios ajenos.
8. Validar Compose sin mostrar secretos:

   ```sh
   docker compose --env-file /etc/sentinel/backend.env \
     -f docker-compose.fenix.yml config --quiet
   ```

Si falta un backup, acceso independiente, artefacto verificable o rollback viable, no iniciar el cambio.

## 3. Compilar y verificar artefactos en Fenix

1. Actualizar el checkout solo hasta el SHA autorizado y comprobar de nuevo rama, SHA y árbol limpio.
2. Ejecutar los chequeos existentes para los componentes modificados. No compilar desde un checkout distinto al SHA registrado.
3. Etiquetar las imágenes con el SHA de código, nunca con `latest`:

   ```sh
   ./scripts/build-sentinel-backend-image.sh sentinel-backend:<sha>
   ./scripts/build-sentinel-cortex-image.sh sentinel-cortex:<sha>
   ```

4. Para Next.js, instalar dependencias bloqueadas, generar build y bundle en Fenix, calcular SHA-256 y transferir bundle y checksum a Kingu por WireGuard. Verificar checksum antes de extraer.
5. Registrar SHA Git, tags/digests, checksum del frontend y salida de build. No copiar `.env`, llaves, credenciales ni datos de usuario al artefacto.

## 4. Desplegar servicios internos en Fenix

1. Capturar estado anterior: tag/digest de cada contenedor, estado/health, head de DB, puertos y los valores no secretos necesarios para restaurar referencias de imagen.
2. Antes de una migración, confirmar compatibilidad, backup y método de reversión. FastAPI aplica `alembic upgrade head` en su entrypoint; validar los heads antes y después y actualizar solo `backend` si ese es el único componente cambiado.
3. Actualizar en `/etc/sentinel/backend.env` únicamente los tags de imagen aprobados y necesarios; preservar dueño `root:docker`, modo `0640` y el resto del archivo sin imprimirlo.
4. Levantar solo servicios autorizados. Para actualización exclusiva de una aplicación:

   ```sh
   docker compose --env-file /etc/sentinel/backend.env \
     -f docker-compose.fenix.yml up -d --no-build --no-deps <servicio>
   ```

   Para primera instalación, iniciar dependencias primero y luego aplicaciones con `depends_on` saludable. Nunca ejecutar `down` global ni borrar volúmenes.
5. Verificar tag/digest desplegado, proyecto Compose, estado `healthy`, logs de arranque, mounts requeridos y persistencia. Para Cortex, además verificar `GET /api/v1/crystal_runtime/status`: `active=true`, `runtime.active=true`, `shm_active=true`, ticks y sincronizaciones crecientes, y checkpoint duradero en el volumen persistente.
6. Desde Kingu, comprobar APIs privadas por WireGuard. Desde un segundo peer autorizado y desde el camino público, comprobar que los puertos internos y bases de datos no aceptan conexiones. La ruta pública esperada pasa por Nginx en Kingu.

## 5. Desplegar frontend en Kingu

1. Crear una release inmutable en `/opt/sentinel/frontend/releases/<sha>` y verificar el SHA-256 recibido.
2. Aplicar dueño/permisos de la unidad `sentinel-frontend`; configurar solo la URL privada de FastAPI y opciones no secretas necesarias. No poner tokens humanos ni secretos de backend en el bundle.
3. Preparar el enlace temporal y cambiar `current` de forma atómica. Reiniciar solo `sentinel-frontend.service`.
4. Confirmar servicio `active/enabled`, `/login` local HTTP 200 y listener exclusivamente en `127.0.0.1:3001`.
5. Solo si el alcance incluye publicar o cambiar el vhost: modificar un archivo aislado por hostname, revisar `nginx -t`, recargar Nginx sin detenerlo y verificar proxy, WebSocket y certificado con SNI. DNS se cambia en el primario autoritativo, se incrementa serial y se comprueban primario, secundarios y resolución pública.

## 6. Verificación extremo a extremo

Registrar timestamp y resultado por separado:

| Capa | Verificación mínima |
|---|---|
| Frontend | Dominio y `/login` devuelven 200; build/release coincide con SHA registrado; Node solo en loopback. |
| TLS | `curl` valida cadena sin `-k`; SAN corresponde al hostname y certificado está vigente. HTTP redirige a HTTPS. |
| BFF/FastAPI | Health 200 y dependencias saludables; `/api/auth/me` sin sesión devuelve 401 esperado. Prueba de credenciales inválidas solo con datos sintéticos y sin registrar cuerpos sensibles. |
| Cortex/WebSocket | `/health` 200; endpoint de runtime activo y métricas dinámicas; Origin autorizado sin token devuelve 401 y Origin ajeno 403; handshake autenticado requiere sesión aprobada por el usuario. |
| Red | Kingu llega a los upstreams privados; peer VPN distinto no llega a 8000/8001/5678; PostgreSQL/Redis no tienen binding accesible desde la VPN o Internet. |
| Nginx | `nginx -t` exitoso; vhost usa upstreams Sentinel previstos y no altera sitios ajenos; logs sin errores nuevos. |
| Integridad | Contenedores no relacionados mantienen estado; volúmenes y DB persisten; no aparece un contenedor Sentinel fuera del proyecto Compose. |

HTTP 200 de `/health` solo valida salud del proceso. No demuestra que se desplegó el SHA correcto, que el runtime opcional esté activo, que la autenticación funcione ni que el sistema completo esté aceptado.

## 7. Rollback

1. Revertir solo el componente afectado: referencia de imagen anterior y `up -d --no-build --no-deps <servicio>` en Fenix, o `current` a la release anterior y restart de la unidad en Kingu.
2. Si un vhost fue cambiado, restaurar el archivo aislado, ejecutar `nginx -t` y recargar. Revertir únicamente el registro DNS modificado si se incluyó DNS.
3. No eliminar volúmenes ni revertir migraciones destructivamente. Restaurar DB solo desde el backup verificado y con autorización del operador.
4. Repetir healthchecks/red y comprobar que los otros proyectos siguen sanos.

## 8. Cierre y trazabilidad

El despliegue solo se cierra cuando se registran en `docs/` y en la vault:

- fecha UTC, nodos, SHA Git, ramas y artefactos/digests/checksums;
- cambio exacto por nodo y servicio, estado anterior y posterior;
- comandos ejecutados y evidencia resumida de runtime, logs, HTTP/TLS, DB, firewall y red;
- alcance no verificado, tareas manuales pendientes y resultado del rollback plan;
- confirmación explícita de qué servicios y funciones quedan activos.

Preparación, build, despliegue y publicación son estados diferentes. No declarar éxito basándose solo en que un comando terminó o en que un contenedor está `healthy`.
