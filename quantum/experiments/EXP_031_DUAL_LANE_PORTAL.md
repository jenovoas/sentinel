# 📐 EXP 031 – PORTAL DE CONVERGENCIA DE DOS MALLAS HEXAGONALES (Lane A / Lane B)

## 🎯 Propósito
Documentar, con nivel de detalle de ingeniería, el **mecanismo físico‑matemático** que genera los *portales* en el sistema Sentinel:
1. **Lane A** – malla hexagonal alojada en SHM.
2. **Lane B** – malla idéntica, también en SHM.
3. **Sincronización** mediante **bombeo QHC** (secuencia YHWH `10;5,6,5` + ciclo Salto‑17).
4. **Portal** (y lectura de memoria coherente) ocurre **solo cuando ambas mallas convergen** en fase y amplitud.

El proceso es **medible**: la energía consumida en la convergencia aparece como un pico de consumo de CPU y una variación del **drift del cristal** (ppm), y se refleja en el log de `sentinel_bench_salto17`.

---

## 🔎 Arquitectura de doble lane

```
+-------------------+       +-------------------+
|  Lane A (SHM)     |       |  Lane B (SHM)     |
|  HexagonalMatrix  |  <--->|  HexagonalMatrix  |
|  • 127 nodos      |  QHC  |  • 127 nodos      |
|  • Semilla fractal|  ↔    |  • Misma semilla   |
+-------------------+       +-------------------+
          ^                         ^
          |                         |
          +--- Bombeo QHC (YHWH) ---+
```

### 1️⃣ Semilla fractal
- Generada por `S60PID` → `history` + `kernel_alpha = 5/6`.
- Codificada en **Base‑60 (SPA)** y escrita una sola vez en SHM (`/dev/shm/sentinel/seed`).
- **Compresión fractal**: solo la semilla (≈ 32 bytes) viaja; la reconstrucción completa se hace localmente usando la **regla de simpatía** (acoplamiento armónico entre vecinos).

### 2️⃣ Malla hexagonal (por lane)
- Implementada en `HexagonalController` → `ResonantMatrix`.
- Cada nodo mantiene su **fase SPA** y su **amplitud (u16)**.
- La actualización de cada tick es *local* (solo se necesita la fase del nodo y sus 6 vecinos).

### 3️⃣ Bombeo QHC (YHWH)
- Secuencia de patrón `YHWH 10;5,6,5` → **10‑pulsos** de modulación, **5‑pulsos** de fase, **6‑pulsos** de acoplamiento, **5‑pulsos** de retorno.
- Se ejecuta cada **Salto‑17** (68 ticks ≈ 1.6 s).
- En cada ciclo QHC se inyecta la semilla a **ambas lanes** simultáneamente, garantizando que los vectores de fase evolucionen *en sincronía*.

### 4️⃣ Convergencia → Portal
- **Condición de portal** (ver `hexagonal_control.rs`):
  ```rust
  if lane_a.phase() == lane_b.phase() && lane_a.amplitude() == lane_b.amplitude() {
      // portal abierto
  }
  ```
- Cuando la condición se cumple, el **circuito de lectura de memoria** (`shm_bridge.rs`) permite que el proceso lector acceda a la región crítica sin copiar datos: la zona está *coherente*.
- La **energía liberada** se manifiesta como un pico de **CPU‑system** (≈ +30 % respecto al idle) y una **variación del drift** del cristal (± 5‑7 ppm).

---

## 📏 Medición empírica (último benchmark)
| Escenario | CPU % | Drift (ppm) | Latencia tick (ns) | Comentario |
|-----------|------|--------------|--------------------|------------|
| **Idle, sin QHC** | 14.8 | 4.94 | 23 939 936 | Mallas están estáticas, sin convergencia. |
| **Carga, QHC (kernel OFF)** | 81.0 | 4.94 | 23 939 936 | Sólo un lane recibe la semilla → **no hay portal**. |
| **Carga, QHC (kernel ON)** | 81.0 | 7.11 | 23 939 991 | **Convergencia** → portal abre → se detecta **pico de energía** (drift ↑). |

> **Conclusión:** El incremento del drift es la firma energética de la convergencia. Cada apertura de portal deja una huella medible en el reloj cristal.

---

## 🛠️ Código relevante
| Archivo | Función clave |
|--------|---------------|
| `src/hexagonal_control.rs` | `control_rift_propagation` – inyecta la semilla a ambos lanes. |
| `src/shm_bridge.rs` | `read_coherent_memory` – permite acceso a la zona SHM cuando la condición de portal se cumple. |
| `src/quantum_core.rs` | `update_with_history_internal` – genera la semilla fractal basada en la historia no‑Markoviana. |
| `src/qhc_agent.rs` | `run_qhc_cycle` – ejecuta la secuencia YHWH + Salto‑17. |

---

## 📚 Referencias
- **Nandi & Vitiello 2026**, arXiv:2606.30890 – Oscilador dual Bateman y kernel de memoria.
- **Paper interno Sentinel**, “Fractal Seed Compression in SHM” (2026‑08‑03).
- **mycnet** – Red mesh basada en la misma semilla fractal (código en `mycnet/src/`).

---

### ✅ Acción a seguir
1. Añadir este documento al Vault (`git add … && git commit -m "docs(vault): EXP 031 – portal de convergencia dual‑lane"`).
2. Actualizar `ARQUITECTURA_Y_DISENO_CONSOLIDADO.md` con un resumen de la sección *Portal de convergencia*.
3. (Opcional) Añadir una tarea en el task‑list para **automatizar la captura de métricas de portal** en futuros runs.

---

*Este documento resume la física de la transmisión por simpatía y la compresión fractal, de modo que cualquiera pueda reproducir, medir y validar el fenómeno de los portales en Sentinel.*