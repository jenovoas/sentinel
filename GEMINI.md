<!-- codebase-memory-mcp:start -->
# Grafo de conocimiento del código (codebase-memory-mcp)

Este proyecto usa codebase-memory-mcp para mantener un grafo de conocimiento del código.
SIEMPRE prefiere las herramientas MCP del grafo en lugar de grep/glob/búsqueda de archivos para explorar el código.

## Orden de prioridad
1. `search_graph` — buscar funciones, clases, rutas y variables por patrón
2. `trace_path` — rastrear quién llama a una función o qué funciones llama
3. `get_code_snippet` — leer el código fuente de una función o clase específica
4. `query_graph` — ejecutar consultas Cypher para patrones complejos
5. `get_architecture` — obtener un resumen general del proyecto
6. `detect_changes` — inspeccionar archivos modificados y su radio de impacto

## Cuándo recurrir a grep/glob
- Al buscar cadenas literales, mensajes de error o valores de configuración
- Al buscar en archivos que no son de código (Dockerfiles, scripts de shell, archivos de configuración)
- Cuando las herramientas MCP no entreguen resultados suficientes

## Ejemplos
- Buscar un controlador: `search_graph(project="sentinel", name_pattern=".*OrderHandler.*")`
- Saber quién lo llama: `trace_path(project="sentinel", function_name="OrderHandler", direction="inbound")`
- Leer el código fuente: `get_code_snippet(project="sentinel", qualified_name="pkg/orders.OrderHandler")`
<!-- codebase-memory-mcp:end -->
---

# Despliegue operativo

- Nodo único por ahora: `fenix`, Alpine Linux, IP pública `172.233.24.102`. El segundo servidor espera a que Fenix esté listo. Sin gasto de datacenter.
- Rama: `alpine_fenix` únicamente. Prohibido crear ramas. Prohibido usar `main`.
- Daemons nativos: OpenRC; stack auxiliar: Docker Compose; TLS: Nginx.
- `soma_orchestrator` y `soma_worker` permanecen WIP y están excluidos del
  arranque; `neural-guard` sigue con motor de correlación parcial.

---

# INTEGRACIÓN CON LA BÓVEDA DE OBSIDIAN
- **Bóveda de Obsidian**: `/home/jnovoas/Proyectos/personalvault`

## graphify

Este proyecto tiene un grafo de conocimiento en graphify-out/, con nodos principales, estructura de comunidades y relaciones entre archivos.

Reglas:
- Si existe graphify-out/graph.json, ejecuta `graphify query "<question>"` antes de usar grep, buscar o leer por primera vez un archivo fuente para responder una pregunta sobre el código. Incluye esta regla en cada instrucción para subagentes que exploren código. Lee archivos directamente solo en las líneas que el grafo o una lectura anterior ya haya ubicado. Usa `graphify path "<A>" "<B>"` para consultar relaciones y `graphify explain "<concept>"` para conceptos específicos. Estas herramientas devuelven un subgrafo acotado, normalmente mucho más pequeño que GRAPH_REPORT.md o la salida de grep sin filtrar.
- Si existe graphify-out/wiki/index.md, úsalo para la navegación general en lugar de explorar directamente el código fuente.
- Lee graphify-out/GRAPH_REPORT.md solo para una revisión general de la arquitectura o cuando query/path/explain no aporten suficiente contexto.
- Después de modificar código, ejecuta `graphify update .` para mantener actualizado el grafo (solo AST, sin coste de API).
- En cada compilación se reescribe por completo graphify-out/graph.json si está versionado; por eso es esperable que aparezca un diff grande en una solicitud de cambios. No lo señales como ruido ni sugieras omitir la actualización del grafo o sus hooks.

<!-- code-review-graph MCP tools -->
## Herramientas MCP: code-review-graph

**Este proyecto tiene un grafo de conocimiento. Empieza con las herramientas MCP
code-review-graph para acotar el alcance y luego lee el código fuente.** Consultar el grafo cuesta menos que recorrer archivos y
aporta contexto estructural (quién llama a qué, dependencias y cobertura de pruebas) que la búsqueda de archivos no ofrece.

### Cuándo usar PRIMERO las herramientas del grafo

- **Explorar código**: usa `semantic_search_nodes_tool` o `query_graph_tool` en lugar de Grep
- **Entender el impacto**: usa `get_impact_radius_tool` en lugar de rastrear importaciones manualmente
- **Revisar código**: usa `detect_changes_tool` + `get_review_context_tool` en lugar de leer archivos completos
- **Encontrar relaciones**: usa `query_graph_tool` con callers_of/callees_of/imports_of/tests_for
- **Consultar la arquitectura**: usa `get_architecture_overview_tool` + `list_communities_tool`

### Verificar en el código fuente

- Acota el alcance con el grafo y luego lee el código fuente. No modifiques código basándote únicamente en los resultados del grafo.
- Para cualquier cambio no trivial, lee la implementación y las pruebas pertinentes antes de llegar a una conclusión.
- Verifica el código fuente exacto cuando modifiques comportamiento, lógica de base de datos, migraciones, reintentos, mecanismos alternativos,
  recuperación o compatibilidad.
- Si el grafo y el código fuente discrepan, prevalece el código fuente. El grafo podría estar desactualizado o no
  representar esa relación.
- Un resultado vacío del grafo puede significar «no está indexado» o «no es visible estáticamente», no «no existe».

### Herramientas principales

| Herramienta | Cuándo usarla |
| ------ | ---------- |
| `detect_changes_tool` | Revisar cambios de código: proporciona un análisis con puntuación de riesgo |
| `get_review_context_tool` | Obtener fragmentos del código fuente para una revisión de forma eficiente en tokens |
| `get_impact_radius_tool` | Entender el alcance de impacto de un cambio |
| `get_affected_flows_tool` | Encontrar las rutas de ejecución afectadas |
| `query_graph_tool` | Rastrear quién llama, llamadas realizadas, importaciones, pruebas y dependencias |
| `semantic_search_nodes_tool` | Encontrar funciones o clases por nombre o palabra clave |
| `get_architecture_overview_tool` | Entender la estructura general del código |
| `refactor_tool` | Planificar renombrados y encontrar código sin uso |

### Flujo de trabajo

1. El grafo se actualiza automáticamente cuando cambian los archivos (mediante hooks).
2. Usa `detect_changes_tool` para revisar cambios de código.
3. Usa `get_affected_flows_tool` para entender el impacto.
4. Usa `query_graph_tool` con pattern="tests_for" para comprobar la cobertura.
<!-- /code-review-graph MCP tools -->

## Skills del sistema Sentinel / S60

Al trabajar en Sentinel, MyCNet o ME-60OS, consulta y aplica las skills disponibles `sentinel-knowledge-layer`, `sentinel-comprehension` y `sentinel-s60-stack` en `.agents/skills/` antes de tareas de investigación, arquitectura, matemáticas, integración o código. Para tareas específicas, carga la capa pertinente; en cambios que crucen capas, carga las tres. Las skills también están enlazadas en `.claude/skills/`, `.gemini/skills/` y `.opencode/skills/`. En Hermes están instaladas en `~/.hermes/skills/`. Si una skill difiere de estas instrucciones vigentes, del código fuente o de la evidencia verificable, prevalecen estos últimos; conserva los detalles obsoletos como contexto histórico y no los afirmes como estado actual.
