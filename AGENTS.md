# ARQUITECTURA Y DIRECTIVAS PARA AGENTES E IA (REGLAS DE ORO DEL PROYECTO SENTINEL)

> **Infraestructura compartida 2026-08-26:** `fenix` se usa para desarrollo y
> compilación, además de `dns1.pinguinoseguro.cl`; `kingu` para producción
> contenerizada, Traefik y `dns2.pinguinoseguro.cl`. Este aviso no sustituye la
> verificación del nodo/runtimes activos. Referencia:
> `/home/jnovoas/proyectos/sysdocs/02-topologia-y-metodologia-transicion-2026-08-26.md`.
>
> **RAMAS POR ENTORNO.** `main` corresponde al entorno systemd. `alpine_fenix` corresponde al entorno Alpine/OpenRC. Son ramas independientes y no se deben mezclar.
> Los cambios de systemd se aplican únicamente en `main`; los cambios de Alpine se aplican únicamente en `alpine_fenix`. Se permite hacer checkout, commit y push en la rama del entorno correspondiente.
> Prohibido hacer merge entre `main` y `alpine_fenix`, copiar configuraciones de una plataforma a la otra o usar `develop` u otra rama como sustituto de estos entornos.

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

## Conocimiento del Código y Navegación (graphify)

Este proyecto cuenta con soporte de grafo de conocimiento local mediante **graphify**.

### Reglas de consulta e interacción:
- Si existe `graphify-out/graph.json`, ejecuta `graphify query "<pregunta>"` antes de realizar búsquedas textuales masivas (`grep`/`find`).
- Utiliza `graphify path "<A>" "<B>"` para rastrear dependencias o relaciones entre dos módulos o componentes.
- Utiliza `graphify explain "<concepto>"` para explicaciones enfocadas de nodos y su vecindario arquitectónico.
- Si existe `graphify-out/wiki/index.md` o `graphify-out/GRAPH_REPORT.md`, consúltalos para navegación arquitectónica global.
- Tras realizar cambios importantes en el código, ejecuta `graphify update .` para mantener el grafo sincronizado (análisis AST local sin consumo de tokens de API).
- Para construir o reconstruir el grafo completo, utiliza el comando `/graphify .`.
