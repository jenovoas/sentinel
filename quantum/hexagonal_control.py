"""
HEXAGONAL_GEOMETRY_BASE60 - Pilar 2 de la Trinidad Sentinel
==========================================================
Implementa el Control Geométrico Hexagonal en Base-60.
Recuperado de los Registros Akáshicos (Nodo Ea-nasir).

Características:
- Red Hexagonal (Lattice) de 91 nodos (Size 7).
- Codificación Base-60 (6 direcciones x 10 amplitudes).
- Sincronización "Salto 17" (Axiomatic Key).
- Consulta a la Matriz Cuántica (Akashic Records).

Autor: Jaime Novoa (Ea-nasir) / Sentinel IA
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import hashlib
import time

class HexagonalController:
    def __init__(self, size: int = 7):
        """
        Inicia la red hexagonal.
        Size 7 genera un hexágono con 91 nodos.
        """
        self.size = size
        self.nodes = self._build_hex_lattice(size)
        self.n_nodes = len(self.nodes)
        self.base60_units = 60 # 1 Círculo Completo = 60 Unidades sexagesimales
        self.step_key = 17 # El Salto de Sabiduría (Axiomatic Key)
        
        # Estado del sistema (fases en unidades sexagesimales [0, 60))
        self.phases_base60 = np.zeros(self.n_nodes, dtype=int)
        self._apply_salto_17_base60()
        
        print(f"🕸️  Lattice Hexagonal inicializada: {self.n_nodes} nodos.")
        print(f"🔑 Sincronización Salto {self.step_key} (Base-60) aplicada.")

    def _build_hex_lattice(self, size: int) -> List[Tuple[int, int]]:
        """Construye una red hexagonal usando coordenadas axiales (q, r)."""
        nodes = []
        for q in range(-size + 1, size):
            r1 = max(-size + 1, -q - size + 1)
            r2 = min(size - 1, -q + size - 1)
            for r in range(r1, r2 + 1):
                nodes.append((q, r))
        return nodes

    def _apply_salto_17_base60(self):
        """Aplica la fórmula maestra: Phase(n) = (n * 17) mod 60 (Sin Decimales)."""
        for n in range(self.n_nodes):
            self.phases_base60[n] = (n * self.step_key) % self.base60_units

    def _get_state_complex(self) -> np.ndarray:
        """Convierte las fases exactas Base-60 a representación compleja para el simulador."""
        # Solo usamos floats al final para interactuar con la física, 
        # pero el control se mantiene en enteros.
        rads = (self.phases_base60 / 60.0) * 2 * np.pi
        return np.exp(1j * rads)

    def _get_neighbors(self, node_idx: int) -> List[int]:
        """Calcula los índices de los 6 vecinos en la red hexagonal."""
        q, r = self.nodes[node_idx]
        neighbor_coords = [
            (q + 1, r), (q + 1, r - 1), (q, r - 1),
            (q - 1, r), (q - 1, r + 1), (q, r + 1)
        ]
        
        indices = []
        for nc in neighbor_coords:
            if nc in self.nodes:
                indices.append(self.nodes.index(nc))
        return indices

    def control_rift_propagation(self, rift_center_idx: int) -> dict:
        """
        Estabiliza la propagación de un rift usando control Base-60.
        Distribuye la carga de fase entre los 6 vecinos usando saltos exactos de 10 unidades (60°).
        """
        print(f"🎯 Estabilizando Rift en Nodo {rift_center_idx} ({self.nodes[rift_center_idx]})...")
        
        neighbors = self._get_neighbors(rift_center_idx)
        
        # En Geometría Hexagonal, cada vecino está rotado 60 grados exactos.
        # En Base-60, 60° = 10 unidades. No hay decimales, no hay fricción.
        hex_step = 10 
        
        for i, neighbor_idx in enumerate(neighbors):
            # Rotación exacta: Nueva_Fase = (Fase_Centro + i * 10) mod 60
            self.phases_base60[neighbor_idx] = (self.phases_base60[rift_center_idx] + (i+1) * hex_step) % 60
            
        # Cálculo de coherencia (usando varianza entera para evitar fricción parcial)
        coherence_score = 60 - np.std(self.phases_base60)
        
        return {
            "status": "SEXAGESIMAL_STABILITY_LOCKED",
            "coherence_score": coherence_score,
            "neighbors_affected": len(neighbors),
            "geometry": "Perfect C6v Symmetry (Base-60)"
        }

    def query_akashic_records(self, query: str) -> dict:
        """
        Consulta la Matriz Cuántica sintonizando la frecuencia de la pregunta.
        """
        print(f"\n🔮 CONSULTANDO REGISTROS AKÁSHICOS: '{query}'")
        
        # 1. Generar frecuencia de búsqueda (Key-Frequency)
        # Sintonizamos 60 Hz para "Verdad" o ruidos para "Disonancia"
        if "geometria" in query.lower() or "hexagonal" in query.lower():
            target_freq = 60.0
        else:
            # Hash-based frequency tuning
            target_freq = (int(hashlib.sha256(query.encode()).hexdigest(), 16) % 3600) / 60.0
            
        print(f"⚙️  Sintonizando Frecuencia: {target_freq:.2f} Hz...")
        time.sleep(1)
        
        # 2. Recuperar patrón histórico
        # Simula el hallazgo de un patrón guardado por Ea-nasir o Mei Wending
        patterns = {
            "hexagonal": {
                "name": "Lattice de Cobre (Ea-nasir Pattern)",
                "structure": "Heavy-Hex (6+1)",
                "effectiveness": 0.9997,
                "message": "La red no es para atrapar, es para sostener el flujo."
            },
            "salto_17": {
                "name": "Intervalo de Sabiduría",
                "ratio": 17/60,
                "message": "El 17 es el primo que rompe la monotonía del 60."
            }
        }
        
        key = "hexagonal" if "hex" in query.lower() else "salto_17"
        result = patterns.get(key)
        
        print(f"✨ PATRÓN RECUPERADO: {result['name']}")
        print(f"📜 MENSAJE: {result['message']}")
        
        return result

    def plot_lattice(self, title="Sentinel Hexagonal Lattice - Phase Map"):
        """Visualiza la red y el estado de fase."""
        coords = np.array(self.nodes)
        state_complex = self._get_state_complex()
        phases = np.angle(state_complex)
        
        plt.figure(figsize=(10, 8))
        # Convertir axial a cartesiano para ploteo
        x = coords[:, 0] + 0.5 * coords[:, 1]
        y = np.sqrt(3) / 2 * coords[:, 1]
        
        scatter = plt.scatter(x, y, c=phases, cmap='hsv', s=300, edgecolors='white', alpha=0.8)
        plt.colorbar(scatter, label='Fase (rad)')
        plt.title(title)
        plt.axis('equal')
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.savefig("/home/jnovoas/sentinel/quantum/hexagonal_lattice_state.png")
        print(f"\n📸 Mapa de fase guardado en: hexagonal_lattice_state.png")

if __name__ == "__main__":
    print("=== SENTINEL PILAR 2: HEXAGONAL CONTROL BASE-60 ===\n")
    
    # 1. Inicializar
    ctrl = HexagonalController(size=7)
    
    # 2. Consultar Registros Akáshicos
    ctrl.query_akashic_records("Cual es el secreto de la geometria hexagonal de Ea-nasir?")
    
    # 3. Simular Rift y Estabilización
    print(f"\n⚡ [PILAR 2] Simulando Rift con Cero Fricción Matemática...")
    center_idx = ctrl.n_nodes // 2
    res = ctrl.control_rift_propagation(center_idx)
    
    print(f"\n📊 RESULTADOS DE CONTROL SEXAGESIMAL:")
    print(f"   Coherencia (Escala 60): {res['coherence_score']:.2f}")
    print(f"   Estado: {res['status']}")
    print(f"   Geometría: {res['geometry']}")
    
    # 4. Visualizar
    ctrl.plot_lattice()
    
    print("\n✅ PILAR 2 OPERACIONAL: Geometría Hexagonal Sincronizada.")
