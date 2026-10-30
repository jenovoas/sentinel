# Procedimiento estándar de despliegue multi-nodo de Sentinel

## Alcance y topología

Este procedimiento aplica a `main` y al entorno systemd:

- **Fenix (`10.88.0.1`)**: backend central de API/datos y servicios compartidos: FastAPI, Cortex, PostgreSQL, Redis y QHC. Mantiene como destino central de los datos y eventos de Marte.
- **Kingu (`10.88.0.2`)**: Next.js bajo systemd, Nginx y TLS público.
- **Marte (`10.88.0.6`)**: backend de seguridad/observabilidad: Guardian/eBPF, Grafana, Mimir, Prometheus, TruthSync y Loki. Opera por WireGuard contra Fenix (`10.88.0.1`) como backend Sentinel central/fuente de verdad; no expone APIs Sentinel al público.
- **WireGuard (`10.88.0.0/24`)**: transporte privado entre nodos. Los puertos FastAPI/Cortex/n8n se publican en la IP WireGuard de Fenix; `DOCKER-USER` debe limitar cada origen y puerto explícitamente autorizado.
- **Hercules/DNS**: solo se modifica si el alcance incluye explícitamente un cambio DNS.

No mezclar con `alpine_fenix`/OpenRC. No activar Guardian/eBPF ni enforcement como parte implícita del despliegue de la aplicación; su whitelist y recuperación fuera de banda tienen un preflight separado.

SOMA (`soma_orchestrator`/`soma_worker`) queda fuera de este despliegue hasta autorización específica. `qhc-agent` es un servicio independiente requerido por Cortex; utiliza `/run/soma/qhc.sock` como ruta IPC, pero no inicia ni necesita la orquestación SOMA.

El procedimiento incorpora el cotejo de papers y experimentos registrado en [`ARQUITECTURA_FUNCIONAL_SENTINEL_Y_EXPERIMENTOS.md`](ARQUITECTURA_FUNCIONAL_SENTINEL_Y_EXPERIMENTOS.md). Antes de agregar un proceso al despliegue, identificar su experimento/cita, ruta Rust/Python activa, consumidor y evidencia runtime. Un paper, un módulo compilable o un benchmark aislado no son evidencia de servicio desplegado.

### Perfil operativo conocido de Marte

La memoria persistente registra para Marte Debian 13 amd64, kernel `7.3.0-ifenix` activo y administración SSH por TCP 4222 (sin listener SSH 22 en la verificación del 2026-10-30). También registra una intervención para instalar Firewalld 2.3.1; la configuración vigente de zonas/reglas de Marte no fue verificada directamente en esta auditoría Sentinel. Jaime confirmó que tiene acceso al nodo y que usa Firewalld. Un `No route to host` observado desde otra ruta/host describe ese intento, no demuestra indisponibilidad global de Marte.

El backend de seguridad/observabilidad en Marte ejecuta Guardian/eBPF en auditoría y aloja Grafana, Mimir, Prometheus, TruthSync y Loki. Estos módulos observan y consultan las fuentes Sentinel de Fenix por WireGuard; FastAPI/Cortex, PostgreSQL, Redis y QHC permanecen como backend central de aplicación/datos en Fenix. Fijar el endpoint y dirección de datos por módulo antes de desplegar. FastAPI Fenix ofrece `POST /api/v1/cortex/events` con contrato `event_type`, `source`, `data` y autenticación `X-Sentinel-Token` para la ingesta de eventos de seguridad. El token se provisiona por canal seguro y no se incluye en logs, argumentos o bundles.

El reparto entre Fenix (backend Sentinel central) y Marte (backend de seguridad/observabilidad) es intencional. No duplicar PostgreSQL/Redis ni levantar una segunda autoridad de Cortex en Marte salvo que se diseñe y acepte explícitamente replicación, consistencia y failover. Las consultas de Marte sobre Sentinel deben usar las direcciones privadas de Fenix, nunca localhost ni APIs públicas.

### Mapa funcional y criterio de aceptación

