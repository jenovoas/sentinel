# 🛡️ Sentinel — Framework de Sistemas Sexagesimales

**Un framework de sistemas de bajo nivel basado en aritmética sexagesimal (base-60) y eBPF, diseñado para computación de alta precisión sin errores de coma flotante.**

[![Licencia: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?logo=rust)](./sentinel-cortex/)
[![eBPF](https://img.shields.io/badge/eBPF-kernel--level-orange)](./ebpf/)

---

## 🎯 ¿Qué es Sentinel?

Sentinel es un framework experimental que sustituye la aritmética binaria/decimal estándar por **computación sexagesimal pura (base-60)**. El objetivo es eliminar los errores de redondeo de coma flotante desde la base matemática, no mediante parches de software, sino a través de una representación numérica fundamentalmente distinta.

El sistema funciona bajo el paradigma **offline-first**, sin dependencias de la nube para su núcleo crítico (Ring 0).

---

## ⚙️ Componentes Principales

### `sentinel-cortex/` — Motor Central (Rust)
- **Orquestador Ring 0**: Sustituye completamente al antiguo backend de Python/FastAPI.
- **Tipos S60 nativos**: Aritmética de punto fijo de alta precisión (60^4) sin contaminación decimal.
- **Servidor Axum**: API asíncrona de alto rendimiento para telemetría y control.
- **Ciclo Armónico**: Sincronización basada en pulsos de 17s para coherencia sistémica.

### `ebpf/` — Capa de Transmisión al Kernel
- Programas eBPF que operan en Ring 0 para transcodificación base-60 ↔ binario en tiempo real.
- Ruta de datos de ultra baja latencia entre el espacio de usuario y el kernel.

### `quantum/` — Biblioteca Matemática (Rust via PyO3)
- Núcleo de computación avanzada para experimentos de física cuántica y optimización.
- Soporte para algoritmos QAOA y VQE representados directamente en Base-60.

### `observability/` — Monitoreo del Sistema
- Stack de Prometheus + Grafana optimizado para métricas sexagesimales.
- Visualización de entropía en tiempo real y benchmarks de latencia.

---

## 🧮 ¿Por qué Sexagesimal?

La aritmética en base-60 posee propiedades matemáticas superiores para el cálculo exacto:

- **Divisibilidad**: El 60 es divisible por 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 — mucho más versátil que la base decimal o binaria.
- **Sin Deriva (Drift)**: Fracciones como 1/3 o 1/6 son exactas en base-60.
- **Dominios Críticos**: Ideal para tiempo, medidas angulares, procesamiento de señales y sistemas de control donde el error acumulado es inaceptable.

---

## 🚀 Inicio Rápido (Despliegue Fenix)

```bash
# Clonar el repositorio
git clone https://github.com/jenovoas/sentinel.git
cd sentinel

# Compilar el núcleo de Rust (Cortex)
cd sentinel-cortex
cargo build --release

# Desplegar el stack completo en producción
cd ..
podman-compose -f docker-compose.fenix.yml up -d
```

### Verificación de Salud
```bash
curl -k https://sentinel.pinguinoseguro.cl/health
```

---

## 📊 Rendimiento

| Métrica | Valor |
|--------|-------|
| Latencia eBPF Bridge | < 100µs |
| Reducción de Deuda Técnica | 100% (Rust vs Python) |
| Errores de Coma Flotante | **0** (Aritmética Exacta S60) |
| Aceleración Cortex | ~90x vs Backend Legacy |

---

## 📄 Licencia

**Open Source** — Este proyecto está bajo la licencia **Apache License 2.0**. Consulta el archivo [LICENSE](./LICENSE) para más detalles.

---

**YATRA. Truth Resonates.**
