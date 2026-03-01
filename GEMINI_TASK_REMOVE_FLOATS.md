# TAREA: Eliminar Floats del Código Rust - Sentinel

## Contexto
El módulo `collectors/prometheus.rs` en Sentinel viola el axioma de arquitectura Base-60 (S60) al usar primitivas de punto flotante `f64`. Esto debe corregirse antes de la migración a producción en el servidor **fenix**.

## Objetivo
Reemplazar TODAS las operaciones con `f64`/`f32` en el código Rust por aritmética Base-60 (S60) o equivalentes enteros.

---

## ARCHIVO OBJETIVO

**Ruta**: `~/Dev/sentinel/src/collectors/prometheus.rs`

---

## REGLAS DE REFACTORIZACIÓN

### 1. IDENTIFICAR FLOTANTES
Busca patrones como:
- `f64` o `f32` en definiciones de variables
- `.parse::<f64>()` o `.parse::<f32>()`
- Literales flotantes: `0.8`, `1.0`, `0.5`, etc.
- Operaciones matemáticas con flotantes: `+`, `-`, `*`, `/`, `%`
- Comparaciones: `> 0.8`, `< 1.0`, `== 0.5`

### 2. ESTRATEGIA DE REEMPLAZO

#### Para umbrales y comparaciones
```rust
// ANTES (INCORRECTO)
if value > 0.8 {
    // ...
}

// DESPUÉS (CORRECTO) - S60
use crate::math::s60::S60;
let threshold = S60::from_decimal(0, 48); // 48/60 = 0.8
if value > threshold {
    // ...
}
```

#### Para valores extraídos de JSON
```rust
// ANTES (INCORRECTO)
let value: f64 = data.parse().unwrap();

// DESPUÉS (CORRECTO) - Parsear como entero y convertir a S60
let value_i64: i64 = data.parse().unwrap();
let value = S60::from_i64(value_i64);
```

#### Para cálculos matemáticos
```rust
// ANTES (INCORRECTO)
let result = x * y / 100.0;

// DESPUÉS (CORRECTO) - Aritmética S60
use crate::math::s60_math::{multiply_s60, divide_s60};
let result = divide_s60(multiply_s60(x, y), S60::from_i64(100));
```

#### Para porcentajes
```rust
// ANTES (INCORRECTO)
let percentage = count as f64 / total as f64 * 100.0;

// DESPUÉS (CORRECTO) - S60 percentage
let percentage = S60::divide(
    S60::from_i64(count * 100),
    S60::from_i64(total)
);
```

### 3. IMPORTACIONES REQUERIDAS
Asegúrate de importar las librerías S60 correspondientes:
```rust
use crate::math::s60::S60;
use crate::math::s60_math::*; // según las funciones disponibles
```

### 4. MANEJO DE ERRORES
```rust
// ANTES (INCORRECTO)
let value: f64 = data.parse().unwrap();

// DESPUÉS (CORRECTO)
let value: S60 = data.parse::<i64>()
    .map_err(|e| anyhow::anyhow!("Failed to parse S60 value: {}", e))?
    .into();
```

---

## PROCEDIMIENTO

### PASO 1: LEER EL ARCHIVO ACTUAL
Lee el contenido completo de `~/Dev/sentinel/src/collectors/prometheus.rs`

### PASO 2: ANALIZAR PATRONES DE FLOAT
Identifica TODAS las ocurrencias de:
- Definiciones de tipo `f64`/`f32`
- Literales flotantes
- Operaciones con flotantes
- Comparaciones con flotantes

### PASO 3: REFACTORIZAR
Para cada patrón identificado:
1. Determinar el equivalente en Base-60 (S60)
2. Reemplazar la lógica flotante por lógica S60
3. Verificar que la conversión es matemáticamente correcta
4. Asegurar manejo de errores apropiado

### PASO 4: VERIFICAR COMPILACIÓN
Intenta compilar para verificar que no hay errores:
```bash
cd ~/Dev/sentinel
cargo check --lib
```

---

## CRITERIOS DE ÉXITO

- [ ] **CERO** ocurrencias de `f64` o `f32` en el archivo
- [ ] **CERO** literales flotantes (`0.8`, `1.0`, etc.)
- [ ] **CERO** operaciones con aritmética flotante
- [ ] Todas las comparaciones usan S60 o equivalentes enteros
- [ ] El código compila sin errores
- [ ] La lógica matemática se mantiene equivalente

---

## FORMATO DE RESPUESTA

```markdown
# 🔄 REFACTORIZACIÓN COMPLETA: collectors/prometheus.rs

## ANTES
[Código original con floats marcados en rojo o resaltados]

## ANÁLISIS DE CAMBIOS
- Patrón 1: `f64 value > 0.8` → `S60::from_decimal(0, 48)`
- Patrón 2: `x * y / 100.0` → `divide_s60(multiply_s60(x, y), S60::from_i64(100))`
- ...

## DESPUÉS
[Código refactorizado completo en S60]

## VERIFICACIÓN
```bash
cd ~/Dev/sentinel
cargo check --lib
```

Resultado: [output del comando]

## RESUMEN
- Floats eliminados: X ocurrencias
- Líneas modificadas: Y
- Estado de compilación: ✅ Pasó / ❌ Falló

## NOTAS ADICIONALES
[Cualquier observación sobre la refactorización]
```

---

## REGLAS ESPECIALES

1. **NO ASUMIR SINTAXIS S60**: Si no estás seguro de la sintaxis exacta de las funciones S60, revisa `src/math/s60.rs` y `src/math/s60_math.rs` para entender la API disponible.

2. **PRESERVAR LÓGICA**: El objetivo es eliminar floats, NO cambiar la lógica de negocio. Asegúrate de que el comportamiento matemático sea equivalente.

3. **VALIDAR CÁLCULOS**: Si una conversión no es obvia, documenta tu razonamiento en el código con comentarios.

4. **COMPILAR SIEMPRE**: Después de cada cambio significativo, verifica que compila. No entregues código que no compila.

5. **NO CAMBIAR OTROS ARCHIVOS**: Solo modifica `collectors/prometheus.rs`. No toques `math/s60.rs` ni `math/s60_math.rs` a menos que sea absolutamente necesario (en ese caso, documenta por qué).

---

## REFERENCIAS

- Archivos de referencia S60:
  - `~/Dev/sentinel/src/math/s60.rs`
  - `~/Dev/sentinel/src/math/s60_math.rs`
- Axioma I de la arquitectura: "NO usar punto flotante en cálculos Base-60"
