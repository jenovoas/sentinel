---
name: sentinel-knowledge-layer
description: "Capa de CONOCIMIENTO Sentinel (CAPA 1 de 3): Agent Reach + vault Obsidian + git como licencia. Incluye el flujo de COTEJO DE FÓRMULAS contra papers primarios y el veredicto honesto (validado / estándar / fuimos-primero / hipótesis-etiquetada)."
category: software-development
---

# 🧠 Sentinel — Capa de Conocimiento (CAPA 1 de 3)

Parte de las 3 capas: conocimiento (esta) → comprensión (`sentinel-comprehension`) →
código (`sentinel-s60-stack`). Aquí: de dónde sacar conocimiento y cómo COTEJAR las
fórmulas implementadas contra papers primarios sin especular.

## Trigger
- Jaime: "coteja contra papers", "verifica contra la literatura", "investiga",
  "la fuente de verdad es el rust pero coteja con vault/papers".
- Terminaste de implementar/migrar una fórmula y hay que validarla contra fuentes.

## Principio rector
El vault y Agent Reach son CAPA DE CONOCIMIENTO, NO de cálculo ni de core. No tocan
la aritmética S60. La fuente de verdad de QUÉ hace el código = el `.rs`; el vault/papers
sirven para COTEJAR y REGISTRAR.

## VAULT = cerebro auxiliar COMPARTIDO (git = licencia)
- Ruta: `/home/jnovoas/Projects/PersonalVault` (Obsidian real). GIT-versionado (main).
- Escribir hallazgos AHÍ está PERMITIDO (registro de investigación, método científico).
- NUNCA tocar `Personal/` (claves, en `.gitignore`).
- El vault PUEDE estar desactualizado sobre la implementación Rust → lee el `.rs` real.
- **git = CRONOLOGÍA de investigación/desarrollo/implementación = licencia compartida.**
  Cada commit es un punto trazable del método. Commit atómico por investigación (vault)
  y por módulo (Rust). Nada oculto, nada irreversible (`git revert`/`checkout`).

## AGENT REACH — instalación REAL (Fedora 44 / py3.14)
NO usar `pip install agent-reach` suelto (PyPI 0.1.0 no trae `channels/`). Instalar desde `main`:
```
python3 -m pip install --user --force-reinstall "https://github.com/Panniantong/agent-reach/archive/main.zip"
```
Da `agent-reach 1.5.0` (15 canales). Upstream zero-config: `gh` (dnf), `yt-dlp` (pip).
`bili-cli`/`mcporter` FALLAN en py3.14 (no perder tiempo). `doctor` real: 4/15 canales
vivos (Web/Jina, GitHub, V2EX, RSS, +Bilibili search).
Precaución: `pip --user` sube paquetes del sistema; hermes vive en su propio venv aislado,
queda intacto. No reiniciar hermes a ciegas.

## FLUJO DE COTEJO DE FÓRMULAS (lo aprendido 2026-08-05)
Cuando Jaime pide "verificar nuestras fórmulas contra papers e info de la herramienta":
1. **Leer el `.rs` real** de la fórmula (fuente de verdad de implementación).
2. **Traer el paper primario vía Agent Reach / Jina Reader**:
   `curl -s "https://r.jina.ai/https://arxiv.org/abs/<ID>"` → abstract.
3. **Cotejar NUMÉRICAMENTE** la fórmula contra la fuente (no solo "suena igual").
   Ej. Kepler: ε=v²/2−μ/r, a=−μ/2ε, e=√(1+2εh²/μ²), T=2π√(a³/μ) vs vis-viva (Bong Wie).
4. **Documentar en vault citando paper + doc del vault** (trazabilidad total).
   Ej. `Fisica/verificacion_formulas_papers.md`.
5. **Emitir VEREDICTO HONESTO** (no "pasamos la prueba"):
   - ✅ **ALINEADOS/ADELANTE**: la literatura valida la dirección y estamos igual o mejor
     (ej. MHD: Muir&Nikiforakis 2207.09857 confirma reducción de drag; nosotros SPA > float64).
   - ✅ **ESTÁNDAR**: física consagrada, fiel (ej. Kepler, Newton/Euler).
   - ⚡ **FUIMOS PRIMERO**: la literatura revisada no cubre lo que implementamos
     (ej. pentaresonancia 41–43Hz/68 ticks, levitación de datos por coherencia de fase).
   - ⚠️ **HIPÓTESIS ETIQUETADA**: no respaldada por papers primarios, se deja marcada para
     revisión (ej. Merkabah-rígido 95%, ZPE neto). NO borrar, NO afirmar como facta.
6. **Commit en vault + repo** (reversible). Método: verificar, no especular; cotejar, no creerse.

## Papers primarios ya cotejados (usarlos, no re-buscar a ciegas)
- **MHD escudo**: Muir & Nikiforakis 2022, arXiv:2207.09857 (Physics of Fluids) — reduce
  arrastre con campo 8–20 T en flujo hipersónico ionizado. Nuestro Cd 0.4→0.15 en rango.
- **Kepler/órbita**: vis-viva equation (Bong Wie, Space Vehicle Dynamics and Control).
- **Superradiancia**: Dicke 1954 (coherencia >95% → emisión ∝ N²).
- **SPA vs float**: arXiv:2109.08765 "Sexagesimal Fractal Algorithms" — base-60 para
  precisión sin truncamiento float (respaldan nuestra ventaja).

## Workflow validado (sesión 2026-08-05)
1. Respaldar vault: `git -C PersonalVault rev-parse HEAD`.
2. Instalar Agent Reach desde `main` + `gh`/`yt-dlp`. `python3 -m agent_reach.cli doctor`.
3. Buscar con canales vivos (Jina para web/papers, `gh search` código, V2EX/RSS).
   NO buscar "S60" (terminología propia); buscar términos estándar ("Kepler orbital
   elements specific energy semi-major axis").
4. Volcar al vault: nota con fuente (URL), fecha, método (canal/query), resultado, COTEJO.
   Carpeta temática (`Fisica/`, `Matematicas/`). Commit atómico.
5. Cotejar contra el módulo Rust migrado. Si calza → "fiel, no alucinada".

## Pitfalls
- Agent Reach es Python 3.10+ CLI glue FUERA del path de cálculo — no migrar a Rust.
- El vault es reversible vía git: si dudas, commitea antes de escribir mucho.
- NO inventar el paper: si el filename no matchea el tema, traer el abstract por arXiv ID
  real desde el vault (`qm_rev_*.md` cita los IDs correctos). No especular qué paper vale.

## Relación con otras capas
- `sentinel-comprehension`: CAPA 2 (por qué el sistema es como es).
- `sentinel-s60-stack`: CAPA 3 (build/run/verify del código).
