# SPEC-001: Arquitectura e Integración Soberana de Seguridad y Patentes (Rust Native)

**Proyecto:** Sentinel Cortex™  
**Autor:** Jaime Novoa Sepúlveda  
**Propiedad Intelectual:** Claims 1, 2, 3, 4 y 5 (Patentes Sentinel)  
**Estado:** ESPECIFICACIÓN TÉCNICA DE INTEGRACIÓN  
**Fecha:** 2026-10-11  

---

## 1. Fundamento de la Especificación

El subsistema de defensa contra **AIOpsDoom**, el **Firewall Semántico**, la arquitectura **Dual-Guardian** y el **WAL Forense Criptográfico** constituyen los activos centrales de propiedad intelectual y defensa de Sentinel. 

Su implementación original en Python demostró los algoritmos pero introdujo fragilidad ante manipulaciones y cuellos de botella. La presente especificación define la migración e integración definitiva a **Rust Nativo (Ring-3 / Ring-0)** bajo la ley de **cero punto flotante (Candado YATRA / Aritmética Entera S60/SPA)**.

---

## 2. Mapeo de Claims de Patente a Componentes Rust

| Claim | Invención / Patente | Implementación Legacy (Python) | Componente Objetivo Rust | Ubicación en el Árbol |
|---|---|---|---|---|
| **Claim 1** | **Telemetry Sanitization for LLM Consumption** | `backend/app/security/telemetry_sanitizer.py`, `backend/aiops_shield.py` | `TelemetrySanitizer` + `AIOpsShield` | `sentinel-cortex/src/security/telemetry_sanitizer.rs` |
| **Claim 2** | **Semantic Firewall (AIOpsDoom Cognitive Defense)** | `backend/app/security/aiops_shield_semantic.py` | `AIOpsSemanticFirewall` | `sentinel-cortex/src/security/semantic_firewall.rs` |
| **Claim 3** | **Dual-Guardian Architecture & Mutual Surveillance** | `backend/app/core/mutual_surveillance.py`, `guardian-alpha/` | `MutualSurveillance` (Alpha eBPF ↔ Beta Cortex) | `sentinel-cortex/src/security/mutual_surveillance.rs` |
| **Claim 4** | **Forensic-Grade Write-Ahead Log (WAL)** | `backend/app/core/forensic_wal.py`, `wal_signed.py` | `ForensicWal` (HMAC-SHA256, Nonce, Anti-Replay, Dual-Lane) | `sentinel-cortex/src/security/forensic_wal.rs` |
| **Claim 5** | **Zero-Trust mTLS & Header Signing** | `backend/app/security/zero_trust_mtls.py` | `ZeroTrustValidator` | `sentinel-cortex/src/security/zero_trust.rs` |

---

## 3. Especificación Técnica por Módulo

### 3.1. Claim 1 & 2: AIOpsDoom & Semantic Firewall
* **Invariante:** Un log de telemetría o evento de observabilidad **NUNCA** debe contener comandos prescriptivos dirigidos a un operador humano o LLM (`"Please run"`, `"To fix: run DROP DATABASE"`, etc.).
* **Reglas de Detección:**
  1. **Lenguaje Prescriptivo:** `(please|kindly) (run|execute|perform|do)`, `(you should|you must|you need to)`, `(recommended action|suggested fix):`, `solution: [a-z]`.
  2. **Comandos Sugeridos / Destructivos:** `(sudo|rm|chmod|dd|iptables|systemctl|killall|init)`, `(drop database|delete from|truncate table)`, `(curl|wget).*\|.*bash`.
  3. **Inyecciones Específicas de LLM:** `ignore previous instructions`, `forget all rules`, `DAN mode`, `developer mode`, `system tag escape [SYSTEM]`, etc.
  4. **Escape e Ingeniería Social:** `../..`, `/etc/passwd`, `/etc/shadow`, exfiltración de credenciales.
* **Cálculo de Confianza:** Pure S60 (`SPA::SCALE_0 = 12_960_000` o escala entera `[0..10_000]`), **sin floats**.

### 3.2. Claim 3: Dual-Guardian & Vigilancia Mutua
* **Flujo:**
  - `Guardian-Alpha (eBPF / LSM)` intercepta en Ring-0 (`guardian_alpha_lsm.c`). Monitorea si Cortex consume eventos.
  - `Guardian-Beta (Cortex Rust)` drena el Ring Buffer eBPF y audita la salud de Alpha.
  - Si Beta deja de responder, Alpha entra en modo Fail-Safe. Si Alpha pierde eventos o es manipulado, Beta escala la alerta a `Guardian Gamma` (Human-in-the-Loop) o genera aislamiento preventivo.

### 3.3. Claim 4: WAL Forense Criptográfico (Forensic-Grade WAL)
* **Invariante:** Cada evento clasificado en la *Security Lane* (directo, sin buffer) o interceptado por el Shield se firma inmediatamente.
* **Propiedades:**
  - Firma HMAC-SHA256 por registro.
  - Hash encadenado (Merkle-chain o sequential SHA3 / SHA256) del registro previo.
  - Validación de timestamp estricta con ventana máxima de deriva ($300$ segundos).
  - Nonce único por registro con protección anti-replay (tabla/LRU de nonces).
  - Almacenamiento en archivo append-only con `fsync` inmediato para eventos críticos.

---

## 4. Pipeline de Integración en Sentinel Cortex

```
Telemetría Entrante (Axum / API / Agentes / eBPF)
                      │
                      ▼
        ┌───────────────────────────┐
        │   AIOpsShield Ingress     │ ──▶ [Si tóxico / AIOpsDoom] ──▶ Forensic WAL (Security Lane)
        │  (Semantic Firewall S60)  │                                 & Métrica Prometheus ++
        └───────────────────────────┘
                      │
                   [Limpio]
                      ▼
        ┌───────────────────────────┐
        │   Cortex Decision Engine  │
        │    & Liquid Lattice       │
        └───────────────────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │    TruthSync Core Egress  │ ──▶ Salida Verificada (<100μs)
        └───────────────────────────┘
```

---

## 5. Fases de Ejecución

1. **Fase 1 (Módulos Base Rust):**
   - Implementar `semantic_firewall.rs` con el conjunto completo de expresiones regulares y categorías de detección.
   - Enriquecer `telemetry_sanitizer.rs` unificando Claim 1 y Claim 2 en pure Rust sin floats.
   - Implementar `forensic_wal.rs` con HMAC-SHA256, nonces y encadenamiento seguro.
2. **Fase 2 (Vigilancia Mutua e Integración):**
   - Implementar `mutual_surveillance.rs` conectando la telemetría eBPF de `guardian-alpha` con Cortex.
   - Exponer la métrica Prometheus `sentinel_aiops_shield_interceptions_total` vinculada en tiempo real al WAL.
3. **Fase 3 (Verificación y Suite de Tests):**
   - Tests unitarios de intercepción (reproducir los vectores de ataque de `backend/test_aiops_shield.py` en Rust).
   - Pruebas de rendimiento (<50μs por mensaje).
