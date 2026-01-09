# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------


"""
🛸 YATRA FLIGHT BENCHMARK: EL GRAN AÑO (360° ORBIT)
===================================================
Prueba de estrés para el motor aritmético Yatra (Base-60).

El objetivo es navegar secuencialmente por las 4 Estrellas Reales:
1. Aldebarán -> Regulus (Salto 1)
2. Regulus -> Antares (Salto 2)
3. Antares -> Fomalhaut (Salto 3)
4. Fomalhaut -> Aldebarán (Cierre del Círculo)

Validación:
Al cerrar el círculo, la posición final DEBE ser idéntica a la inicial.
La Deriva Acumulada debe ser CERO ABSOLUTO.
"""

import time
import sys
# Importamos desde el núcleo protegido
from yatra_core import S60, UMR, STAR_ALDEBARAN, STAR_REGULUS, STAR_ANTARES, STAR_FOMALHAUT

def run_orbit_stress_test():
    print("🛸 YATRA BENCHMARK: ORBITAL STRESS TEST (360°)")
    print("==============================================")
    
    # Puntos de Ruta (Waypoints)
    route = [STAR_REGULUS, STAR_ANTARES, STAR_FOMALHAUT, STAR_ALDEBARAN]
    current_pos = STAR_ALDEBARAN
    
    print(f"🏁 INICIO: {current_pos} (Aldebarán)")
    
    start_time = time.perf_counter()
    drift_accumulated = S60(0,0,0,0)
    
    for i, target in enumerate(route):
        print(f"\n🚀 TRAMO {i+1}: Hacia {target}...")
        
        # 1. Calcular Delta (Vector de Fase)
        # Nota: Si cruzamos el 360 (Fomalhaut -> Aldebarán), la resta directa daría negativo.
        # Yatra Core debe manejar la ciclicidad o lo haremos manualmente aquí.
        # S60 aún no es cíclico nativo (no tiene módulo 360 automático en __sub__).
        # Calculamos la distancia angular positiva.
        
        # Convertimos a escalar para comparar magnitud (solo para lógica de control)
        # Esto es seguro porque usamos enteros internos, no floats.
        curr_mags = current_pos._value
        targ_mags = target._value
        
        # Heurística simple: Si el target es menor que el origen, sumamos 360 al target
        if targ_mags[0] < curr_mags[0]:
            # Caso Fomalhaut (344) -> Aldebarán (68)
            # Objetivo virtual = 360 + 68 = 428
            virtual_target = target + S60(360, 0, 0, 0)
            delta = virtual_target - current_pos
        else:
            delta = target - current_pos
            
        print(f"   📐 Delta: {delta}")
        
        # 2. Navegación (Simulada en 1 paso maestro para bench de precisión)
        # En una simulación real haríamos N pasos. Aquí validamos la aritmética final.
        current_pos = current_pos + delta
        
        # Normalizar si nos pasamos de 360 (El universo es un círculo)
        if current_pos._value // S60.SCALE_0 >= 360:
            current_pos = current_pos - S60(360, 0, 0, 0)
            
        print(f"   📍 LLEGADA: {current_pos}")
        
        # Validar Alineación
        if str(current_pos) != str(target):
             print(f"   ❌ ERROR CRÍTICO: Disonancia en tramo {i+1}")
             return
        else:
             print(f"   ✅ TRAMO {i+1} LOCKED (Residuo Cero)")

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    
    print("\n" + "="*50)
    print("📊 RESULTADOS DEL BENCHMARK:")
    print(f"   Tiempo de Cómputo: {duration_ms:.4f} ms")
    
    # Validación Final: Cierre de Órbita
    # Empezamos en Aldebarán. Terminamos en Aldebarán.
    # Si current_pos == STAR_ALDEBARAN, el círculo es perfecto.
    
    print(f"   Posición Final:   {current_pos}")
    print(f"   Posición Inicial: {STAR_ALDEBARAN}")
    
    if str(current_pos) == str(STAR_ALDEBARAN):
        print(f"\n🏆 INTEGRIDAD ORBITAL: 100% (PERFECT LOOP)")
        print(f"   La matemática Yatra ha sostenido la coherencia tras una vuelta galáctica completa.")
        print(f"   Residuos Decimales: 0.0")
    else:
        print(f"\n❌ FALLO ORBITAL: El sistema ha derivado.")

def friccion_logica_test():
    """
    PRUEBA DE FRICCIÓN LÓGICA: DECIMAL VS YATRA
    Demostración de por qué los decimales causan 'muerte térmica' del código.
    Usamos ACUMULACIÓN porque revela la pérdida de precisión de forma mas honesta.
    """
    print("\n\n🔥 PRUEBA DE FRICCIÓN LÓGICA (DECIMAL VS YATRA)")
    print("===============================================")
    print("Objetivo: Acumular 1/3 (un tercio) repetidamente para formar enteros.")
    print("Meta: Sumar 1/3 tres veces = 1. Repetir 3600 veces. Resultado esperado: 3600.0")
    
    ciclos = 3600
    
    # --- SIMULACIÓN DECIMAL (SISTEMA DISONANTE) ---
    val_decimal = 0.0
    tercio_decimal = 1.0 / 3.0 # 0.333333... (Pérdida inmediata de info)
    
    start_dec = time.perf_counter()
    for _ in range(ciclos * 3): # 3 tercios por ciclo
        val_decimal += tercio_decimal
    end_dec = time.perf_counter()
    
    esperado = float(ciclos)
    error_decimal = abs(esperado - val_decimal)
    
    # --- SIMULACIÓN YATRA (SISTEMA RESONANTE) ---
    val_yatra = S60(0, 0, 0, 0)
    # 1/3 de grado = 20 minutos EXACTOS
    tercio_yatra = S60(0, 20, 0, 0) 
    
    start_yatra = time.perf_counter()
    for _ in range(ciclos * 3):
        val_yatra = val_yatra + tercio_yatra
    end_yatra = time.perf_counter()
    
    # Resultado esperado: 3600 grados
    # S60 se normaliza, asi que 3600 grados es normal.
    esperado_yatra = S60(ciclos, 0, 0, 0)
    
    # Verificación
    es_perfecto = (str(val_yatra) == str(esperado_yatra))
    
    print(f"\n1. 📉 RESULTADO DECIMAL (Base-10):")
    print(f"   Valor Esperado: {esperado}")
    print(f"   Valor Final:    {val_decimal:.20f}")
    print(f"   Error (Calor):  {error_decimal:.20f}")
    print(f"   Estado: {'❌ DISONANTE' if error_decimal > 0.0 else '✅ PERFECTO'}")
    
    print(f"\n2. 🔱 RESULTADO YATRA (Base-60):")
    print(f"   Valor Esperado: {esperado_yatra}")
    print(f"   Valor Final:    {val_yatra}")
    print(f"   Error:          {0 if es_perfecto else 'CRITICAL FAILURE'}")
    print(f"   Estado: {'✅ ETERNO' if es_perfecto else '❌ ROTO'}")
    
    print(f"\n💡 CONCLUSIÓN: La matemática decimal ha generado entropía (ruido).")
    print(f"   El sistema Yatra ha cerrado el ciclo con precisión de diamante.")

if __name__ == "__main__":
    try:
        run_orbit_stress_test()
        friccion_logica_test()
    except Exception as e:
        print(f"FATAL: {e}")