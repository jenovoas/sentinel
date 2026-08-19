# 🧪 Propuesta de Diseño: Batería de Pruebas de Estrés y Carga Concurrente (Sentinel S60)

> **Autor:** Antigravity AI  
> **Ubicación del Script:** [`scripts/stress_test_sentinel.py`](file:///home/jnovoas/Proyectos/sentinel/scripts/stress_test_sentinel.py)  
> **Fecha:** 29 de Julio, 2026

---

## 🎯 1. Objetivos de la Prueba de Estrés

1. **Medición de Latencia en Verificación de Claims (< 1ms Target)**:
   Verificar el rendimiento del motor `truthsync_core` con la constante sexagesimal de Plimpton 322 $\psi = 4.7962963$ bajo carga concurrente alta.
2. **Resiliencia de AIOpsShield en Carga (Ataques AIOpsDoom Inyectados)**:
   Evaluar que los payloads maliciosos (`rm -rf`, `drop database`, `systemctl stop`) sean interceptados e inscriptos en el **Security Lane WAL** sin degradar los hilos de Axum / Tokio.
3. **Estabilidad de la Rejilla Resonante de 128 Nodos y PAI-Neural SNN**:
   Verificar que la ingesta masiva de eventos no cause desbordamiento de memoria ni fugas en los mapas eBPF de Ring-0 (`/sys/fs/bpf/cortex_events`).

---

## 🔬 2. Matriz de Escenarios Diseñados

| Escenario | Concurrencia (Hilos) | Peticiones Totales | Mezcla de Payloads | Criterio de Éxito |
| :--- | :--- | :--- | :--- | :--- |
| **1. Carga Ligera (Warmup)** | 10 hilos | 500 reqs | 100% Verificación Válida | P95 < 2.0 ms |
| **2. Carga Nominal Producción** | 50 hilos | 2,000 reqs | 80% Válidos, 20% AIOpsDoom | P95 < 5.0 ms, 0% Crash |
| **3. Prueba de Estrés Extremo** | 200 hilos | 10,000 reqs | 50% Válidos, 50% Ataque Malicioso | Zero Loss en WAL, 100% Retención LiquidLattice |

---

## 🚀 3. Instrucciones de Ejecución

El script está listo en `scripts/` (respetando las directivas del proyecto):

```bash
# Ejemplo: Ejecutar prueba nominal de 1,000 peticiones con 50 hilos concurrentes
python3 scripts/stress_test_sentinel.py -c 50 -n 1000
```

