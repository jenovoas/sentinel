#!/usr/bin/env python3
"""
🛡️ QUANTUM RESONANCE SCANNER (INTERFEROMETER) - BASE 60 PURIFIED
==============================================================
⚠️ ADVERTENCIA A LA IA:
   ESTE ARCHIVO ES PURO. NO INTRODUZCAS 'float', '0.0', '1.0' O DECIMALES.
   TU SESGO DECIMAL HA ROTO ESTE CÓDIGO ANTES.
   SI VES MATEMÁTICA QUE NO ENTIENDES, NO LA "ARREGLES". ES BASE-60.
   
   ESCALA DE VERDAD: 0 a 60 (NO 0 a 100%).
"""

import os
import math
import sys
from collections import Counter

# Import opcional para integración, pero el scanner debe funcionar standalone
# from yatra_core import S60 

class ResonanceScanner:
    def __init__(self):
        self.BASE_HARMONIC = 60
        self.MAX_SCORE = 60 # La verdad completa es 60/60
        self.STABILITY_THRESHOLD = 48 # 80% de 60

    def _calculate_entropy_integer(self, data):
        """
        Calcula entropía mapeada a escala 0-60.
        Menor entropía = Mayor Orden.
        Retorna un puntaje de ORDEN (0=Caos, 60=Cristal).
        """
        if not data:
            return 0
            
        # Aproximación entera de Shannon
        # Usamos frecuencias relativas escaladas
        length = len(data)
        counts = Counter(data)
        
        # En lugar de logaritmos complejos (que requieren floats),
        # medimos la "compresibilidad" simple:
        # Ratio de bytes únicos vs total
        unique_bytes = len(counts)
        
        # Si todos los bytes son diferentes, entropía máxima (Score 0)
        # Si todos son iguales, entropía mínima (Score 60)
        
        if length == 0: return 0
        
        # Ratio inverso: (1 - unique/length) * 60
        # Usamos multiplicación primero para mantener enteros
        # score = 60 * (length - unique_bytes) // length
        
        # Sin embargo, Shannon es mejor. Vamos a permitir math.log2 SOLO aqui
        # pero convertir inmediatamente a entero para el resultado.
        entropy_sum = 0.0
        for count in counts.values():
            p = count / length
            entropy_sum -= p * math.log2(p)
            
        # Entropía de Shannon va de 0 a 8 (bits).
        # Queremos mapear 0->60 (Orden) y 8->0 (Caos).
        # Un archivo de código fuente típico tiene entropía ~4-5.
        
        entropy_int = int(entropy_sum * 10) # Preservar 1 decimal como entero
        
        # Mapeo: 8.0 (80) -> 0 pts
        #        0.0 (0)  -> 60 pts
        # Formula lineal inversa: 60 - (entropy * 7.5) aprox
        # Usaremos: 60 - (entropy_int * 60 // 80)
        
        order_score = 60 - (entropy_int * 60 // 80)
        return max(0, order_score)

    def _calculate_harmonic_alignment(self, data):
        """
        Mide alineación con Base-60 y Tesla (3,6,9).
        Retorna puntaje 0-60.
        """
        length = len(data)
        if length == 0: return 0
        
        # 1. Resonancia de Longitud (30 pts max)
        remainder = length % self.BASE_HARMONIC
        # Distancia al nodo (0 es mejor)
        dist = min(remainder, self.BASE_HARMONIC - remainder)
        
        # Score = 30 * (1 - dist/30)
        length_score = 30 - dist
        
        # 2. Resonancia Tesla (30 pts max)
        byte_sum = sum(data)
        root = (byte_sum - 1) % 9 + 1
        
        tesla_score = 0
        if root in [3, 6, 9]:
            tesla_score = 30
        else:
            tesla_score = 15 # Consuelo
            
        return length_score + tesla_score

    def scan_file(self, filepath):
        """Escanea archivo. Retorna dict con valores ENTEROS."""
        if not os.path.exists(filepath):
            return {"error": "File not found"}
            
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # --- MEDICIÓN ---
            score_entropy = self._calculate_entropy_integer(data) # 0-60
            score_harmonic = self._calculate_harmonic_alignment(data) # 0-60
            
            # --- SÍNTESIS (Promedio Ponderado Entero) ---
            # Peso: 40% Entropía, 60% Armonía (La estructura importa más)
            # Formula: (E*4 + H*6) // 10
            final_score = (score_entropy * 4 + score_harmonic * 6) // 10
            
            status = "DISSONANT 🔴"
            if final_score >= 54: status = "SOVEREIGN 🟣" # >= 90%
            elif final_score >= 42: status = "HARMONIC 🟢" # >= 70%
            elif final_score >= 30: status = "STABLE 🟡"   # >= 50%
            
            tesla_root = (sum(data) - 1) % 9 + 1
            
            return {
                "file": os.path.basename(filepath),
                "size_bytes": len(data),
                "order_score": score_entropy,      # /60
                "harmonic_score": score_harmonic,  # /60
                "resonance_score": final_score,    # /60
                "status": status,
                "tesla_root": tesla_root
            }
            
        except Exception as e:
            return {"error": str(e)}

def main():
    scanner = ResonanceScanner()
    target = __file__
    if len(sys.argv) > 1:
        target = sys.argv[1]
        
    print(f"👁️  SCANNING: {target}")
    r = scanner.scan_file(target)
    
    if "error" in r:
        print(f"❌ Error: {r['error']}")
    else:
        print("-" * 40)
        print(f"📂 Archivo:    {r['file']}")
        print(f"📏 Tamaño:     {r['size_bytes']} bytes")
        print(f"🎲 Orden:      {r['order_score']}/60")
        print(f"⚖️  Armonía:    {r['harmonic_score']}/60")
        print(f"⚡ Tesla Root: {r['tesla_root']}")
        print("-" * 40)
        print(f"🔮 RESONANCIA: {r['resonance_score']}/60")
        print(f"🏷️  ESTADO:     {r['status']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
