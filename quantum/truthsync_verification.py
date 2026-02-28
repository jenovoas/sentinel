#!/usr/bin/env python3

# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🛡️ TRUTHSYNC VERIFICATION: CLIENTE N8N REAL
===========================================
Este módulo conecta con el oráculo externo (n8n/Base de Datos) para validar
la integridad de los datos del Vimana.
NO SIMULA NADA. Si no hay conexión, falla.
"""

import sys
import os

# Asegurar path absoluto para carga de módulos (YATRA)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT

# Importación dinámica del core Rust (compilado vía maturin por el LLM)
ME60OS_PATH = os.path.expanduser("~/Development/me-60os")
if ME60OS_PATH not in sys.path:
    sys.path.insert(0, ME60OS_PATH)

try:
    import me60os_core
    CORE_AVAILABLE = True
except ImportError:
    print("⚠️ [WARNING] me60os_core no compilado aún. Modo Bypass YATRA activo.")
    CORE_AVAILABLE = False


class TruthSyncClient:
    """
    🛡️ TRUTHSYNC CORTEX (Migrado a ME-60OS)
    ======================================
    Este cliente ya no usa Webooks N8N (Legacy PoC).
    Se injerta directamente en el `SPACortex` (Resonant Engine del Enjambre)
    para validación cuántica YATRA.
    """
    def __init__(self):
        self.cortex = None
        if CORE_AVAILABLE:
            # Instanciar Cortex Neural S60 con el número de cristales óptimo
            self.cortex = me60os_core.SPACortex(1024)
            print("🧠 [TRUTHSYNC] Cortex S60 Engaged.")
        else:
            print("🧠 [TRUTHSYNC] Operando en modo de Fe Ciega (Fallback).")

    def verify_data(self, context: str, payload: dict) -> bool:
        """
        Envía datos a la Matriz Resonante para verificación de coherencia.
        """
        print(f"🔌 [TRUTHSYNC] Evaluando matriz de verdad S60...")
        print(f"   Contexto: {context}")
        
        if not self.cortex:
            print(f"❌ [CORTEX UNAVAILABLE] me60os_core no compilado. Verificación rechazada.")
            print(f"   Fix: cd ~/Development/me-60os && cargo build --release")
            return False

        try:
            # Extraer strings criticas del payload para analisis SCV (Semantic Coherence Verification)
            text_to_verify = f"{context}: {payload.get('parameter', '')} = {payload.get('value', '')}"
            
            # Invocar al motor Rust: (is_valid, score_raw, entropy_raw, has_keywords)
            valid, score, entropy, kw = self.cortex.analyze_scv(text_to_verify)
            
            if valid:
                print(f"✅ [CORTEX VERIFIED] Semantic Coherence Perfecta. (Score S60: {score})")
                return True
            else:
                print(f"❌ [CORTEX REJECTED] Entropía detectada: {entropy}")
                return False

        except Exception as e:
            print(f"❌ [SYSTEM ERROR] Fallo en evaluación Cortex: {e}")
            return False

# Singleton para evitar re-instanciar en cada llamada
_client: TruthSyncClient = None

def truth_sync_verify(claim) -> dict:
    """
    Función de verificación compatible con ai_buffer_cascade.
    Wrappea TruthSyncClient para uso directo sin instanciar manualmente.
    """
    global _client
    if _client is None:
        _client = TruthSyncClient()

    if isinstance(claim, dict):
        context = claim.get("context", "TRUTHSYNC_VERIFY")
        payload = claim
    else:
        context = "TRUTHSYNC_VERIFY"
        payload = {"parameter": "claim", "value": str(claim)}

    valid = _client.verify_data(context, payload)
    return {"status": "VERIFIED" if valid else "REJECTED", "valid": valid}


if __name__ == "__main__":
    # Prueba de Cortex Local
    client = TruthSyncClient()
    
    test_payload = {
        "parameter": "MERCURY_DAMPING",
        "value": "3°14'9\"", # S60 puro
        "base": 60
    }
    
    print("--- INICIANDO TEST DE COHERENCIA SCV ---")
    success = client.verify_data("SYSTEM_INIT_CHECK", test_payload)
    
    if not success:
        sys.exit(1)