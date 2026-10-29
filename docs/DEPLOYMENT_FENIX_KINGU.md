# Despliegue separado: Fenix y Kingu

## Objetivo

Separar la superficie pública de los servicios internos:

- **Kingu** (`10.88.0.2`): entrada pública, Nginx, TLS y proxy inverso. No aloja contenedores de aplicación ni bases de datos.
- **Fenix** (`10.88.0.1`): contenedores de aplicación y backend, bases de datos, compilación y servicios internos.
- **WireGuard** (`10.88.0.0/24`): único camino de Kingu a los servicios internos de Fenix.

Interpretación operativa: “frontend en Kingu” significa que Kingu termina TLS y recibe el tráfico público. El proceso Next.js puede estar contenerizado en Fenix; Nginx en Kingu lo alcanza por WireGuard. Las bases de datos permanecen en una red interna de contenedores en Fenix y no se publican en la interfaz pública ni en la VPN salvo que exista una necesidad documentada.

Esta guía aplica a `main` y systemd. No mezclar con `alpine_fenix`/OpenRC.

## Estado observado el 2026-10-29

La instalación real no coincide con el objetivo:

- Kingu ejecuta Nginx en `:80/:443` y un contenedor `pinguinoseguro-web` en `127.0.0.1:3000`; Nginx envía el tráfico a ese puerto local.
- Fenix tiene Docker y los artefactos `.next`, pero no hay contenedores activos ni listeners en `3000`, `5432` o `6379`. Faltan los archivos de entorno requeridos por los Compose observados.
- La unidad `sentinel-ebpf.service` está enmascarada en Kingu. No hay un Guardian fijado en bpffs actualmente.

No asumir que un archivo Compose presente equivale a un servicio desplegado o saludable.

## Secuencia de despliegue

### 1. Preflight y recuperación

1. Confirmar SSH independiente a ambos nodos y acceso de consola del proveedor a Kingu.
2. Registrar salud HTTP/TLS pública, estado de Nginx, túnel WireGuard, servicios de Fenix, contenedores y bases de datos.
3. Confirmar copias de seguridad y espacio de disco. No imprimir valores de `.env`, secretos ni configuración privada en terminales o logs. Rotar las credenciales del frontend expuestas durante el diagnóstico antes de recrearlo o migrar su entorno.
4. Mantener disponible el despliegue actual de Kingu hasta que el destino en Fenix pase los chequeos de salud.

### 2. Preparar servicios internos en Fenix

1. Instalar los secretos directamente en Fenix mediante un canal seguro; no versionarlos ni copiarlos a salidas de comandos.
2. Levantar primero las bases de datos en una red Docker interna, con volúmenes persistentes y healthchecks.
3. Levantar APIs/backend en esa misma red y verificar salud, migraciones, persistencia y conectividad a las bases.
4. Levantar Next.js en Fenix. Publicar su puerto únicamente en `10.88.0.1` o restringirlo por firewall para permitir solo el origen Kingu por WireGuard.
5. Desde Kingu, verificar por WireGuard el endpoint de salud y las rutas del frontend y API. Confirmar desde una red externa que los puertos internos de Fenix no son accesibles.

### 3. Cambiar la entrada pública en Kingu

1. Cambiar el upstream de Nginx de `127.0.0.1:3000` al endpoint privado de Fenix acordado.
2. Ejecutar `nginx -t`; solo si pasa, recargar Nginx sin detenerlo.
3. Verificar por el dominio público TLS, rutas del frontend/API, WebSocket si aplica, logs de Nginx y salud del servicio en Fenix.
4. Mantener el contenedor antiguo de Kingu como rollback solo durante la ventana de validación. Tras confirmar el tráfico por Fenix, detenerlo y retirar sus secretos locales de forma segura.

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
- Kingu alcanza frontend y backend de Fenix por WireGuard; los servicios internos no quedan expuestos a Internet.
- Las bases de datos solo aceptan conexiones desde los servicios autorizados en Fenix.
- Un reinicio de un contenedor de aplicación en Fenix y una recarga de Nginx en Kingu no dependen de rutas ausentes de la whitelist.
- El mapa de Guardian se valida antes del attach; una whitelist incompleta aborta el despliegue.
- Un attach normal o reinicio deja Guardian en auditoría y no bloquea rutas desconocidas.
- Una segunda sesión SSH y la ruta de rollback funcionan durante la prueba de enforcement.

## Rollback

1. Si falla salud o acceso tras el cambio de upstream, restaurar la configuración Nginx anterior, ejecutar `nginx -t` y recargar.
2. Si falla el acceso después del attach LSM, dejar que opere el rollback automático o usar la consola del proveedor para retirar el pin del enlace Guardian.
3. Mantener las bases de datos y sus volúmenes intactos durante el rollback de frontend.
4. Registrar versión, hora, chequeos y resultado en el registro de cambios antes de cerrar la ventana.

## Regla de producción

La preparación, compilación y validación se hacen en Fenix. Cualquier cambio de producción en Kingu requiere orden explícita de despliegue y una ventana con rollback preparado.