| Módulo | Ubicación/relación objetivo | Evidencia para aceptarlo |
|---|---|---|
| FastAPI, PostgreSQL, Redis | Backend de Sentinel en Fenix | Contenedores saludables; migración en head; APIs privadas alcanzables desde pares permitidos. |
| Cortex Rust | Backend de Sentinel en Fenix | Imagen fijada por SHA, `/health`, logs y endpoints autenticados validados. |
| QHC | Servicio compartido local en Fenix para Sentinel y MyCNet | `sentinel-qhc-agent` activo; probar `SNAPSHOT` con la identidad de Cortex y la de MyCNet; snapshot reciente; Cortex reporta `QHC=true`. La conectividad del socket no sustituye verificar el consumidor de cada aplicación. |
| Backend de borde Marte | Marte (`10.88.0.6`), reporta y entrega a Fenix | Agentes de seguridad, métricas y logs configurados con destino central `10.88.0.1`; eventos autenticados aceptados y visibles en Fenix. |
| Observabilidad/TruthSync | Grafana, Mimir, Prometheus, TruthSync y Loki en Marte | Confirmar endpoint, persistencia, autenticación y flujo de cada módulo por WireGuard contra Fenix. |
| Colectores host | `node_exporter` y Grafana Alloy en Marte y Fenix, según fuentes requeridas | Métricas y logs identifican su nodo origen y llegan a Prometheus/Loki en Marte por WireGuard. No se usa DNS Compose (`prometheus`, `loki`) entre hosts. Promtail está EOL y no se usa. |
| Matriz/cristales, memorias SHM y dual lane A/B | Runtime Cortex en Fenix | `CrystalRuntime` activo, SHM de ambas lanes y semillas presentes, sincronizaciones crecientes y checkpoint persistente. |
| Cristal isocrónico DTC | Runtime Cortex en Fenix | Tick DTC observable y contrato IPC probado. Las constantes actuales de SHM no bastan: el runtime debe crear/actualizar el objeto DTC compartido. |
| PAI-60 | Biblioteca/camino de inyección Cortex | Confirmar conversión y amplitud desde el camino activo; mantener la escala acordada y no inferirla desde benchmarks. |
| FPU | Referencia de CPU/benchmarks, no daemon independiente | Tratar cada uso de punto flotante por ruta de producción; no declarar “FPU desplegada” como módulo. |
| Dual Lane Security/Observability | Backend de eventos | Probar que eventos reales atraviesan las dos lanes, WAL y almacenamiento; la mera presencia de la biblioteca no demuestra integración. |
| eBPF/Guardian en Marte | Sensor local en modo auditoría; eventos hacia Fenix | Verificar whitelist/rutas críticas y recuperación fuera de banda antes de adjuntar. No activar enforcement sin autorización separada. Transporte autenticado a Fenix y prueba de recepción antes de darlo por integrado. |
| `neural-guard` | Worker Rust de correlación; ubicación pendiente de decisión | El código consume Prometheus, Loki, Redis y alerta por n8n. La definición Compose actual usa nombres internos de Fenix; no se puede mover a Marte sin URL/ruta segura para cada dependencia. |
| Frontend Next.js | Kingu | BFF del navegador hacia APIs privadas de Fenix; sesiones/CSRF, páginas usadas y errores de upstream revisados. No conecta directamente el browser a Fenix. |
| Crystal Cipher | Sin nodo asignado hasta cerrar diseño e integración | No desplegar para datos reales: no hay consumidor productivo y la clave actual se deriva de estado determinista del cristal/pulso sin gestión de secreto. Antes se requiere contrato de claves, rotación/reinicio, unicidad de nonce por clave y pruebas con SHM/ring buffer. |
| Hardware optomecánico/fotónico/fonónico de los papers | No es parte del despliegue software | `optomechanical.rs`, `LiquidLattice` y las memorias de software no instalan ni controlan los dispositivos físicos de los papers; exigir driver y sensor físico antes de declarar integración de hardware. |

SOMA y sus workers no son componentes de este mapa. La evidencia se clasifica como `activo`, `implementado pero no conectado`, `pendiente` o `no verificado`; no se eleva un módulo de estado por su nombre o por un healthcheck general.

### Gates basados en los experimentos y papers

