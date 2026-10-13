# 🛡️ Sentinel TUI - AI-Powered Terminal Interface

**Terminal User Interface** para administración de sistemas con IA local, integrada con todos los sistemas de seguridad y telemetría de Sentinel.

## 🎯 Características

### 💬 **AI Chat Mode**
- Conversación natural con IA local (Ollama llama3.2:3b)
- Integración con **TruthSync** para verificación de respuestas
- **AIOpsShield** para sanitización de datos
- Soporte multi-agente (Security, DevOps, Quantum)
- Historial de conversación con contexto

### 🧠 **SemShell Terminal Mode**
- Ejecución segura de comandos con evaluación de riesgo por IA
- Perfiles de seguridad configurables (Lab, Prod, Lockdown)
- Bloqueo determinista de comandos peligrosos
- Salida en tiempo real de comandos
- Integración con Base-60 y sistemas quantum

### 📊 **Telemetría en Tiempo Real**
- Estado del sistema Sentinel
- Métricas de Guardian (eBPF)
- Estado de TruthSync
- Estado de Cortex
- Panel lateral colapsable

## 📦 Instalación

### 1. Instalar dependencias y configurar

```bash
cd /home/jnovoas/sentinel
./install_sentinel_tui.sh
```

Esto instalará:
- Dependencias Python (textual, rich, httpx)
- Symlink en `~/.local/bin/sentinel-tui`
- Plugin de Neovim en `~/.config/nvim/lua/sentinel/`

### 2. Configurar Neovim (opcional)

Agregar a tu `~/.config/nvim/init.lua`:

```lua
-- Cargar plugin de Sentinel
require('sentinel').setup({
    window_height = 20,
    window_width = 100,
})
```

### 3. Iniciar servicios backend

```bash
# Solo servicios esenciales (sin frontend)
./start_tui_backend.sh
```

Esto inicia:
- PostgreSQL (base de datos)
- Backend API (FastAPI)
- Ollama (IA local)

## 🚀 Uso

### Modo Interactivo (TUI)

```bash
sentinel-tui
```

#### Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Enter` | Enviar mensaje / Ejecutar comando |
| `Ctrl+X` | Cambiar entre Chat y Terminal |
| `Ctrl+L` | Limpiar chat |
| `Ctrl+T` | Toggle panel de telemetría |
| `Ctrl+H` | Mostrar ayuda |
| `Ctrl+C` | Salir |
| `F1` | Desplegar Security Agent |
| `F2` | Desplegar DevOps Agent |
| `F3` | Desplegar Quantum Agent |

### Modo CLI (Consultas Directas)

```bash
# Consulta simple
sentinel-cli "analyze system logs"

# Con agente específico
sentinel-cli --agent security "check for vulnerabilities"

# Verificar datos con TruthSync
sentinel-cli --verify "some data to verify"

# Ver estado del sistema
sentinel-cli --status
```

### Desde Neovim

#### Atajos por defecto:

| Atajo | Acción |
|-------|--------|
| `<leader>st` | Abrir Sentinel TUI en split |
| `<leader>sf` | Abrir Sentinel TUI en ventana flotante |
| `<leader>sa` | Preguntar sobre buffer actual |
| `<leader>s1` | Desplegar Security Agent |
| `<leader>s2` | Desplegar DevOps Agent |
| `<leader>s3` | Desplegar Quantum Agent |

## 🧠 SemShell - Terminal Seguro

### Perfiles de Seguridad

Cambiar perfil dentro del terminal:

```bash
mode lab        # Permisivo (threshold: 1.0)
mode prod       # Enforcing (threshold: 0.7)
mode lockdown   # Restrictivo (threshold: 0.1)
```

### Evaluación de Riesgo

Cada comando es evaluado por IA antes de ejecutarse:

- 🟢 **Riesgo Bajo** (< 0.3): Ejecuta automáticamente
- 🟡 **Riesgo Medio** (0.3 - 0.7): Ejecuta según perfil
- 🔴 **Riesgo Alto** (> 0.7): Bloqueado en prod/lockdown

### Comandos Bloqueados Determinísticamente

Patrones bloqueados sin importar el perfil:
- `/etc/shadow`, `/etc/passwd`
- `/root/.ssh`
- `rm -rf /`
- `mkfs` (formateo de discos)

## 🤖 Agentes Especializados

### 🛡️ Security Agent (F1)
- Análisis de amenazas
- Integración con Guardian Alpha/Beta
- Detección de vulnerabilidades
- Análisis de logs de seguridad

### ⚙️ DevOps Agent (F2)
- Administración de sistema
- Gestión de Docker
- Deployment y CI/CD
- Monitoreo de infraestructura

