# GEMINI.md — Sentinel

> **[DIRECTIVA MAESTRA YATRA PARA GEMINI]**
> **OBLIGATORIO**: Al iniciar cualquier interacción en este repositorio, DEBES leer inmediatamente los archivos `PROMPT_GLOBAL_AGENTES.md` y `tasks/lessons.md`.
> Estás obligado a acatar las 6 reglas de orquestación, subagentes, verificación empírica y automejora. Eres el custodio de Fenix y la delegación de Claude. No des un solo paso sin un plan (`tasks/todo.md`).

## Contexto actualizado (2026‑07‑25)

- **Gobernanza ITIL 4 / ISO 20000‑1 / ISO 27001** – carpeta `governance/` (ver `CLAUDE.md` para lista completa).
- **Traducción EN → ES** – backlog en `ENGLISH_MD_LIST.md`; memoria persistente en `.opencode/memory.md`.
- **Nodo Fenix** – único servidor Podman rootless; stack Rust + eBPF + PyO3.
- **YATRA Lock** – prohibido `f32`/`f64` en lógica base‑60 (eBPF lo bloquea).

## Próximas acciones prioritarias
1. Traducir `README.md` → `README_es.md`
2. Traducir `CLAUDE.md` → `CLAUDE_es.md`
3. Generar script de traducción por lotes (Argos‑Translate / LibreTranslate) para el resto de `*.md` marcados como **Inglés** en `ENGLISH_MD_LIST.md`.