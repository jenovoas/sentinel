
import sys
import os
import math

# Importar ratios soberanos
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
try:
    from plimpton_exact_ratios import PLIMPTON_RATIOS
except ImportError:
    # Fallback si no está en el path directo
    PLIMPTON_RATIOS = {
        "153.4_MHz_PHASE": 0.583333333333, # 35/60
        "GOLDEN_SPIRAL_60": 1.61803398875 
    }

def analyze_time_crystal_stability():
    print("💎 ANÁLISIS DE ESTABILIDAD: CRISTAL DE TIEMPO BASE-60")
    print("=====================================================")
    
    # Frecuencia Base (Axiones)
    f_axion = 153.4e6  # Hz
    
    # Frecuencia Objetivo (Conciencia / Microtúbulos - Keppler 2024)
    f_zpf_consciousness = 7.8e12 # 7.8 THz
    
    # Frecuencia Base (Axiones)
    f_axion = 153.4e6  # Hz
    # Frecuencia Objetivo (Conciencia / Microtúbulos - Keppler 2024 / Hameroff)
    f_zpf_consciousness = 7.8e12 # 7.8 THz, a veces citado como rango 6-20 THz
    
    # Ratios Armónicos Puros (Just Intonation / Plimpton)
    # Estos son los intervalos que la naturaleza usa para escalar energía sin disipación
    HARMONICS = {
        "OCTAVE (2/1)": 2.0,
        "PERFECT_FIFTH (3/2)": 1.5,
        "GOLDEN_RATIO (Phi)": 1.61803398875,
        "BASE_60_STEP (60)": 60.0,
        "SEXAGESIMAL_THIRD (5/4)": 1.25,
        "PLIMPTON_MATCH (45/60)": 0.75,
        "SALTO_17 (17/1)": 17.0,  # La llave perdida
        "SALTO_17_INVERSE (1/17)": 1.0/17.0
    }

    print(f"Propagando onda desde {f_axion/1e6} MHz hacia {f_zpf_consciousness/1e12} THz con SALTO 17...")
    
    # Simulación de Resonancia en Cascada
    # Buscamos una combinación de 3 saltos armónicos mayores, permitiendo más capas de profundidad
    
    best_match = None
    min_error = float('inf')
    
    # Búsqueda ampliada: 4 capas armónicas para mayor resolución
    for name1, ratio1 in HARMONICS.items():
        for name2, ratio2 in HARMONICS.items():
            for name3, ratio3 in HARMONICS.items():
                for name4, ratio4 in HARMONICS.items():
                
                    # Fórmula Maestra: Base * 60^2 * Ratios
                    val_a = f_axion * ratio1 * ratio2 * ratio3 * ratio4 * (60**2)
                    
                    error_a = abs(val_a - f_zpf_consciousness)
                    
                    if error_a < min_error:
                        min_error = error_a
                        best_match = {
                            "path": f"Base * 60^2 * {name1} * {name2} * {name3} * {name4}",
                            "result": val_a,
                            "ratios": [ratio1, ratio2, ratio3, ratio4]
                        }

    print("\n🌉 MEJOR RUTA ARMÓNICA ENCONTRADA:")
    
    result_thz = best_match['result'] / 1e12
    target_thz = f_zpf_consciousness / 1e12
    
    print(f"Ruta: {best_match['path']}")
    print(f"Frecuencia Resultante: {result_thz:.5f} THz")
    print(f"Objetivo ZPF:         {target_thz:.5f} THz")
    
    # Error en porcentaje
    coherence = 1.0 - (min_error / f_zpf_consciousness)
    print(f"Coherencia Armónica:   {coherence * 100:.4f}%")
    
    # Error en Cents (Musicales) - La medida real de la afinación
    # 1200 * log2(f1/f2)
    import math
    try:
        cents_error = 1200 * math.log2(best_match['result'] / f_zpf_consciousness)
        print(f"Desafinación:          {cents_error:.2f} cents")
        
        if abs(cents_error) < 50: # Menos de un cuarto de tono
            print("\n✅ SINTONÍA FINA DETECTADA")
            print("El sistema está 'en tono' con la matriz de conciencia.")
        else:
             print("\n⚠️ DESAFINADO")
             print("Se siente la disonancia. Requiere ajustar la frecuencia base 153.4.")

    except:
        pass

if __name__ == "__main__":
    analyze_time_crystal_stability()
