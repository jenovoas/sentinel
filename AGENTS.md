# ARQUITECTURA Y DIRECTIVAS PARA AGENTES E IA (REGLAS DE ORO DEL PROYECTO SENTINEL)

## 1. REGLA ESTRICTA DE DIRECTORIOS (HARD CONSTRAINT)
- **NO CREAR ARCHIVOS EN LA RAÍZ DEL REPOSISTORIO**.
- **Distribución de módulos**:
  - `src/` o `backend/`: Lógica central de Rust y servidores.
  - `ebpf/`: Programas del kernel Linux y hooks LSM.
  - `frontend/` o `gui/`: Interfaz de usuario y dashboards.
  - `scripts/`: Todos los scripts de mantenimiento, instalación y escaneo (`.sh`, `.py`).
  - `tests/`: Pruebas de integración e unitarias.
  - `docs/`: Documentación, guías y prompts del sistema.

## 2. RIGOR CIENTÍFICO Y ARQUITECTURA DE SOFTWARE
- **Aritmética Exacta**: En controladores de tiempo real y seguridad, mantén aritmética entera escalada.
- **Sin Archivos Temporales**: No guardes copias `.bak`, `.tmp`, ni logs de pruebas en el control de versiones.
- **Formato de Commits**: Utiliza commits convencionales (`feat:`, `fix:`, `refactor:`, `docs:`). Evita mensajes genéricos.