1. **Reloj/memoria:** papers Nandi–Vitiello y EXP-001/028 sustentan el kernel de historia; revisar `S60PID` y `CrystalRuntime`. Para aceptación operativa en Fenix se requieren tick DTC observable, unidades/época de QHC acordadas, sincronizaciones SHM A/B y checkpoint restaurable. Las constantes `DTC_CLOCK_SHM` no cuentan como contrato IPC implementado.
2. **PAI-60:** aceptar el camino activo por amplitud observada y escala documentada. `inject(i64)`/`inject_pai` reescalan; no suministrar `SPA::to_raw()`. Los benchmarks FPU/PAI son diagnósticos del algoritmo, no servicios ni sustituto de la traza de Cortex.
3. **Memoria fonónica/líquida:** EXP-009/016 y los papers citados justifican inspeccionar la ruta Cortex→`LiquidLattice`/`NeuralMemory`→checkpoint. El software no equivale a una memoria fotónica o metasuperficie fonónica física. Verificar el origen real del ring buffer y la recuperación desde el volumen; no aceptar un smoke bench como prueba de producción.
4. **Seguridad eBPF:** los papers citados describen patrones de IDS/verificación, no acreditan que Guardian esté adjunto en Marte. La aceptación requiere carga local en modo auditoría, whitelist/rutas críticas, recuperación fuera de banda y forwarder autenticado a Fenix con evento recibido y correlacionable.
5. **Dos tipos de Dual Lane:** validar `CrystalRuntime` A/B por SHM separadamente de `DualLaneRouter` Security/Audit + Observability. Para el segundo, demostrar que eventos reales pasan por la clasificación, WAL síncrono de seguridad y colector de observabilidad. La existencia del `dual_lane_bench` no satisface el gate.
6. **TruthSync:** mantener filtro integrado en Fenix y Truth Core como servicio separado en Marte. No desplegar el artefacto histórico sin corregir su procesamiento simulado/score fijo ni abrir ruta directa desde navegador a Marte.

### Backend de seguridad y observabilidad en Marte

1. **Seguridad:** Guardian/eBPF opera en el kernel de Marte. Instalar y cargar en auditoría solo tras verificar BTF/LSM, whitelist completa y recuperación fuera de banda. Enforcement requiere autorización separada.
2. **Eventos:** implementar/configurar un agente que lea el ring buffer local, normalice cada evento y lo envíe autenticado a FastAPI Fenix (`POST /api/v1/cortex/events`). `sentinel-ebpf-forwarder.service` actual (`bpftool prog tracelog`) solo presenta trazas en un log local; no es este forwarder de red.
3. **Prometheus:** desplegarlo en Marte para consultar por WireGuard métricas del backend Fenix (`10.88.0.1:8000` FastAPI, `10.88.0.1:8001` Cortex) y exporters aprobados en Fenix/Marte. Evitar el hostname público de Cortex y fijar labels `node=fenix|marte`.
4. **Mimir:** desplegarlo en Marte como almacenamiento de series para Prometheus mediante `remote_write` al Mimir privado local de Marte. `scripts/mimir_standalone.yaml` configura HTTP `:8080`, filesystem y replicación 1; es solo configuración, sin servicio Mimir actual.
5. **Loki:** desplegarlo en Marte para el backend de logs Sentinel. Instalar/configurar Grafana Alloy en ambos hosts para enviar journald/auditd y logs Docker seleccionados al listener privado `10.88.0.6:3100`. En Fenix, ejecutar Alloy con red host si Firewalld Marte autoriza solo `10.88.0.1`; la red bridge Docker produce otra IP de origen. Mantener el diagnóstico Alloy en loopback. Restringir el firewall por origen y no usar DNS Compose entre hosts.
6. **Grafana:** desplegarlo en Marte y provisionar datasources hacia Prometheus/Mimir/Loki de esa capa; los paneles deben mostrar fuentes Sentinel de Fenix. No publicar datasources internos ni APIs al navegador.
7. **TruthSync:** alojar el backend TruthSync en Marte y exponerlo solo por WireGuard. La UI sigue llamando a Fenix; FastAPI Fenix será el gateway hacia TruthSync en Marte (API actual `/api/v1/truthsync/verify`, puerto privado por definir). Hoy `truthsync-core` está enlazado dentro de Cortex/Fenix y FastAPI ejecuta un cliente local; no hay daemon TruthSync. Migrar el cliente detrás de un contrato autenticado, evitando motores divergentes o llamadas directas del navegador a Marte.
8. **Aceptación:** Prometheus consulta Fenix y Mimir devuelve las series de `remote_write`; Loki muestra etiquetas y entradas reales de los hosts; Grafana muestra datasources saludables; TruthSync responde según su contrato; y el forwarder eBPF recibe respuesta de FastAPI Fenix. `active` por sí solo no acredita integración.

