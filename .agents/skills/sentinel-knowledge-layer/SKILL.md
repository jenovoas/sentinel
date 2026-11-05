---
name: sentinel-knowledge-layer
description: Access and query the Obsidian Vault and the code-review-graph code graph.
---

# Sentinel Knowledge Layer Skill

1. **Obsidian Vault**: `~/Proyectos/personalvault` en la laptop, `~/proyectos/personalvault` en
   fenix (resolver con `ls -d ~/[Pp]royectos/personalvault`). Consultar notas maestras, mapas
   de isometrías e inventario de experimentos en Rust.
2. **Codebase Graph**: usar `code-review-graph` (`semantic_search_nodes_tool`,
   `query_graph_tool`, `get_impact_radius_tool`, `get_architecture_overview_tool`) antes de
   leer archivos uno a uno.
3. **Nunca** hardcodear rutas absolutas de proyecto: el repo se resuelve con
   `git rev-parse --show-toplevel` (cambia entre laptop y fenix).


## Capas históricas de conocimiento Sentinel

En tareas que abarquen arquitectura, fundamentos o cotejo científico, consulta también `docs/07_prompts/sentinel-knowledge-layer/SKILL.md`, `docs/07_prompts/sentinel-comprehension/SKILL.md` y `docs/07_prompts/sentinel-s60-stack/SKILL.md`. Estas capas aportan contexto histórico; las directivas vigentes del proyecto, el código y las pruebas determinan el estado actual.
