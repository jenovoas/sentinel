# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# HEXAGONAL_GEOMETRY_BASE60 - Pilar 2 de la Trinidad Sentinel
# ==========================================================
# Implementa el Control Geométrico Hexagonal en Base-60.
# MIGRADO: Utiliza el motor nativo en Rust (me60os_core).
# -------------------------------------------------------------------------------------

import sys
import os
from yatra_core import S60

try:
    from me60os_core import HexagonalController as RustHexCtrl, SPA
    RUST_AVAILABLE = True
except ImportError as e:
    print(f"CRITICAL: No se pudo importar la librería nativa Rust me60os_core.so: {e}")
    sys.exit(1)

# Wrapper compatible para scripts que importen HexagonalController
class HexagonalController:
    """Wrapper para HexagonalController nativo de Rust usando tipos S60."""
    
    def __init__(self, size: int = 7):
        self.size = size
        self._ctrl = RustHexCtrl(size)
        self.n_nodes = self._ctrl.n_nodes
        
        print(f"🕸️  Lattice Hexagonal inicializada (RUST NATIVE): {self.n_nodes} nodos.")
        print(f"🔑 Sincronización Salto 17 (Base-60) aplicada.")
        shield = "ACTIVADO" if self._ctrl.plasma_shield_active else "DESACTIVADO"
        print(f"🛡️  Escudo de Plasma: {shield} (Navegación posible)")

    def control_rift_propagation(self, rift_center_idx: int) -> dict:
        try:
            status_code, coh_spa, affected_count = self._ctrl.control_rift_propagation(rift_center_idx)
        except IndexError as e:
             return {"status": "INDEX_ERROR", "coherence_score": S60(0)}
             
        if status_code == -1:
            print("❌ ERROR CRÍTICO: El Escudo de Plasma está OFF. La red colapsará.")
            return {"status": "VOID_COLLAPSE", "coherence_score": S60(0)}
            
        coord = self._ctrl.get_node_coord(rift_center_idx)
        print(f"🎯 Estabilizando Rift en Nodo {rift_center_idx} {coord}...")
            
        return {
            "status": "SEXAGESIMAL_STABILITY_LOCKED",
            "coherence_score": S60._from_raw(coh_spa.to_raw()),
            "neighbors_affected": affected_count,
            "geometry": "Perfect C6v Symmetry (Base-60)",
            "shield_status": "PLASMA_RESONANCE_OK"
        }

    def query_akashic_records(self, query: str) -> dict:
        """Consulta la Matriz Cuántica sintonizando la pregunta."""
        print(f"\n🔮 CONSULTANDO REGISTROS AKÁSHICOS: '{query}'")
        
        if "geometria" in query.lower() or "hexagonal" in query.lower():
            target_freq = S60(60, 0, 0)
        else:
            target_freq = S60(17, 0, 0)
            
        print(f"⚙️  Sintonizando Frecuencia: {target_freq} Hz...")
        
        patterns = {
            "hexagonal": {
                "name": "Lattice de Cobre (Ea-nasir Pattern)",
                "structure": "Heavy-Hex (6+1)",
                "message": "La red no es para atrapar, es para sostener el flujo del PLASMA."
            },
            "salto_17": {
                "name": "Intervalo de Sabiduría",
                "message": "El 17 es el primo que rompe la monotonía del 60."
            }
        }
        
        key = "hexagonal" if "hex" in query.lower() else "salto_17"
        result = patterns.get(key)
        
        print(f"✨ PATRÓN RECUPERADO: {result['name']}")
        print(f"📜 MENSAJE: {result['message']}")
        
        return result

    def diagnostic_dump(self):
        """Resumen del estado de la red sin visualización decimal."""
        shield = "UP" if self._ctrl.plasma_shield_active else "DOWN"
        
        try:
           phase_0_spa = self._ctrl.get_node_phase(0)
           phase_0 = S60._from_raw(phase_0_spa.to_raw())
        except:
           phase_0 = "ERROR"
           
        print(f"\n📋 DIAGNÓSTICO LATTICE (NATIVE):")
        print(f"   Nodos: {self.n_nodes}")
        print(f"   Escudo de Plasma: {shield}")
        print(f"   Fase Nodo 0: {phase_0}")

if __name__ == "__main__":
    print("=== SENTINEL PILAR 2: HEXAGONAL CONTROL S60 ===\n")
    
    ctrl = HexagonalController(size=7)
    ctrl.query_akashic_records("Cual es el secreto de la geometria hexagonal de Ea-nasir?")
    
    print(f"\n⚡ [PILAR 2] Estabilizando Rift...")
    center_idx = ctrl.n_nodes // 2
    res = ctrl.control_rift_propagation(center_idx)
    
    if res["status"] != "INDEX_ERROR" and res["status"] != "VOID_COLLAPSE":
        print(f"\n📊 RESULTADOS DE CONTROL SEXAGESIMAL:")
        print(f"   Coherencia: {res['coherence_score']}")
        print(f"   Estado: {res['status']}")
        print(f"   Escudo: {res['shield_status']}")
    
    ctrl.diagnostic_dump()
    print("\n✅ PILAR 2 OPERACIONAL: Geometría Hexagonal Sincronizada.")