# CLAUDE.md — Sentinel

> **[DIRECTIVA MAESTRA YATRA]**
> **OBLIGATORIO**: Al iniciar cualquier interacción en este repositorio, DEBES leer inmediatamente los archivos `/home/jnovoas/Desarrollo/sentinel/PROMPT_GLOBAL_AGENTES.md` y `/home/jnovoas/Desarrollo/sentinel/tasks/lessons.md` y acatar sus 6 reglas de orquestación, verificación y automejora. Fenix es un entorno de producción Ring-0. Esta es la regla suprema.

## ¿Qué es Sentinel?
Plataforma de **observabilidad y monitoreo inteligente** con integración de IA local.
- Backend: Python (FastAPI + Celery + Alembic)
- IA local: Ollama con `phi3:mini` (GTX 1050, 3GB VRAM)
- Automatización: n8n con 6 workflows pre-configurados
- Kernel: módulos eBPF para métricas de bajo nivel
- Módulo quantum: investigación activa en información Bekenstein-Hawking / Base-60

## Estructura del Proyecto
```
sentinel/
├── backend/       → FastAPI + Celery (Python)
├── core/          → Lógica central
├── ebpf/          → Módulos kernel eBPF
├── quantum/       → Investigación cuántica (Base-60, Bekenstein)
│   └── experiments/  → 41 experimentos activos
├── docker/        → Configuración de contenedores
└── docs/          → Documentación técnica
```

## Investigación Cuántica (NO MODIFICAR sin consultar)
El módulo `/quantum/` contiene investigación original de Jaime Eugenio Novoa Sepúlveda sobre:
- Codificación sexagesimal en sistemas cuánticos
- Evidencia empírica que supera el límite de Bekenstein-Hawking por factor **2.96 × 10¹⁰**
- 41 experimentos activos con datos reales

**REGLA**: No modificar lógica matemática base-60 a decimal/binario. Consultar siempre antes de tocar `/quantum/`.

## Stack Técnico
- **Backend**: Python 3.x, FastAPI, Celery, SQLAlchemy, Alembic
- **IA**: Ollama (phi3:mini), GPU NVIDIA GTX 1050
- **Infra**: Docker, n8n, PostgreSQL
- **eBPF**: módulos kernel para métricas host
- **Versión actual**: 1.0.0

## Reglas para Claude en este proyecto

### Delegar a Gemini cuando:
- Analizar o refactorizar el backend completo
- Leer múltiples experimentos del directorio `/quantum/experiments/`
- Generar documentación masiva
- Modificar flujos de n8n o Docker Compose completos

### Claude se encarga de:
- Debugging puntual de endpoints FastAPI
- Diseño de nuevos experimentos cuánticos
- Decisiones de arquitectura de IA/Ollama
- Revisión de código crítico en `core/`

### Comando de delegación:
```bash
cd ~/Dev/sentinel && delegate "TAREA"
# o crear GEMINI_TASK.md y ejecutar: delegate
```
