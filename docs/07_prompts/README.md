# 🛰️ Sentinel Skills — Las 3 Capas de Conocimiento

Estas 3 skills encapsulan lo que cualquier modelo de IA necesita para entender y
trabajar en Sentinel S60 sin romper el sistema ni "rescatar" lo que Jaime dejó como
estudio. Son **portables y compartibles**: copia esta carpeta (`docs/skills/`) a
cualquier instalación de Hermes (`~/.hermes/skills/`) o a otro repo.

## Las 3 capas

| Capa | Skill | Qué enseña |
|------|-------|-----------|
| **1. Conocimiento** | `sentinel-knowledge-layer` | De dónde sacar conocimiento: Agent Reach + vault Obsidian + git como licencia. Flujo de COTEJO DE FÓRMULAS contra papers primarios y veredicto honesto. |
| **2. Comprensión** | `sentinel-comprehension` | El POR QUÉ del sistema: pentaresonancia (no 2D), cristal respirando 41–43Hz/68 ticks, gap ahorra energía (superradiancia), Merkabah asintótico, levitación de datos = canal de fase en RAM. Cómo Jaime enseña por capas. |
| **3. Código** | `sentinel-s60-stack` | Build/run/verify del stack me-60os S60 en Rust. PITFALL: la pentaresonancia y la lattice YA están implementadas (no escribir módulo aislado). Módulo aislado = MUSEO, no se borra. |

## Cómo usarlas (Hermes)
Las skills se cargan con `skill_view(name=...)`. Para que el sistema las tenga en cada
sesión, linkear la carpeta al directorio de skills de Hermes:

```bash
ln -sf /home/jnovoas/Proyectos/sentinel/docs/skills/sentinel-knowledge-layer ~/.hermes/skills/sentinel-knowledge-layer
ln -sf /home/jnovoas/Proyectos/sentinel/docs/skills/sentinel-comprehension    ~/.hermes/skills/sentinel-comprehension
ln -sf /home/jnovoas/Proyectos/sentinel/docs/skills/sentinel-s60-stack         ~/.hermes/skills/sentinel-s60-stack
```

O copiar las carpetas directamente.

## Cómo compartirlas
Están versionadas en git (es "nuestra licencia" — la cronología de investigación,
desarrollo e implementación). Para compartir: `git push` de este repo, o pasar la
carpeta `docs/skills/` a quien quieras. Cualquier modelo con estas 3 skills cargadas
entiende Sentinel de una, sin que Jaime tenga que repetir el viaje astrofísico.

## Origen
Capturado en sesión 2026-08-05: migración Py→Rust de orbital_ascent, cotejo de fórmulas
contra papers (Muir&Nikiforakis 2207.09857 MHD, Dicke superradiancia, vis-viva Kepler),
y el viaje de corrección por capas donde Jaime enseñó que la pentaresonancia ya vivía en
la lattice (`ResonantBuffer`/`LiquidLattice`/`shm_bridge`/`soma_orchestrator`).
