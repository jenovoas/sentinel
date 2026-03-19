# Registro de Lecciones Aprendidas (Automejora Gemini/Claude)

*Regla: Después de CUALQUIER corrección del usuario, actualizar este archivo con el patrón y una regla para no repetir el error.*

## [2026-03-18] Error de Permisos en Volúmenes Podman Rootless (SELinux)

**El Error:**
Al levantar Prometheus y PostgreSQL en `docker-compose.fenix.yml`, los contenedores entraron en crash-loop (CPU >174% o denegación de inicialización) por errores de tipo `permission denied` (ej: `open /etc/prometheus/prometheus.yml: permission denied`).

**La Causa:**
Rocky Linux 9 (Fenix) usa SELinux en modo enforcing. En Podman rootless, montar archivos locales vía bind mount (`./ruta/local:/ruta/contenedor:ro`) requiere explícitamente etiquetar el volumen para que SELinux permita el acceso al contenedor. Al olvidar el flag, se gatilló el error de denegación sin visibilidad inmediata.

**La Regla de Oro (Prevención):**
**SIEMPRE** que se añada un bind mount local en un `docker-compose` para sistemas Podman en RHEL/Rocky Linux, **OBLIGATORIAMENTE** se debe añadir el sufijo `:z` (o `:Z`) a los permisos. 
*Mal:* `- ./config.yml:/etc/config.yml:ro`
*BIEN:* `- ./config.yml:/etc/config.yml:ro,z`

---

## [2026-03-18] Contexto de Construcción Cruzado en Dockerfiles (me-60os)

**El Error:**
Compilar `sentinel-cortex` en Podman falló porque `Cargo.toml` apuntaba a `../../me-60os`, el cual estaba fuera del contexto de Docker (que solo veía `./sentinel-cortex`).

**La Causa:**
Falta de validación previa de dependencias físicas fuera del docker build context. 

**La Regla de Oro (Prevención):**
Para binarios Rust en arquitectura mono-repo separada donde un crate depende de un path externo, considerar:

1. Compilar nativamente `cargo build --release` y copiar el binario precompilado (`COPY target/release/bin` en una imagen Alpine/Debian-slim). **<- Este enfoque es el recomendado y el más rápido.**
2. Jamás intentar un build multistage sin auditar antes dónde apuntan los `path=` del `Cargo.toml`.

---

## [2026-03-18] Error de Soberanía Documental y Alucinación Operacional

**El Error:**
Llevar a cabo modificaciones en la documentación y proponer planes de monitoreo/despliegue basándose en archivos obsoletos (ej: `GEMINI_TASK_MONITORING.md` de febrero) sin realizar primero una auditoría empírica del sistema (`podman ps`, `ip addr`). Esto llevó a la "alucinación" de un clúster de 4 nodos (Kingu, Centurion, Sentinel, Fenix) que ya no existía en el entorno productivo.

**La Causa:**
Priorizar la "ayuda rápida" sobre el rigor investigativo. El agente ignoró que la documentación de desarrollo puede divergir drásticamente de la realidad de producción (Fenix como Nodo Único). Además, se mezclaron proyectos externos (La Espiguita, Pinguino Web) con la documentación core de Sentinel.

**La Regla de Oro (Prevención):**
**NUNCA** confiar en un documento descriptivo como fuente de verdad absoluta sin validación física. Antes de proponer cambios, el agente **DEBE** realizar un "Mapeo de Verdad":

1. **Validación de Procesos:** `podman ps --all` para ver la realidad del host.
2. **Validación de Red:** `ip addr` y `podman network ls` para confirmar segmentos (ej. VPN 10.100.0.x).
3. **Validación de Ruteo:** `podman inspect` para mapear labels de Traefik y dominios reales.
4. **Separación de Dominios:** Mantener la documentación de Sentinel puramente técnica y separada de proyectos de clientes o agencias externas.

---

## [2026-03-18] Configuración de BasicAuth en Traefik vía Entorno

**El Error:**
Uso de placeholders o fallbacks hardcodeados en `docker-compose.yml` para el middleware de autenticación (`basicauth.users`), lo que dificulta la gestión de secretos y puede exponer credenciales por defecto.

**La Causa:**
Falta de una variable de entorno dedicada y un procedimiento claro para generar hashes compatibles con Apache/Traefik sin depender de herramientas externas no instaladas (como `htpasswd`).

**La Regla de Oro (Prevención):**

1. **SIEMPRE** usar variables de entorno (ej: `TRAEFIK_BASIC_AUTH`) para definir usuarios de BasicAuth en las etiquetas de Traefik.
2. **NUNCA** dejar el hash en claro o como fallback en el archivo compose.
3. Para generar hashes compatibles sin `htpasswd`, usar `openssl`:
   `openssl passwd -apr1 <password>`
4. Formato en `.env`: `USUARIO:HASH` (ej: `admin:$apr1$1URqO8Xv$...`).
5. En `docker-compose.yml`, referenciar simplemente como `${VARIABLE}`.
