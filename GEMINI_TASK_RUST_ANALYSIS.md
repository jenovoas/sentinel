# TAREA: Análisis Quirúrgico del Código Rust en Sentinel v7.0/v8.0

## Contexto
Sentinel es un servidor de **infraestructura crítica** para producción. Solo migraremos lo que esté **completamente optimizado en Rust**. El proyecto corre en `~/Dev/sentinel` en el servidor **fenix** (34.176.84.47).

## Objetivo
Identificar qué componentes Rust están listos para producción y cuáles necesitan más trabajo.

---

## ESTRUCTURA A ANALIZAR

El proyecto Sentinel tiene las siguientes áreas con código Rust:

1. **`src/`** - Código principal Rust
2. **`sentinel-cortex/`** - Core cuántico Rust
3. **`ebpf/`** - Módulos eBPF en Rust
4. **`quantum/`** - Capa Python que integra con Rust

## CRITERIOS DE EVALUACIÓN PARA CADA MÓDULO RUST

Para cada archivo o módulo Rust encontrado, evalúa:

### A. OPTIMIZACIÓN Y RENDIMIENTO
- ¿Usa tipos de datos óptimos (no `String` innecesario, usa `&str`)?
- ¿Evita clonaciones y asignaciones innecesarias?
- ¿Usa `Cow`, `Rc`/`Arc`, `Box` donde corresponde?
- ¿Aprovecha el ownership system de Rust correctamente?
- ¿No hay panic! en código de producción (usa `Result`/`Option`)?
- ¿Memoria pre-asignada donde es crítico (Vec::with_capacity)?

### B. SEGURIDAD Y ROBUSTEZ
- ¿Manejo de errores completo (no `unwrap()`/`expect()` sin contexto)?
- ¿Validación de entrada en todos los boundary points?
- ¿No hay `unsafe` innecesario?
- ¿Uso de crates seguros y bien mantenidos?
- ¿No hay data races en código concurrente (usando Mutex/RwLock/atomic correctamente)?
- ¿Buffer overflow protections implementados?

### C. ARQUITECTURA Y MANTENIBILIDAD
- ¿Módulos bien separados (responsabilidad única)?
- ¿Testing coverage suficiente (unit tests, integration tests)?
- ¿Documentación de API con `///` comments?
- ¿Configuración externalizada (no hardcoded values)?
- ¿Logging estructurado implementado (tracing/log crate)?
- ¿Code review ready (formatting con rustfmt, clippy clean)?

### D. INTEGRACIÓN DE SISTEMA
- ¿Compatible con eBPF (si aplica)?
- ¿Integración correcta con Python (si aplica)?
- ¿No rompe con la arquitectura Base-60 (S60 math)?
- ¿Resource limits definidos (CPU, memoria, threads)?
- ¿Graceful shutdown implementado?
- ¿Health check endpoint disponible?

### E. PRODUCCIÓN READINESS
- ¿Performance benchmarks ejecutados?
- ¿Memory leaks testeados?
- ¿Error rates aceptables?
- ¿Backward compatible con interfaces existentes?
- **¿TOTALMENTE OPTIMIZADO Y PRODUCTION READY?** (CRÍTICO)

---

## OUTPUT ESPERADO

### 1. INVENTARIO COMPLETO DE MÓDULOS RUST
Lista TODOS los archivos `.rs` encontrados en el proyecto con:
- Ruta completa
- Líneas de código
- Propósito (según comentarios/contexto)

### 2. MATRIZ DE EVALUACIÓN
Para cada módulo, crear una tabla con puntajes por categoría.

### 3. CLASIFICACIÓN FINAL

Crear tres categorías:

#### 🟢 LISTO PARA MIGRAR A PRODUCCIÓN
Módulos que cumplen TODOS los criterios

#### 🟡 REQUIERE AJUSTES MENORES
Módulos que necesitan pequeñas correcciones

#### 🔴 NO LISTO - REQUIERE TRABAJO
Módulos que necesitan refactorización importante

### 4. RECOMENDACIÓN DE ORDEN DE MIGRACIÓN
Basado en dependencias y complejidad.

### 5. ANÁLISIS DE DEPENDENCIAS
Mapa de dependencias entre módulos Rust.

---

## FORMATO DE RESPUESTA

```markdown
# 📊 ANÁLISIS QUIRÚRGICO DE CÓDIGO RUST - SENTINEL

## 📋 INVENTARIO DE MÓDULOS RUST

[Lista de todos los módulos encontrados con metadatos]

## 🟢 LISTO PARA PRODUCCIÓN

[Tabla para cada módulo listo]

## 🟡 REQUIERE AJUSTES MENORES

[Tabla para cada módulo con ajustes]

## 🔴 NO LISTO - REQUIERE TRABAJO

[Tabla para cada módulo que necesita trabajo]

## 📝 RECOMENDACIÓN DE ORDEN DE MIGRACIÓN

1. [Primer módulo]
2. [Segundo módulo]
...

## 🔗 MAPA DE DEPENDENCIAS

[Diagrama de dependencias]

## 📊 RESUMEN EJECUTIVO

- Total módulos Rust: X
- Listos para producción: Y (Z%)
- Requieren ajustes menores: A (B%)
- No listos: C (D%)

## ⚠️ OBSERVACIONES CRÍTICAS

[Listar problemas de seguridad, bugs, o riesgos]
```

---

## REGLAS ESPECIALES

1. NO ASUMIR NADA: Si no entiendes un módulo, investiga más.
2. SER HONESTO: Si un módulo no está listo, dilo claramente.
3. CONTEXTUALIZAR: Explica por qué un problema es crítico en producción.
4. NO CAMBIAR CÓDIGO: Solo leer y analizar.
5. FOCÓCATE EN OPTIMIZACIÓN RUST: Identificar código Rust optimizado para producción.
