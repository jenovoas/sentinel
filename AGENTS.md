# ARQUITECTURA Y DIRECTIVAS PARA AGENTES E IA (REGLAS DE ORO DEL PROYECTO SENTINEL)

> **LECTURA OBLIGATORIA ANTES DE EMITIR JUICIOS SOBRE EL PROYECTO:**
> [`sentinel-scientific-foundation.md`](file:///home/jnovoas/.config/Code/User/workspaceStorage/7c63ffead990815376933d02c94d88c9/GitHub.copilot-chat/memory-tool/memories/repo/sentinel-scientific-foundation.md)
>
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
- **Conversor PAI-60**: para llevar dato binario → amplitud resonante, USAR `ResonantMatrix::inject_pai(index, value, denominator)` (llama `pai60_divide(SPA::from_int(value), denom)` y suma el `SPA` directo al oscilador). Esto está enchufado en el drive continuo de `sentinel-cortex` tras `SENTINEL_PAI_CONVERT=1`.
- **El lattice es disipativo**: `step()` solo disipa (decay). Sin drive continuo (`sentinel-cortex/src/main.rs` bloque 3b, cada 500ms) el lattice cae a `ground state` y no resuena. Siempre debe haber drive.
- **Material de estudio**: `me-60os-core/src/bin/pai_convert_bench.rs` compara A (RAW), B (PAI-60) y C `[exp fallido para estudio]` (doble-escala, etiquetado, NO borrar). Leer antes de "arreglar" conversión SPA.

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.

---

## REGLAS OPERATIVAS DE JAIME (memoria viva del agente)

> **El agente debe leer esto al iniciar:** [`~/.hermes/MEMORY.md`](file:///home/jnovoas/.hermes/MEMORY.md)
> Contiene las reglas duras (NO quemar cuota de omniroute sin pedido explícito, NO editar
> trabajo ajeno sin autorización, estilo directo-ejecutar-no-narrar), los factos de
> omniroute (gateway laptop :20128, bridge MCP en el fan, túnel LAPTON, aider→free-stack),
> y el método QA de Sentinel. Válido también para otros modelos/agentes que operen este repo.