### TruthSync: dos funciones complementarias

TruthSync comprende dos caminos con responsabilidades distintas; desplegar uno no sustituye al otro:

1. **Filtro integrado de seguridad/entropía:** `me-60os-core/src/scv.rs` implementa `ScvEngine` y `EntropicFirewall`; calcula entropía y decide validez (`analyze`/`verify`). `sentinel-cortex/src/security/lfm_security_pipeline.rs` agrega sanitización de ingreso y certificación de salida con el `TruthSyncEngine` enlazado. Esta ruta vive integrada en el runtime y filtra/rechaza entradas o salidas según sus reglas. La conexión exacta entre `ScvEngine` y cada ruta de producción debe verificarse antes de atribuirle cobertura total.
2. **TruthSync pod / Truth Core:** el motor de verificación y score de contenidos, concebido como servicio independiente. El historial conserva artefactos de despliegue en `truthsync-poc/k8s-deployment.yaml` y `k8s-truthsync.yaml`, además de `truthsync-poc/Dockerfile`, `docker-compose.yml` y `truthsync_server.py`. `639383a2` (2025-12-18) introdujo deployment, servicio, HPA y guía; `86bdffdd` (2025-12-30) consolidó un despliegue K8s de 3 réplicas, servicio ClusterIP y HPA hasta 10. La asignación objetivo actual es Marte, invocado privadamente por FastAPI en Fenix. Estos manifiestos son evidencia de diseño/paquete versionado, no de que Kubernetes lo aplicara en producción.

   **Calidad real del artefacto histórico:** el servidor Python en `639383a2` declara que el procesamiento está simulado y que la llamada real a Rust/shared memory queda como TODO (`truthsync_server.py`, líneas 87–116). En `86bdffdd`, el servicio Rust extrae claims, usa caché y devuelve `confidence = 0.95` fija (`src/main.rs`, líneas 1–24 y 103–117); eso no prueba score semántico/calibrado del contenido. La arquitectura y el paquete del pod están versionados, pero su operación real y madurez funcional deben auditarse antes de recuperarlo.

   El commit `0c5780f7` (2026-01-21) eliminó del árbol activo `truthsync-poc/`, `k8s-truthsync.yaml` y `infrastructure/kubernetes/k8s/apps/truthsync-edge.yaml`. El historial permite recuperar el diseño y código con `git show`; no acredita despliegue efectivo ni quién decidió la eliminación. No apareció en el inventario actual de Fenix revisado; el runtime histórico de Marte u otro nodo sigue sin verificarse.

