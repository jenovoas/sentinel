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
