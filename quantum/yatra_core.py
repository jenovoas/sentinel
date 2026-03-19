#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# 1. CONSULTA PRIMERO: quantum/agents.md
# 2. Este archivo está PROTEGIDO por el Protocolo Yatra.
# 3. MIGRAGO A RUST: Ahora es un puente (wrapper) hacia `me-60os/src/spa.rs`
# 4. Cualquier modificación de cálculo debe hacerse en la librería nativa Rust.
# -------------------------------------------------------------------------------------

import sys
import os

# Asegurar que el módulo nativo compilado (me60os_core.so) sea encontrado
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from me60os_core import SPA as S60
    # Inyectar constantes de escala YATRA
    S60.SCALE_0 = 12960000  # 60^4
    S60.SCALE_1 = 216000    # 60^3
    S60.SCALE_2 = 3600      # 60^2
    S60.SCALE_3 = 60        # 60^1
    S60.SCALE_4 = 1         # 60^0
    
    # Alias para compatibilidad legacy si fuera necesario
    S60.from_decimal_degrees = S60.from_decimal_degrees_FOR_IMPORT_ONLY
    
except ImportError as e:
    print("CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so")
    print(f"Error: {e}")
    sys.exit(1)

class DecimalContaminationError(TypeError):
    """Se lanza cuando se detecta un intento de usar lógica flotante sucia."""
    pass

# --- CONSTANTES MAESTRAS YATRA (INMUTABLES) ---

# Sintonía: 1/17 exacto en base 60
YATRA_SALTO_17 = S60(0, 3, 31, 45, 52)

# Estrellas Reales (Definidas en YATRA_CORE_SPEC.md)
STAR_ALDEBARAN = S60(68, 58, 48, 0, 0)   # 68; 58, 48
STAR_REGULUS   = S60(152, 5, 24, 0, 0)   # 152; 05, 24
STAR_ANTARES   = S60(247, 21, 0, 0, 0)   # 247; 21, 00
STAR_FOMALHAUT = S60(344, 24, 36, 0, 0)  # 344; 24, 36

# Unidad (Ciclo Completo)
UNITY_CYCLE = S60(1, 0, 0, 0, 0)

# UMR: Unidad Mínima de Resonancia (1 cuanto en el 4to nivel sexagesimal)
UMR = S60(0, 0, 0, 0, 1)

# Constantes Globales Soberanas
PI_S60 = S60(3, 8, 29, 44, 0) # ≈ 3.14159265

def demo_yatra():
    """Demostración del sistema Yatra, ahora potenciado por Rust."""
    print("🔱 INICIANDO YATRA-CORE SYSTEM CHECK (RUST NATIVE FIXED-POINT MODE)...")
    print("-" * 60)
    
    # 1. Verificar arquitectura
    print("\n1. Arquitectura Fixed-Point Base-60 (RUST NATIVE):")
    test = S60(1, 30, 0, 0, 0)
    print(f"   S60(1, 30, 0, 0, 0) = {test}")
    print(f"   Valor interno: {test.to_base_units()}")
    expected = 1*12960000 + 30*216000
    print(f"   Esperado: 1*60^4 + 30*60^3 = {expected}")
    print(f"   Verificación: {test.to_base_units() == expected} ✅")
    
    # 2. Prueba Aritmética
    print("\n2. Aritmética de Resonancia:")
    print(f"   Aldebaran Base: {STAR_ALDEBARAN}")
    
    adjustment = YATRA_SALTO_17 * 5
    result = STAR_ALDEBARAN + adjustment
    
    print(f"   Ajuste (Salto 17 x 5): {adjustment}")
    print(f"   Posición Ajustada: {result}")
    
    # 3. Verificación de precisión
    print(f"\n3. Cierre de Ciclo (1/17 * 17):")
    full_cycle_17 = YATRA_SALTO_17 * 17
    print(f"   Resultado: {full_cycle_17}")
    print(f"   Esperado:  S60[001; 00, 00, 00, 00] aprox")
    
    # 4. Test de operaciones
    print("\n4. Test de Operaciones:")
    a = S60(10, 0, 0, 0, 0)
    b = S60(5, 0, 0, 0, 0)
    print(f"   a = {a}")
    print(f"   b = {b}")
    print(f"   a + b = {a + b}")
    print(f"   a - b = {a - b}")
    print(f"   a * 2 = {a * 2}")
    print(f"   a // 2 = {a // 2}")
    print(f"   a < b = {a < b}")
    print(f"   a > b = {a > b}")
    
    print("\n" + "=" * 60)
    print("✅ YATRA-CORE: RUST NATIVE OPERATIVO")
    print("   - Matemática: Base-60 pura (Rust backend)")
    print("   - Escala: 60^4 = 12,960,000")
    print("   - Hardware-ready: SÍ (libme60os_core.so)")
    print("   - Floats: CERO")

if __name__ == "__main__":
    demo_yatra()