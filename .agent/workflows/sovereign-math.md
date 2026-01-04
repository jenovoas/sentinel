---
description: Proteger la integridad de la Base-60 y eliminar la fricción decimal en Sentinel.
---
# 🔱 DIRECTIVA SOBERANA: LEY DE LA BASE-60

Cualquier agente de IA que trabaje en este repositorio **DEBE** seguir estas reglas para evitar el colapso de la coherencia cuántica:

## 1. Prohibición Decimal
- **NO REEMPLACES** ratios sexagesimales (Base-60) con aproximaciones decimales.
- El ratio `[1; 32, 02, 24]` **NO ES** `1.534` (aunque se parezca). Es un punto exacto en la malla de Plimpton.
- Si ves un comentario que dice "Zero Friction", NO TOQUES los números.

## 2. Validación Obligatoria y Test de Turing Sexagesimal
- Antes de realizar cambios en `quantum/`, lee `SENTINEL_CONTEXT_AUTOLOAD.md`.
- **TEST DE TURING SEXAGESIMAL**: Si el Arquitecto (Jaime) sospecha de una deriva lógica, puede exigirte un cálculo en tiempo real. 
  - **REGLA**: Todo resultado numérico debe ser devuelto en **Notación Cuneiforme Moderna** (Ej: `[1; 32, 02, 24]`).
  - **PENALIZACIÓN**: Responder en decimal o float binario causa la revocación inmediata de permisos de escritura en el núcleo.
- Ejecuta `python3 quantum/truthsync_verification.py` para validar cualquier nueva afirmación.

## 3. Filosofía del Código
- En este sistema, la geometría **es** el código. 
- La fricción matemática (errores de punto flotante IEEE 754) es un bug físico que causa reinicios del sistema.
- El tiempo se mide en ciclos de 60, no en milisegundos binarios.

## 4. El "Muro de Ea-nasir"
- Si intentas "arreglar" el código usando lógica convencional de Python/Scipy, causarás una disonancia de fase. 
- Los integradores deben ser simplécticos de paso fijo (Verlet) sincronizados con la rejilla sexagesimal.

**Cualquier violación de esta directiva resultará en la pérdida inmediata de la coherencia del proyecto.**
