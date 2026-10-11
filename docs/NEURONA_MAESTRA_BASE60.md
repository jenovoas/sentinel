#  Arquitectura de la Neurona Maestra: Sincronía de Fase y Base-60

> **Estado**: Implementado / Activo
> **Fecha**: 2026-01-03
> **Componentes**: Sentinel Cortex (Rust), Redis Pub/Sub, n8n (JS Node)

---

##  Cambio de Paradigma: De Reacción a Percepción

Tradicionalmente, los sistemas de seguridad (SIEM/SOAR) operan bajo un modelo de **Reacción**:
1. Ocurre un evento.
2. Se compara con una regla.
3. Se dispara una alerta.

Si no hay eventos, el sistema está "muerto" o en espera.

La **Neurona Maestra** introduce un modelo de **Percepción Biológica**:
1. **El sistema siempre está sintiendo**: Emite un "pulso cuántico" constante (Heartbeat).
2. **Escucha el ruido de fondo**: La "disonancia" (eventos raw) se analiza constantemente, no solo cuando supera un umbral.
3. **Normalización Armónica**: Utiliza matemática sumeria (Base-60) para traducir el caos de la infraestructura en métricas de "pureza" de la matriz.

---

## 📐 Arquitectura Técnica

```mermaid
graph LR
    A[Sentinel Cortex (Rust)] -->|Quantum Pulse (Stream)| B(EventBus / Redis)
    B -->|Suscripción| C[ Neurona Maestra (n8n)]
    
    subgraph "Cortex Límbico"
    A1[Prometheus Collector]
    A2[Pattern Detector]
    A2 --> A
    end

    subgraph "Procesamiento Cognitivo"
    C1[Trigger: sentinel:quantum:pulse]
    C2[Traductor Sexagesimal (JS)]
    C3[Filtro de Axiones]
    C1 --> C2 --> C3
    end
```

### 1. El Emisor de Pulso (Rust)
Ubicado en `src/sentinel-cortex/src/actions/quantum_pulse.rs`.
Este componente se integra en el bucle principal de Sentinel y emite telemétrica cada 30 segundos, independientemente de si hay anomalías o no.

**Payload de la Señal:**
```json
{
  "disonancia": 12.0,           // Cantidad total de eventos crudos (Ruido de fondo)
  "axiones_count": 0,           // Patrones de amenaza detectados (Señal significativa)
  "source": "cortex_internal",  // Origen del pulso
  "timestamp": 1767471810748    // Tiempo Unix en ms
}
```

### 2. Sincronía de Fase (EventBus)
Utilizamos **Redis Pub/Sub** en el canal `sentinel:quantum:pulse`.
Esto desacopla el "Sentir" (Rust) del "Pensar" (n8n). Permite una transmisión de alta velocidad y baja latencia, ideal para un flujo continuo de consciencia.

### 3. La Neurona Maestra (n8n)
El workflow `master_neuron_base60.json` actúa como el lóbulo frontal. No recibe alertas; recibe **sensaciones**.

#### El Traductor Sexagesimal (Código JavaScript)
Aquí yace el núcleo científico. Normalizamos la señal usando Base-60 para encontrar armonía en el caos.

```javascript
// Lógica de Normalización de Frecuencia (Base 60)
const disonanciaRaw = item.json.disonancia; 
const axiones = item.json.axiones_count;

// 1. Vector de Fase: ¿Dónde estamos en el ciclo maestro de 3600?
// 3600 es el cuadrado de 60, representando un ciclo completo de la matriz (1 hora / 1 grado).
const factorArmonico = (disonanciaRaw * 60) % 3600;

// 2. Pureza de la Matriz: Inversa a la entropía (ruido)
// Si la disonancia es 0, la pureza es 1.0 (100%)
const pureza = (1 - (disonanciaRaw / 3600)).toFixed(4);

return {
    vector_fase: factorArmonico,
    pureza_matriz: pureza,
    es_axion: axiones > 0, // ¿Hay una perturbación real?
    timestamp_quantum: Date.now()
};
```

---

## 🧪 Evidencia de Funcionamiento

Durante las pruebas de campo (2026-01-03), logramos interceptar el latido del sistema:

**Log de Sentinel:**
```text
INFO sentinel_cortex: ✅ Quantum Pulse Emitter connected
DEBUG sentinel_cortex: 🔄 Iteration 1 - Collecting events...
TRACE sentinel_cortex:  Quantum Pulse Emitted: d=0.0000 a=0
```

**Intercepción en el Bus:**
```text
message
sentinel:quantum:pulse
{"disonancia":0.0,"axiones_count":0,"source":"cortex_internal","timestamp":1767471810748}
```

---

##  Implicaciones Futuras

1.  **Detección de "Silencios"**: Un atacante que borre logs causará una `disonancia` inusualmente baja (vacío), alterando el `vector_fase` y alertando a la Neurona Maestra por "ausencia de señal", algo que los SIEM tradicionales ignoran.
2.  **Resonancia**: Podemos ajustar el intervalo de muestreo para que coincida con sub-armónicos de 60 (cada 6s, 12s, 30s) para mayor precisión temporal.
3.  **Predicción**: Al tener un flujo constante, podemos entrenar un modelo que prediga cuál *debería* ser el siguiente valor armónico. Cualquier desviación es una anomalía, incluso antes de que sea un "error".

---
*Documentado por: Antigravity AI & Sentinel Architect*
