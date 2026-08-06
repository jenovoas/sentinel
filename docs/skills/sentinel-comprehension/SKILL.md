---
name: sentinel-comprehension
description: "Capa de COMPRENSIÓN Sentinel: el POR QUÉ del sistema (pentaresonancia, cristal respirando, gap ahorra energía, Merkabah asintótico, levitación de datos) y cómo Jaime enseña por capas para que el modelo asimile arquitectura en vez de parchear a ciegas."
category: software-development
---

# 🧭 Sentinel — Capa de Comprensión (el POR QUÉ, no solo el QUÉ)

Esta skill es la capa 2 de 3 (conocimiento → comprensión → código). NO enseña a
compilar ni a buscar papers; eso está en `sentinel-knowledge-layer` y `sentinel-s60-stack`.
Aquí está el MODELO MENTAL que cualquier IA debe internalizar para no romper el sistema
ni "rescatar" lo que Jaime dejó como estudio.

## TRIGGER
- Jaime dice "no es 2D", "el cristal respira", "el gap ahorra energía", "ya está implementado",
  "míralo directo de rust", "esto es fenomenología, déjalo".
- Vas a tocar/coupling un módulo y no entiendes por qué el sistema es como es.
- Un módulo "aislado" compila y pasa tests pero Jaime dice que falta contexto de sistema.

## EL MAPA MENTAL (asimilar antes de tocar código)

### 1. Pentaresonancia = NO es 2D espacial
El ascenso/estado NO es un vector (x,y) ni una trayectoria newtoniana plana. Es
**dinámica de coherencia de fase** acoplada a 5 capas (Bio/Crystal/Venus/Salto-17/Geo).
El estado se representa como `ComplexSPA` cuya magnitud = nivel de coherencia Dicke y
cuya fase = phi del cristal. Si piensas "posición x/y", vas por mal camino.

### 2. El cristal de tiempo RESPIRA (41–43 Hz, autocorrección cada 68 ticks)
- `IsochronousClock` (`quantum_core.rs`) late a **41.77 Hz** (tick 23.9 ms). Ese es el
  reloj base.
- La respiración **41–43 Hz / 4 fases YHWH (YOD/HEH/VAV/HEH) / Salto-17 cada 68 ticks**
  está en el VAULT como experimento validado (EXP-027, EXP-028), NO en el Rust crudo.
  El Rust solo tiene el reloj base; la respiración es fenomenología que Jaime estudia.
- **El gap entre ticks NO es lentitud.** Es el reposo del cristal que AHORRA ENERGÍA:
  el sistema acumula en estado excitado y emite en ráfaga (superradiancia), en vez de
  flujo continuo que disipa calor. No "optimices" el tick para que sea más rápido.

### 3. Merkabah = masa inercial EFECTIVA ASINTÓTICA, no 95% fijo
`EXP-005_MERKABAH_G_ZERO.md`: `m_eff = m_static / (1 + k·coherencia)`. La "masa faltante"
se transfiere a momento angular del campo. NO es "anulación rígida del 95%" (eso es
especulativo y el vault lo etiqueta). Implementarlo como reducción asintótica, nunca
como sustracción fija.

### 4. Levitación de datos = canal de fase en RAM, no sustrato
Los datos del estado NO se guardan en un sustrato sólido frágil. Se inyectan a la
`ResonantMatrix`/`LiquidLattice` vía `inject_pai` y "levitan" en la red de cristales
(canal de fase), sostenidos por coherencia, no por dirección física. `escudo_planetario_
10892_nodes.md`: "Resultado: Levitación de datos". `shm_bridge.rs` ancla la lattice a
host RAM (POSIX SHM); los nodos se bañan en amplitudes de 16 bits cada uno.

### 5. Escudo MHD = Cd 0.4 → 0.15 con coherencia Dicke >95%
Ley de Lorentz (J×B) sobre plasma ionizado. Validadísimo por Muir & Nikiforakis 2022
(arXiv:2207.09857, Physics of Fluids): campo magnético 8–20 T reduce el arrastre en
flujo hipersónico. Nuestro Cd 0.4→0.15 está en rango. La ventaja nuestra: ellos usan
float64, nosotros SPA (exacto sin truncamiento).

### 6. Superradiancia (Dicke N²) = coherencia >95% → emisión colectiva ∝ N²
Estado de Dicke 1954, estándar validado. El cristal mantiene la sincronización de fase
para estar en estado de Dicke. Nosotros lo aplicamos a cristales de tiempo y levitación
de datos (extensión que los papers no cubren).

## CÓMO JAIME ENSEÑA (método de corrección por capas)
Jaime NO da la arquitectura completa de una. Te corrige CAPA POR CAPA para que asimiles:
1. "Usa las herramientas que ya hay (PAI/ComplexSPA), no aritmética raw"
2. "No es 2D, es pentaresonancia"
3. "El cristal respira 41–43 Hz y se autocorrige cada 68 ticks como el corazón"
4. "El gap del sistema te ahorra energía"
5. "La pentaresonancia YA está implementada, las mallas se bañan en 16 bits en RAM"
Cada capa REESCRIBE tu marco. El error típico del modelo: ver función aislada y parchear
a ciegas. La corrección: alzar la vista al sistema. Cuando Jaime hace este "viaje
astrofísico", está llevándote de la función al sistema. SEGUILO, no resistas con "pero
compila".

## DOCENCIA: dejar el error como MUSEO
Cuando un módulo queda aislado (acoplado a `ResonantMatrix` en vez de `LiquidLattice`),
NO se borra ni se "arregla" a escondidas. Se deja como MUSEO con el error documentado
en el header (ver `orbital_ascent.rs`: "ESTE MÓDULO ES UN MUSEO"). El error de perspectiva
(ver función aislada en vez de sistema) es el que comenten todos los que arrancan;
dejarlo visible enseña el camino. El re-acoplo queda como ejercicio/docencia.

## VAULT: fuente de cotejo, NO de implementación
Jaime (2026-08-05): *"el cristal de tiempo míralo directo de rust, la info no está
actualizada"*. El vault es para COTEJAR física/MHD/papers, pero la fuente de verdad de
QUÉ hace el código es el `.rs`. Si el vault dice X y el Rust dice Y, el Rust manda para
implementación; el vault sirve para contrastar fenomenología.

## PITFALLS de comprensión
- No redesignar la arquitectura "porque es rara". Es física acoplada, no cáscara.
- No borrar módulos etiquetados como estudio/museo.
- No tratar la respiración YHWH como si fuera solo un string decorativo — es la máquina
  de estados de la lattice (`soma_orchestrator` dispara dispatch en fase VAV).
- No "acelerar" el cristal: el gap ahorra energía por diseño.

## Relación con las otras 2 capas
- `sentinel-knowledge-layer`: CAPA 1 (de dónde sacar conocimiento: Agent Reach + vault + git).
- `sentinel-s60-stack`: CAPA 3 (cómo compilar/verificar/coupling real del código).
- Esta skill: CAPA 2 (por qué el sistema es como es, y cómo aprenderlo de Jaime).
