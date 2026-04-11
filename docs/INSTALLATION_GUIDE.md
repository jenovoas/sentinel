# Sentinel - Guía de Instalación (Fenix Native)

**Guía paso a paso para desplegar Sentinel en entornos de alto rendimiento con matemática S60 y Ring-0.**

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#-requisitos-del-sistema)
2. [Configuración de Podman (Rootless)](#-configuracion-de-podman-rootless)
3. [Instalación de Dependencias de Compilación](#-dependencias-de-compilacion)
4. [Despliegue con Orquestador Fenix](#-despliegue-con-orquestador-fenix)
5. [Verificación eBPF Ring-0](#-verificacion-ebpf-ring-0)
6. [Solución de Problemas](#-solución-de-problemas)

---

## 📦 Requisitos del Sistema

Sentinel está optimizado para **Rocky Linux 9 (Fenix)** y requiere capacidades de Kernel para eBPF.

| Componente | Requisito |
|------------|-----------|
| **Sistema Operativo** | Linux (Kernel 5.8+ requerido para eBPF, Rocky/RHEL 9 recomendado) |
| **Arquitectura** | x86_64 (con soporte para instrucciones de punto fijo) |
| **Contenedores** | Podman 4.6+ (Modo Rootless) |
| **Lenguajes** | Rust 1.75+ (Stable), Node.js 18+ (LTS) |
| **Memoria** | 8 GB RAM (Mínima), 16 GB+ (Producción con IA) |

---

## 🐋 Configuración de Podman (Rootless)

Sentinel NO utiliza Docker por diseño de seguridad. Se requiere Podman en modo rootless.

### 1. Instalar Podman

```bash
sudo dnf install -y podman podman-docker podman-compose
```

### 2. Configurar SubUIDs/SubGIDs (Para Rootless)

Asegúrese de que su usuario tenga rangos asignados:

```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER
podman system migrate
```

### 3. Exponer puertos privilegiados (Opcional)

Si desea usar puertos < 1024:

```bash
sudo sysctl net.ipv4.ip_unprivileged_port_start=80
```

---

## 🦀 Dependencias de Compilación

El núcleo de Sentinel (**Cortex**) se compila de forma nativa para máxima eficiencia.

### 1. Herramientas de Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustup target add x86_64-unknown-linux-gnu
```

### 2. LLVM y Clang (Para eBPF)

```bash
sudo dnf install -y clang llvm elfutils-libelf-devel libbpf-devel
```

---

## 🚀 Despliegue con Orquestador Fenix

Sentinel utiliza un archivo de orquestación depurado para el nodo Fenix.

### 1. Clonar y Preparar

```bash
git clone https://github.com/jenovoas/sentinel.git
cd sentinel
cp .env.example .env
```

### 2. Configurar Secretos Críticos

Edite el archivo `.env` y asegúrese de definir:

- `POSTGRES_PASSWORD`: Contraseña de la base de datos.
- `REDIS_PASSWORD`: Contraseña de Redis.
- `SECRET_KEY`: Llave para la firma de tokens JWT.
- `GF_ADMIN_PASSWORD`: Acceso a Grafana.
- `TRAEFIK_BASIC_AUTH`: Formato `usuario:hash` (Generar con `openssl passwd -apr1`).

### 3. Iniciar el Stack
>
> [!IMPORTANT]
> El servicio `cortex` requiere privilegios para cargar programas eBPF en el kernel.

```bash
# Iniciar servicios core
podman-compose -f docker-compose.fenix.yml up -d
```

---

## 🛡️ Verificación eBPF Ring-0

Una vez que el contenedor `sentinel-cortex` esté arriba, verifique que los hooks de kernel estén activos:

```bash
# Ver logs de carga de eBPF
podman logs sentinel-cortex | grep -i "bpf"

# Verificar programas cargados en el host
sudo bpftool prog list
```

---

## 🔧 Solución de Problemas

### Error de Permisos en Volúmenes (SELinux)

Si ve errores de "Permission Denied" al acceder a archivos configurados por volúmenes:
**Solución**: Asegúrese de usar el sufijo `:z` en el `docker-compose.yml`.
*Ejemplo*: `- ./config.yml:/etc/config.yml:ro,z`

### eBPF: operation not permitted

**Causa**: El contenedor no tiene privilegios suficientes o el kernel del host está bloqueado.
**Solución**: Asegúrese de que el contenedor corre con `--privileged` o con las capacidades `SYS_ADMIN` y `BPF`.

---

**Nota**: Esta documentación es parte del protocolo de soberanía de Sentinel. No compartir fuera de niveles de acceso autorizados.

# Verificar variables de entorno

podman exec sentinel-cortex env

# Verificar conectividad entre servicios

podman exec sentinel-cortex ping postgres
podman exec sentinel-cortex ping sentinel-redis

```

---

## 📚 Recursos Adicionales

### Documentación

- [README.md](README.md) - Descripción general del proyecto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura técnica
- [HA_REFERENCE_DESIGN.md](docs/HA_REFERENCE_DESIGN.md) - Alta disponibilidad
- [BACKUP_SETUP_GUIDE.md](docs/BACKUP_SETUP_GUIDE.md) - Sistema de backups

### Comandos Útiles (Makefile)

```bash
make help              # Ver todos los comandos disponibles
make up                # Iniciar servicios
make down              # Detener servicios
make restart           # Reiniciar servicios
make logs              # Ver logs
make health            # Verificar salud
make db-backup         # Backup de base de datos
make clean             # Limpiar todo (⚠ elimina datos)
```

### Soporte

- **Issues**: <https://github.com/tu-usuario/sentinel/issues>
- **Documentación**: <https://sentinel.dev/docs>
- **Email**: <support@sentinel.dev>

---

## 🎉 ¡Instalación Completada

Si llegaste hasta aquí, **¡felicitaciones!** 🎊

Sentinel está instalado y corriendo. Ahora puedes:

1. ✅ Acceder al dashboard: <https://cortex.pinguinoseguro.cl>
2. ✅ Ver métricas en Grafana: <https://grafana.pinguinoseguro.cl>
3. ✅ Explorar logs en Loki/Grafana: <https://grafana.pinguinoseguro.cl> (Data Source: Loki)
4. ✅ Crear workflows en n8n: <https://n8n.pinguinoseguro.cl>

---

**¿Problemas?** Consulta la sección [Solución de Problemas](#-solución-de-problemas) o abre un issue en GitHub.

**¡Disfruta Sentinel!**
