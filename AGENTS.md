# ARQUITECTURA Y DIRECTIVAS PARA AGENTES E IA (REGLAS DE ORO DEL PROYECTO SENTINEL)

> **RAMAS POR ENTORNO Y RAMA PREDETERMINADA.** `alpine_fenix` corresponde al entorno Alpine/OpenRC y es la rama activa de desarrollo y la rama predeterminada del repositorio GitHub mientras Fénix sea el único nodo operativo. `main` corresponde al entorno systemd y se mantiene independiente para ese entorno; no representa el estado actual de Alpine.
> Los cambios de Alpine se aplican únicamente en `alpine_fenix`; los cambios de systemd, únicamente en `main`. Se permite hacer checkout, commit y push en la rama del entorno correspondiente.
> Prohibido hacer merge entre `main` y `alpine_fenix`, copiar configuraciones de una plataforma a la otra o usar `develop` u otra rama como sustituto de estos entornos.
>
> **Nodo actual, por ahora uno.** `fenix`, Alpine, kernel `6.18.40-0-virt`, IP `172.233.24.102`.
> El sistema está en desarrollo activo, **construyéndose con estándar estricto de producción** para preparar el despliegue final. Sin segundo servidor y sin datacenter hasta terminar Fenix. OpenRC, Docker Compose, Nginx.
>
> **CABLEADO Y TOPOLOGÍA OBLIGATORIA:** Ver [`docs/ops/CABLEADO_Y_TOPOLOGIA_CANONICA.md`](docs/ops/CABLEADO_Y_TOPOLOGIA_CANONICA.md).
> Prohibido usar IPs antiguas (10.88.0.1, 172.18.0.1 fija, etc.). La comunicación entre contenedores usa exclusivamente nombres de servicio DNS (postgres, redis, prometheus, loki, n8n); Cortex atiende en 127.0.0.1:8000 detrás de Nginx TLS (*.pinguinoseguro.cl).

> **LECTURA OBLIGATORIA ANTES DE EMITIR JUICIOS SOBRE EL PROYECTO:**
> Ver [`docs/02_ciencia_y_quantum/research/base60_mathematics.md`](docs/02_ciencia_y_quantum/research/base60_mathematics.md), [`docs/02_ciencia_y_quantum/research/TesisResonancia.md`](docs/02_ciencia_y_quantum/research/TesisResonancia.md) y nota en vault `personalvault/Matemáticas/mathematical_model.md`.
> Sentinel **NO es misticismo ni maquetas**. Es **ciencia exacta**.
>
> La base decimal no es defectuosa — es solo **una décima parte de la expresión
> matemática universal**. La base-60 permite cálculos exactos: es divisible por 1, 2, 3, 4, 5, 6,
> 10, 12, 15, 20, 30, por lo que las fracciones más comunes (1/3, 1/6, 1/12, 1/60)
> son **exactas** en sexagesimal, mientras que en binario de punto flotante son
> periódicas y acumulan errores sistemáticos de redondeo.
>
> Usar solo base decimal como regla de medir deja fuera de alcance exacto esas
> fracciones. Una sola operación float en una cadena de cómputo entera contamina
> el resultado: rompe cristales, secuencias, memorias, procesos y conversiones.
> Si tu regla de medir no es exacta, jamás podrás medir la exactitud de un sistema.
>
> Por eso muchos proyectos de energía libre y combustibles verdes fueron marcados
> como inválidos: no eran incorrectos los proyectos — era incompleta la regla de
> medir. **Lee el documento completo.**

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

## 3. CONVERSIÓN BINARIO → AMPLITUD (PAI-60 / SPA SCALE)

- **Escala SPA**: `SPA` usa fixed-point base-60⁴ (`SCALE_0 = 12_960_000`). `SPA::from_int(n)` = número entero `n.0`; `SPA::from_raw(n)` = `n/SCALE_0` (unidades raw). NO confundir.
- **Inyección al lattice**: `transduce_pulse(pressure: i64)` y `inject(index, pressure: i64)` esperan un **entero** que ellos mismos re-escalan por `SCALE_0`. **NUNCA** pasar `SPA::to_raw()` a esos métodos (doble-escala → dato irrecuperable).
- **Conversor PAI-60**: dato binario → amplitud con `pai60_divide(SPA::from_int(value), denom)` y el `SPA` se suma al oscilador (`inject_spa` / `inject_pai`). El drive térmico de Cortex usa siempre esa amplitud. No hay rama `inject(i64)` ni flag `SENTINEL_PAI_CONVERT`.
- **El lattice es disipativo**: `step()` solo disipa (decay). Sin drive continuo (`sentinel-cortex/src/main.rs` bloque 3b, cada 500ms) el lattice cae a `ground state` y no resuena. Siempre debe haber drive.
- **Material de estudio**: `me-60os-core/src/bin/pai_convert_bench.rs` compara A (RAW), B (PAI-60) y C `[exp fallido para estudio]` (doble-escala, etiquetado, NO borrar). Leer antes de "arreglar" conversión SPA.

<!-- code-review-graph:start -->
# Codebase Knowledge Graph (code-review-graph)

Este proyecto mantiene un grafo del código con `code-review-graph` (MCP). Usa SIEMPRE las
herramientas del grafo antes de grep/glob/read para descubrir código: cuestan menos tokens y
dan contexto estructural (llamadores, dependientes, cobertura de tests) que el escaneo de
archivos no puede dar.

## Orden de prioridad
1. `semantic_search_nodes_tool` — localizar funciones, clases, rutas o variables por nombre
2. `query_graph_tool` — relaciones: `callers_of`, `callees_of`, `imports_of`, `tests_for`
3. `get_impact_radius_tool` — radio de impacto de un cambio
4. `detect_changes_tool` — cambios con puntuación de riesgo
5. `get_review_context_tool` — snippets de fuente eficientes en tokens
6. `get_architecture_overview_tool` — estructura de alto nivel
7. `refactor_tool` — planificar renombrados, detectar código muerto

## Cuándo caer a grep/glob
- Literales de cadena, mensajes de error, valores de configuración
- Archivos que no son código (Dockerfiles, scripts shell, configs, docs)
- Cuando el grafo no cubre lo que necesitas o está desactualizado

## Arranque y rutas
- OpenCode: `opencode.jsonc` → `mcp.servers.code-review-graph` (formato V2).
- Todos los clientes resuelven el repo con `git rev-parse --show-toplevel`, nunca con ruta
  absoluta: la laptop usa `/home/jnovoas/Proyectos` y fenix `/home/jnovoas/proyectos`.
- Los hooks (`.claude`, `.codebuddy`, `.gemini`) actualizan el grafo tras cada edición.
<!-- code-review-graph:end -->


