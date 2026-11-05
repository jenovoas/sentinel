# 🛰️ Sentinel Skills — Las 3 Capas de Conocimiento

Estas 3 skills aportan contexto para trabajar en Sentinel S60 y sus proyectos relacionados.
La fuente maestra vive en `docs/07_prompts/`; cada proyecto mantiene copias locales activas
en `.agents/skills/`, enlazadas a los directorios de skills de Claude, Gemini y OpenCode.

## Las 3 capas

| Capa | Skill | Qué enseña |
|------|-------|-----------|
| **1. Conocimiento** | `sentinel-knowledge-layer` | De dónde sacar conocimiento: Agent Reach + vault Obsidian + git como licencia. Flujo de COTEJO DE FÓRMULAS contra papers primarios y veredicto honesto. |
| **2. Comprensión** | `sentinel-comprehension` | El POR QUÉ del sistema: pentaresonancia (no 2D), cristal respirando 41–43Hz/68 ticks, gap ahorra energía (superradiancia), Merkabah asintótico, levitación de datos = canal de fase en RAM. Cómo Jaime enseña por capas. |
| **3. Código** | `sentinel-s60-stack` | Build/run/verify del stack me-60os S60 en Rust. PITFALL: la pentaresonancia y la lattice YA están implementadas (no escribir módulo aislado). Módulo aislado = MUSEO, no se borra. |

## Activación por proyecto y agente

Las instrucciones `AGENTS.md`, `CLAUDE.md` y `GEMINI.md` de Sentinel, MyCNet y ME-60OS piden cargar estas skills al trabajar en investigación, arquitectura, matemáticas, integración o código. Las copias de `.agents/skills/` se exponen mediante enlaces relativos en `.claude/skills/`, `.gemini/skills/` y `.opencode/skills/`. Para Hermes u otro runtime, las instrucciones de proyecto señalan las copias canónicas y pueden consultarse directamente.

La skill local de conocimiento existente en Sentinel se conserva y complementa estas tres capas. Los textos de las skills guardan contexto histórico; prevalecen las instrucciones vigentes del proyecto, el código fuente y la evidencia verificable cuando haya discrepancias.

## Cómo compartirlas

Las skills maestras y las copias por proyecto están versionadas en sus respectivos repositorios. Al actualizar una skill, sincroniza las copias de los otros proyectos y conserva la misma precedencia de fuentes descrita arriba.

## Origen
Capturado en sesión 2026-08-05: migración Py→Rust de orbital_ascent, cotejo de fórmulas
contra papers (Muir&Nikiforakis 2207.09857 MHD, Dicke superradiancia, vis-viva Kepler),
y el viaje de corrección por capas donde Jaime enseñó que la pentaresonancia ya vivía en
la lattice (`ResonantBuffer`/`LiquidLattice`/`shm_bridge`/`soma_orchestrator`).
