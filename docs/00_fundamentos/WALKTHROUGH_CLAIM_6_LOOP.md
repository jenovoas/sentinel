# Walkthrough - Claim 6: Ciclo Cognitivo del Kernel (Cognitive Loop)

## Objetivo
Validar el **Ciclo Cognitivo** ("El Eslabón Perdido"):
1.  **Kernel** bloquea un binario desconocido.
2.  **IA en Userspace** analiza la intención.
3.  **Mapa del Kernel** se actualiza dinámicamente para permitir/bloquear.

## Configuración
-   **Programa eBPF**: `guardian_cognitive.o` (Hook LSM).
-   **Ciclo Cognitivo**: `scripts/cognitive_loop.py` (Python + IA Simulada).
-   **Comunicación**: `/sys/kernel/debug/tracing/trace_pipe` $\to$ `bpftool map update`.

## Pasos de Verificación (Ejecutados)

### 1. Binario Seguro ("Desconocido")
**Comando**: `/tmp/safe_deployment_v1`
-   **Resultado 1 (T=0s)**: `BLOCKED` (Política por defecto: Denegar).
-   **Log**: `Guardian [BLOCK]: Unknown binary ...`
-   **Análisis IA**: "Contexto implica operación legítima (safe)." $\to$ **PERMITIR**.
-   **Acción**: Añadido a la lista blanca dinámica.
-   **Resultado 2 (T=2s)**: `SUCCESS` (Permitido por el Kernel).

### 2. Binario Malicioso
**Comando**: `/tmp/malware_attack_v1`
-   **Resultado**: `BLOCKED`.
-   **Análisis IA**: "Amenaza detectada (malware)." $\to$ **BLOQUEAR**.
-   **Resultado 2**: Sigue `BLOCKED`.

## Conclusión
El **Ciclo del Kernel Cognitivo** está activo.
Hemos logrado unir exitosamente la **ejecución en Ring 0** con la **Inteligencia en Userspace**. El kernel ahora posee "Capacidades de Aprendizaje" mediadas por el ciclo cognitivo.