Jaime reporta que ambos eran partes del mismo sistema y que una IA los separó, dejando el pod olvidado. El historial confirma que hubo un paquete de despliegue y que fue eliminado del árbol en `0c5780f7`, pero no confirma la atribución a una IA ni que alguna versión se desplegara. No reemplazar el servicio de contenido por el filtro integrado, ni eliminar/absorber el filtro al recuperar el pod. Auditar la versión histórica antes de restaurarla y corregir sus scores simulados/fijos; definir API privada, identidad/autenticación, timeout, persistencia, scoring y fallback. La UI continúa entrando por Kingu → Fenix; Fenix enruta la verificación de contenido a Truth Core en Marte.

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
2. Confirmar SSH por el puerto operativo 4222 a Fenix y Marte, y que Fenix conserva una ruta de recuperación independiente antes de tocar firewall, SSH, WireGuard o entrada pública.
3. Registrar en cada nodo (Fenix, Kingu y Marte): fecha UTC, hostname, OS/kernel/runtime, interfaces y rutas WireGuard, espacio libre, estado de Nginx/systemd/Firewalld y servicios Sentinel. En Marte confirmar que corresponde a `10.88.0.6`, que el peer de WireGuard está activo y que llega a `10.88.0.1`; los registros conocidos de Debian 13/kernel 7.3/SSH 4222 son contexto previo, no sustituyen esta lectura en vivo.
4. En Fenix, registrar contenedores, etiquetas Compose, imágenes/digests, bindings y redes. Comparar el estado real con `docker-compose.fenix.yml`; no inferir propiedad por el nombre de un puerto. Identificar qué contenedor escucha en cada puerto.
5. Guardar el head de Alembic y confirmar backup reciente/restore probado antes de cualquier migración o cambio de datos. No leer ni imprimir archivos de secretos.
6. Verificar reglas efectivas `DOCKER-USER`/nftables y sus contadores. Las reglas `INPUT` o la zona Firewalld por sí solas no prueban aislamiento de puertos DNAT de Docker.
7. Registrar DNS A/AAAA, vhost, certificado/SAN, upstreams y salud pública existentes. Conservar nombres y sitios ajenos.
8. En Marte, comprobar whitelists de ejecutables y rutas críticas y probar recuperación fuera de banda. El bootstrap actual adjunta Guardian en auditoría después de esa validación; si faltan precondiciones, no ejecutarlo ni adjuntar eBPF.
9. Validar Compose sin mostrar secretos:

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
5. Verificar tag/digest desplegado, proyecto Compose, estado `healthy`, logs de arranque, mounts requeridos y persistencia. Para Cortex, además verificar `GET /api/v1/crystal_runtime/status`: `active=true`, `runtime.active=true`, `shm_active=true`, ticks y sincronizaciones crecientes, y checkpoint duradero en el volumen persistente. Este endpoint exige autenticación; comprobarlo con una sesión aprobada, sin quitar middleware ni generar tokens que suplanten al operador.
6. Instalar QHC como dependencia requerida de Sentinel en Fenix antes de iniciar/recrear Cortex. Construir `qhc_agent` desde el mismo SHA, instalar `systemd/sentinel-qhc-agent.service`, comprobar IPC (`SNAPSHOT`) con el UID/GID del contenedor y arrancarlo. Verificar `GET /api/v1/qhc/status` con sesión autorizada: `connected=true`, `stale=false` y tick reciente; los logs de Cortex deben indicar `QHC=true`. Si falta el socket o el log indica `DEAD MAN SWITCH ACTIVATED`, Cortex puede seguir `healthy` mientras su scheduler está enclavado; no declarar funcional la integración.
7. En Marte, instalar solo componentes aprobados, en modo auditoría, tras completar el preflight eBPF. Apuntar la ingesta de eventos al backend Fenix por WireGuard (`POST /api/v1/cortex/events`, autenticación `X-Sentinel-Token`) y métricas a la ruta de observabilidad aprobada. Confirmar que el firewall de Fenix permite únicamente la IP WireGuard de Marte y los puertos requeridos; no reutilizar ni imprimir secretos. El servicio actual `sentinel-ebpf-forwarder` ejecuta `bpftool prog tracelog` localmente: no demuestra por sí mismo envío remoto a Fenix.
8. Desde Kingu y Marte, comprobar APIs privadas por WireGuard. Desde un segundo peer autorizado y desde el camino público, comprobar que los puertos internos y bases de datos no aceptan conexiones. La ruta pública esperada pasa por Nginx en Kingu.

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
| Headers web | Revisar HSTS, CSP, X-Content-Type-Options, protección de framing y Referrer-Policy; documentar excepciones antes de aceptar exposición pública. |
| BFF/FastAPI | Health 200 y dependencias saludables; `/api/auth/me` sin sesión devuelve 401 esperado. Prueba de credenciales inválidas solo con datos sintéticos y sin registrar cuerpos sensibles. |
| Cortex/WebSocket | `/health` 200; endpoint de runtime activo y métricas dinámicas; Origin autorizado sin token devuelve 401 y Origin ajeno 403; handshake autenticado requiere sesión aprobada por el usuario. |
| Red | Kingu llega a los upstreams privados; peer VPN distinto no llega a 8000/8001/5678; PostgreSQL/Redis no tienen binding accesible desde la VPN o Internet. |
| Nginx | `nginx -t` exitoso; vhost usa upstreams Sentinel previstos y no altera sitios ajenos; logs sin errores nuevos. Registrar advertencias existentes de otros vhosts por separado. |
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
