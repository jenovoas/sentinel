# Guía de Operación: Contenedores y Persistencia (Fénix)

Este documento detalla la configuración de contenedores en el nodo **Fénix**, cómo asegurar su persistencia tras reinicios y cómo diagnosticar fallos de salud.

## 1. Arquitectura de Despliegue
En Fénix, utilizamos **Podman** en modo *rootless* para mayor seguridad. Los contenedores se agrupan en **Pods** para compartir namespaces de red (localhost).

*   **Pod Maestro**: `pod_sentinel`
*   **Gestión de Red**: Los servicios se comunican internamente usando sus nombres de servicio (ej: `backend`, `postgres`) gracias a la red interna de Podman.

---

## 2. Diagnóstico de Salud (Health Checks)

Si un contenedor muestra un estado **unhealthy** (triángulo amarillo en el IDE o `unhealthy` en `podman ps`), verifica los siguientes puntos críticos corregidos el 2026-04-17:

### A. Backend (Redis Sentinel vs Standalone)
*   **Fallo Común**: El backend intenta buscar clusters de Sentinel (`redis-sentinel-1`) en un entorno que solo tiene Redis standalone.
*   **Solución**: Asegurar que `REDIS_MODE=standalone` esté configurado en el `.env`. El código en `redis_client.py` ahora respeta esta variable para evitar fallos de resolución DNS.

### B. Nginx (Upstreams)
*   **Fallo Común**: Nginx intenta conectar a `localhost:8000`. En Podman, `localhost` dentro de Nginx apunta al propio contenedor de Nginx.
*   **Solución**: Los upstreams en `nginx.conf` deben apuntar al nombre del servicio:
    ```nginx
    upstream backend {
        server backend:8000;
    }
    ```

---

## 3. Persistencia tras Reinicio del Servidor

Para que los contenedores arranquen automáticamente al encender el servidor sin intervención manual:

### A. Unidades de Systemd
Cada contenedor principal tiene una unidad de systemd en `~/.config/systemd/user/container-<nombre>.service`.
*   **Importante**: Estas unidades deben generarse con el flag `--new` para que el contenedor se recree desde la imagen en cada inicio, integrando cualquier cambio reciente.
*   **Comando de actualización**:
    ```bash
    podman generate systemd --new --name <container-name> > ~/.config/systemd/user/container-<container-name>.service
    systemctl --user daemon-reload
    systemctl --user enable --now container-<container-name>.service
    ```

### B. Usuario "Linger"
Para que los servicios de usuario arranquen sin que el usuario `jnovoas` haya iniciado sesión vía SSH:
```bash
loginctl enable-linger jnovoas
```

---

## 4. Protocolo de Recuperación ante Fallos (SOP)

Si el sistema no responde o hay contenedores caídos:

1.  **Verificar Estado Global**:
    ```bash
    podman ps --all
    ```
2.  **Reiniciar vía Systemd** (Preferido para mantener persistencia):
    ```bash
    systemctl --user restart container-sentinel-backend.service
    systemctl --user restart container-sentinel-nginx.service
    ```
3.  **Re-despliegue Completo** (Si el código ha cambiado):
    ```bash
    # En la carpeta del proyecto
    podman-compose up -d --build
    # IMPORTANTE: Regenerar unidades systemd después de un cambio estructural
    ```
4.  **Limpieza de Contenedores Huérfanos**:
    Si ves contenedores duplicados o en estado "Exited" que estorban:
    ```bash
    podman rm -f $(podman ps -a -f status=exited -q)
    ```

---

## 5. Flags de Seguridad y Red
*   **SELinux**: Siempre usar el flag `:z` en los montajes de volumen (ej: `./config:/app/config:z`) para evitar errores de `Permission Denied`.
*   **Internal Network**: Todos los servicios críticos deben estar en la red `sentinel_internal` para aislamiento.
