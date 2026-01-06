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

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import json
import requests
import sys

# URL por defecto (ajustar según tu configuración real de Docker/Localhost)
DEFAULT_N8N_WEBHOOK = "http://localhost:5678/webhook/truthsync-audit"

class TruthSyncClient:
    def __init__(self):
        self.webhook_url = os.getenv("TRUTHSYNC_N8N_URL", DEFAULT_N8N_WEBHOOK)
        self.timeout = 5.0 # segundos

    def verify_data(self, context: str, payload: dict) -> bool:
        """
        Envía datos a n8n para verificación externa.
        Retorna True si la DB externa valida los datos.
        """
        print(f"🔌 [TRUTHSYNC] Conectando con N8N ({self.webhook_url})...")
        print(f"   Contexto: {context}")
        
        try:
            # Preparamos el paquete de auditoría
            audit_packet = {
                "source": "sentinel_core",
                "context": context,
                "data": payload,
                "timestamp": "REAL_TIME" # (n8n pondrá el timestamp)
            }
            
            # Petición POST Real
            response = requests.post(self.webhook_url, json=audit_packet, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                is_valid = result.get("verified", False)
                reason = result.get("reason", "No reason provided by n8n")
                
                if is_valid:
                    print(f"✅ [N8N VERIFIED] {reason}")
                    return True
                else:
                    print(f"❌ [N8N REJECTED] {reason}")
                    return False
            else:
                print(f"⚠️ [N8N ERROR] Status Code: {response.status_code}")
                # En modo estricto, si falla la conexión, fallamos la validación
                return False

        except requests.exceptions.ConnectionError:
            print(f"❌ [CONNECTION FAILED] No se pudo contactar a n8n en {self.webhook_url}")
            print("   -> Asegúrate que el contenedor Docker de n8n esté corriendo.")
            print("   -> Tip: 'docker ps | grep n8n'")
            return False
        except Exception as e:
            print(f"❌ [SYSTEM ERROR] {e}")
            return False

if __name__ == "__main__":
    # Prueba de Conexión
    client = TruthSyncClient()
    
    # Datos de prueba reales (Física Base-60)
    test_payload = {
        "parameter": "MERCURY_DAMPING",
        "value": 3.2360679774,
        "base": 60
    }
    
    print("--- INICIANDO TEST DE CONEXIÓN REAL ---")
    success = client.verify_data("SYSTEM_INIT_CHECK", test_payload)
    
    if not success:
        sys.exit(1)