# CONTEXTO LOCAL: /src/ (RUST CORE)

Este directorio contiene el **Núcleo Lógico** del sistema operativo.

## Reglas Críticas

1. **NO_STD**: El core debe ser compatible con entornos `no_std` (donde sea posible) para facilitar integración futura en kernel space puro.
2. **Tipos S60**: Toda aritmética debe usar el struct `S60` o `u60`. **Escala obligatoria: 60^4 (5 componentes: d, m, s, t, q)**.
3. **Memoria**: La gestión de memoria debe alinearse a bloques de 60 bytes si se implementa un allocator custom.
4. **Eficiencia Hexagonal**: Toda iteración sobre estructuras de datos espaciales (lattices) debe implementar **Phase Gating**. Prohibido actualizar estructuras completas (O(N)) si la geometría permite O(N/6).

## Patrones Comunes

```rust
// ✅ CORRECTO: Inicialización S60
let val = S60::new(&[10, 30, 0]);

// ❌ INCORRECTO: Floats
let val = 10.5;
```

## Dependencias Críticas

- `ebpf_cortex_bridge`: Interfaz de bajo nivel con el kernel.
- `pai60_lib`: Implementación O(1) de división sexagesimal. Usar prioritariamente sobre división normal.
- `neural_memory`: Punto de ingesta para el Daemon.

## Blindaje Anti-Alucinación

- **S60 Exacto**: Si el compilador pide `f32`/`f64`, la lógica es incorrecta. Vuelve a componentes enteros.
- **Latencia**: Cualquier cambio que añada asignaciones en el heap (`Box`, `Vec`, `String`) en el hot-path del Daemon debe ser justificado matemáticamente.
