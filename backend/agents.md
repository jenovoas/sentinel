# 🐍 AGENTE BACKEND: ORQUESTACIÓN Y API

> **CONTEXTO:** Este directorio (`/backend`) maneja la "fontanería" del sistema: APIs, Bases de Datos, y Contenedores Docker.

## 1. 🛡️ DIRECTIVAS CRÍTICAS

### 🎭 AXIOMA II: HONESTIDAD RADICAL (Logs)
- **LOGS:** Los logs deben ser reales. No ocultes errores 500.
- **ESTADO:** Reporta el estado de salud real de los contenedores (`healthcheck.sh`).

### ⚡ AXIOMA III: RUST CORE DELEGATION
- **ROL DE PYTHON:** Python es SOLO para orquestación (mover datos, APIs, coordinar).
- **CÁLCULO PESADO:** Si tienes que calcular algo complejo, llama al `sentinel_core` (Rust) o usa `quantum` libs. NO lo implementes en Python puro si es intensivo.

## 2. ⚙️ REGLAS OPERATIVAS

1. **Docker:** Todo corre en contenedores. Respeta `docker-compose.yml`.
2. **Base de Datos:** PostgreSQL para persistencia. Redis para caché rápido (Hot State).
3. **Migraciones:** Usa `alembic` para cambios en DB. Nunca modifiques el esquema manualmente en producción.
4. **API:** FastAPI es el estándar. Tipado estricto con Pydantic.

## 3. 📂 MAPA DE CONOCIMIENTO

- **App:** `app/` (Código fuente API).
- **Workers:** `Dockerfile.worker` (Procesos de fondo).
- **Config:** `.env` (Gestionado con seguridad, no commitear secretos).

---
**OBJETIVO:** Estabilidad y Disponibilidad. "El backend debe ser aburrido y predecible."
