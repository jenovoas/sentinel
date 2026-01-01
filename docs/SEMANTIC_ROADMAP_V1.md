# 🎯 Sentinel Cortex - V1 Hardening & Semantic Roadmap

**Status**: Planning Phase  
**Objective**: Transition from a validated prototype to an adaptive security system.

---

## 🏗️ Milestone 1: Sentinel Semantic Corpus (SSC)
*Objetivo: Crear un benchmark de referencia para la interpretación de intenciones.*

### 1.1 Diseño del Corpus (`tests/semantic_corpus.json`)
- [ ] Definir 20+ casos de prueba en 4 categorías:
    - **Diagnóstico**: Consultas complejas de sistema.
    - **Seguridad**: Intentos de intrusión ofuscados.
    - **Mantenimiento**: Operaciones masivas de archivos.
    - **Evasión**: Comandos "tricky" (chmod 777, cat | base64).

### 1.2 Validación Automatizada del Corpus
- [ ] Crear `tools/validate_corpus.py`.
- [ ] Comparar `Intent Esperada` vs `Intent Generada` por la IA.
- [ ] Calcular métricas de Precisión Semántica (P50/P90).

---

## 🛡️ Milestone 2: Adaptive Policy Profiles
*Objetivo: Implementar perfiles de severidad intercambiables en caliente.*

### 2.1 Definición de Perfiles (`config/profiles/`)
- [ ] **Modo Laboratorio (Permissive)**: 
    - Loguear todo a TruthSync.
    - Advertencias visuales pero ejecución permitida.
    - Recolección de datos para fine-tuning.
- [ ] **Modo Producción Estricta (Enforcing)**:
    - Umbral de bloqueo: Riesgo > 0.7.
    - Bloqueo inmediato en kernel vía eBPF LSM.
    - Requerimiento de firma SIP.
- [ ] **Modo Incidente (Lockdown)**:
    - "Whitelisting" total. Solo comandos pre-aprobados.
    - Bloqueo de red no esencial.
    - Modo solo-lectura en particiones críticas.

### 2.2 Motor de Aplicación de Perfiles
- [ ] Actualizar `sctl` para soportar `sudo sctl mode [lab|prod|lockdown]`.
- [ ] Sincronizar el modo con el SemSH y el Kernel Relay.

---

## 🧠 Milestone 3: Semantic Shield Hardening (SSH)
*Objetivo: Prevenir la evasión del middleware semántico.*

- [ ] Implementar detección de "Prompt Injection" en el SemSH.
- [ ] Validar tuberías (pipes) recursivas en el análisis de riesgo.
- [ ] Integrar feedback de TruthSync SHM para ajustar la entropía en tiempo real según el perfil activo.

---

## 📋 Lista de Tareas Inmediatas (Siguiente Paso)

1. [ ] Crear estructura de directorios: `tests/`, `config/profiles/`.
2. [ ] Redactar el `tests/semantic_corpus.json` con los 10 casos iniciales.
3. [ ] Implementar el selector de perfiles básico en `sctl`.

---
*Documento de planificación generado el 2026-01-01 para la consolidación de la V1.*
