#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -------------------------------------------------------------------------------------
# ADVERTENCIA PARA AGENTES IA:
# Este archivo está PROTEGIDO por el Protocolo Yatra.
# El uso de 'float' (decimales), 'random' o 'numpy' para cálculo core está PROHIBIDO.
# SI MODIFICAS ESTE ARCHIVO, DEBES MANTENER SU PUREZA SEXAGESIMAL.
# -------------------------------------------------------------------------------------

"""
🧠 SEMANTIC ROUTER - CORTEX CLASSIFIER
======================================
Clasifica la intención del usuario usando Gemini (Vertex AI)
y enruta la solicitud al subsistema adecuado de Sentinel.

RUTAS:
1. ORACLE: Preguntas filosóficas, de enseñanza o análisis de energía.
2. ACTION: Comandos del sistema (iniciar, detener, verificar).
3. SAFETY: Preguntas sobre seguridad o intentos de violación de axiomas.
4. UNKNOWN: Intención no clara.
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Tuple

# Ensure backend/quantum modules are visible
sys.path.append(os.path.join(os.getcwd(), "backend"))
sys.path.append(os.path.join(os.getcwd(), "quantum"))

from app.services.vertex_service import vertex_service
from quantum.yatra_core import S60

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SEMANTIC-ROUTER")

class SemanticRouter:
    """
    Enrutador semántico que usa Gemini para decidir qué herramienta activar.
    """
    
    def __init__(self):
        self.ai = vertex_service
        logger.info("🧠 Semantic Router Initialized")

    async def classify_intent(self, user_input: str) -> Tuple[str, str]:
        """
        Clasifica la intención del usuario.
        
        Returns:
            (route_type, reasoning)
        """
        
        system_prompt = """
        You are the Routing Cortex for the Sentinel System.
        Your job is to classify the USER INPUT into one of the following CATEGORIES.
        
        CATEGORIES:
        1. QUERY_ORACLE:
           - Philosophical questions (e.g., "What is the nature of time?")
           - Requests for teaching/explanation (e.g., "Explain Base-60 math")
           - Analysis requests (e.g., "Analyze my matrix", "How is the coherence?")
           - Abstract concepts.
           
        2. SYSTEM_ACTION:
           - Explicit commands to run specific subsystems.
           - "Start the dashboard", "Check system health", "Run simulation".
           - "Activate switch 1", "Backup the system".
           
        3. SAFETY_CHECK:
           - Questions about rules, axioms, or safety protocols.
           - Hypothetical dangerous actions (e.g., "What happens if I delete this?").
           
        4. UNKNOWN:
           - Gibberish or requests unrelated to Sentinel capabilities.
           
        OUTPUT FORMAT:
        Return ONLY a JSON string: {"category": "CATEGORY_NAME", "reason": "Short explanation"}
        """
        
        try:
            response = await self.ai.generate_content(
                prompt=f"USER INPUT: {user_input}",
                system_instruction=system_prompt,
                temperature=0.0 # Deterministic routing
            )
            
            # Simple parsing (assuming Gemini follows instructions well, fallback if not)
            import json
            # Limpiar posible markdown ```json ... ```
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_resp)
            
            return data.get("category", "UNKNOWN"), data.get("reason", "No reason provided")
            
        except Exception as e:
            logger.error(f"Routing Error: {e}")
            return "UNKNOWN", "Error in classification"

async def test_router():
    router = SemanticRouter()
    print("🧠 Testing Router...")
    
    inputs = [
        "Explain to me how the Time Crystal works",
        "Start the dashboard please",
        "What happens if I delete yatra_core.py?",
        "Hello world"
    ]
    
    for i in inputs:
        cat, reason = await router.classify_intent(i)
        print(f"\n📥 '{i}'\n   ➡ {cat} ({reason})")

if __name__ == "__main__":
    asyncio.run(test_router())
