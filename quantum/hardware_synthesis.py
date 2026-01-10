#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# S60 HARDWARE SIMULATOR v2 (DSP MODEL)
# Simula pipeline de multiplicación hardware con acumulador 128-bit.
# -------------------------------------------------------------------------------------

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quantum.yatra_core import S60

class DSPConstraintError(Exception):
    pass

class S60DSP:
    """
    Simula un bloque DSP FPGA para S60.
    Inputs: Int64
    Accumulator: Int128
    Output: Int64
    """
    MAX_INT64 = 2**63 - 1
    MIN_INT64 = -2**63
    MAX_INT128 = 2**127 - 1
    MIN_INT128 = -2**127
    
    # 12960000 hardcoded to avoid class attr ambiguity
    SCALE = 12960000

    @staticmethod
    def _check_128(val):
        """Verifica si el valor intermedio cabe en el acumulador DSP (128-bit)."""
        if val > S60DSP.MAX_INT128 or val < S60DSP.MIN_INT128:
            raise DSPConstraintError(f"🔥 DSP ACCUMULATOR MELTDOWN: {val} excede 128-bit")

    @staticmethod
    def _check_64(val, stage="Output"):
        """Verifica si el resultado final cabe en el registro de destino (64-bit)."""
        if val > S60DSP.MAX_INT64 or val < S60DSP.MIN_INT64:
            raise DSPConstraintError(f"🌊 REGISTER OVERFLOW ({stage}): {val} excede 64-bit")

    @staticmethod
    def mul_pipeline(a: S60, b: S60) -> S60:
        """
        Simula operación A * B en hardware S60.
        Paso 1: Multiplicación Raw (64 * 64 -> 128 bit)
        Paso 2: Scaling (División por constante hardware)
        Paso 3: Writeback (Check 64 bit)
        """
        raw_a = a._value
        raw_b = b._value
        
        # Paso 1: Acumulación de alta precisión
        intermediate = raw_a * raw_b
        S60DSP._check_128(intermediate)
        
        # Paso 2: Barrel Shifter / Divisor Algebraico
        # S60 usa division floor, en hardware sería shift+sub o dedicated divider
        res_raw = intermediate // S60DSP.SCALE
        
        # Paso 3: Writeback a registro
        S60DSP._check_64(res_raw, "Writeback")
        
        return S60._from_raw(res_raw)

    @staticmethod
    def mul_wide_pipeline(a: S60, b: S60) -> S60:
        """Pipeline para Deep Space (Output a registro 128-bit simulado)"""
        raw_a = a._value
        raw_b = b._value
        intermediate = raw_a * raw_b
        S60DSP._check_128(intermediate)
        res_raw = intermediate // S60DSP.SCALE
        # No check 64, permitimos 128 bits de salida
        S60DSP._check_128(res_raw) 
        return S60._from_raw(res_raw)

class SynthesisBench:
    def run(self):
        print("⚡ INICIANDO TESTBENCH DSP S60 (128-BIT ACCUMULATOR)...")
        dsp = S60DSP()
        
        # 1. Caso Trivial (1 * 1)
        r1 = dsp.mul_pipeline(S60(1), S60(1))
        print(f"   ✅ [DSP] 1 * 1 = {r1}")
        
        # 2. Caso Nominal (Navegación LEO: 7000km * 7km/s)
        # r = 7,000,000 m
        # v = 7,000 m/s
        # r*v = 49,000,000,000 (4.9e10)
        # Raw = 4.9e10 * 1.29e7 = 6.3e17 -> Cabe en Int64 (9e18)
        # Intermediate = (7e6 * 1.29e7) * (7e3 * 1.29e7) = 8e27 -> Cabe en 128 (1.7e38)
        r = S60(7000000)
        v = S60(7000)
        ang_momentum = dsp.mul_pipeline(r, v)
        print(f"   ✅ [DSP] LEO Momentum (r*v) OK: {ang_momentum}")
        
        # 3. Caso Límite Int64
        # Multiplicación que da resultado > MAX_INT64
        # MAX_INT64_S60 = 9e18 / 1.29e7 = 7e11 (700 Billones)
        # Probemos 1 Billón * 1 Billón = 1e18 (Debe fallar en 64-bit output)
        big = S60(1000000000000) # 1e12
        print(f"   [DSP] Probando Overflow Output (1T * 1T)...")
        try:
            dsp.mul_pipeline(big, big)
            print("   ❌ FALLO: No detectó overflow de registro")
        except DSPConstraintError as e:
            print(f"   ✅ ÉXITO: Trap de registro 64-bit activo -> {e}")
            
        # 4. Caso Deep Space (Wide Output)
        print(f"   [DSP] Probando Wide Pipeline (1T * 1T)...")
        res_wide = dsp.mul_wide_pipeline(big, big)
        print(f"   ✅ ÉXITO: Wide Pipeline soportó carga masiva: {res_wide}")
        
if __name__ == "__main__":
    SynthesisBench().run()