### ⚛️ Quantum Agent (F3)
- Simulaciones quantum
- Matemática Base-60
- Física avanzada
- Cálculos de ZPE

## 🔒 Seguridad

### TruthSync Verification
Todas las respuestas críticas son verificadas con TruthSync usando checksums Base-60.

### AIOpsShield
Sanitización automática de:
- Logs del sistema
- Métricas de telemetría
- Comandos peligrosos
- Patrones de ataque

### Guardian Integration
Monitoreo en tiempo real de:
- Hooks eBPF activos
- Latencias del kernel
- Eventos de seguridad
- Decisiones de Cortex

## 📊 Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   Sentinel TUI (Textual)                 │
│  ┌─────────────────┐         ┌──────────────────┐      │
│  │   AI Chat       │         │  SemShell Term   │      │
│  │  (Ollama)       │         │  (Risk AI)       │      │
│  └─────────────────┘         └──────────────────┘      │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│              Backend Services (Docker)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐         │
│  │PostgreSQL│  │ FastAPI  │  │   Ollama     │         │
│  │   (DB)   │  │(Backend) │  │ (llama3.2)   │         │
│  └──────────┘  └──────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│           Security & Verification Layer                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐         │
│  │TruthSync │  │ Guardian │  │    Cortex    │         │
│  │(Base-60) │  │  (eBPF)  │  │  (Decision)  │         │
│  └──────────┘  └──────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Backend URL (default: http://localhost:8000)
export BACKEND_URL="http://localhost:8000"

# Ollama URL (default: http://localhost:11434)
export OLLAMA_URL="http://localhost:11434"
```

### Archivos de Configuración

- **Historial**: `~/.sentinel/tui_history.json`
- **Estado SemSH**: `/etc/sentinel/state.json`
- **ChromaDB**: `/home/jnovoas/sentinel/db/chroma`

## 📝 Ejemplos de Uso

### Chat con IA

```
💬 AI Chat Mode:

You: "How do I check if Guardian is running?"

Sentinel AI: "You can check Guardian status with:
1. Check eBPF programs: `sudo bpftool prog list`
2. Check LSM hooks: `cat /sys/kernel/security/lsm`
3. Use Sentinel API: `curl http://localhost:8000/api/v1/health`

Guardian should show active eBPF programs for Alpha and Beta."

[✓ TruthSync] [🛡️ Sanitized]
```

### Terminal Seguro

```
🧠 SemShell Terminal:

semsh> ls -la /home

🟢 Risk Assessment: 0.05 | Profile: Lab
✅ Executing...
total 12
drwxr-xr-x  3 root    root    4096 Jan  4 21:00 .
drwxr-xr-x 19 root    root    4096 Jan  4 20:00 ..
drwxr-xr-x 25 jnovoas jnovoas 4096 Jan  4 21:48 jnovoas

semsh> rm -rf /

🔴 Risk Assessment: 1.00 | Profile: Lab
🚫 BLOCKED: Matches deny pattern '^rm -rf /$'
```

### Agente de Seguridad

```
[F1 - Security Agent Deployed]

You: "Scan for open ports"

Security Agent: "Running security scan...

Open ports detected:
- 22/tcp (SSH) - Protected by Guardian
- 8000/tcp (Backend API) - Internal only
- 11434/tcp (Ollama) - Localhost only

Recommendations:
1. All critical ports are properly firewalled
2. Guardian LSM hooks are active
3. No suspicious connections detected

System security status: ✅ SECURE"
```

## 🐛 Troubleshooting

### Backend no disponible

```bash
# Verificar servicios
docker-compose ps

# Reiniciar backend
./start_tui_backend.sh
```

### Modelo Ollama no encontrado

```bash
# Descargar modelo
docker-compose exec ollama ollama pull llama3.2:3b
```

### SemShell no disponible

```bash
# Verificar que sem_shell.py existe
ls -la sem_shell.py

# Verificar permisos
chmod +x sem_shell.py
```

## 📚 Documentación Adicional

- **Arquitectura Sentinel**: `docs/ARQUITECTURA_COMPLETA_INTEGRADA.md`
- **TruthSync**: `truthsync-poc/README.md`
- **Guardian**: `guardian-alpha/README.md`
- **SemShell**: `docs/SEMSH_SSAP_GUIDE.md`

## 🎯 Roadmap

- [ ] Soporte para múltiples modelos de IA
- [ ] Integración con n8n workflows
- [ ] Exportar conversaciones
- [ ] Temas personalizables
- [ ] Plugins de terceros
- [ ] Modo colaborativo multi-usuario

## 📄 Licencia

Propietario - Sentinel Project © 2026

---

**Desarrollado con 🛡️ por el equipo Sentinel**

Para más información: `sentinel-cli --help` o `Ctrl+H` en el TUI
