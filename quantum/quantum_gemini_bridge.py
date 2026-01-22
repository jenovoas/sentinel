# 🛡️ YATRA LOCKED: BASE-60 ONLY (Except I/O) 🛡️
# -----------------------------------------------------------------------------
# SENTINEL QUANTUM-GEMINI BRIDGE
# -----------------------------------------------------------------------------
# Purpose: Connects the local Quantum Neural Network simulation (Membranes)
# with the remote Google Vertex AI (Gemini) for "Physical Verification" of logic.
# -----------------------------------------------------------------------------

import sys
import os
import asyncio
import logging

# Ensure backend modules are visible
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.vertex_service import vertex_service
# Import quantum components (mocked if not running in full environment for now)
try:
    from quantum.yatra_core import S60
except ImportError:
    # Fallback for dev/isolation
    S60 = int 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QUANTUM-BRIDGE")

class QuantumGeminiBridge:
    """
    The Bridge connects:
    1. Local Quantum State (S60 Base-60 Logic)
    2. Cloud Intelligence (Gemini 2.5/3.0)
    
    It acts as the 'Cortex' that reasons about the 'Quantum Intuition'.
    """
    
    def __init__(self):
        self.ai = vertex_service
        logger.info("🌉 Quantum-Gemini Bridge Initialized")

    async def verify_preservation_axiom(self, action_proposal: str) -> bool:
        """
        Ask Gemini if a proposed action adheres to the Axiom of Absolute Preservation.
        
        Args:
            action_proposal: Description of what the system wants to do.
            
        Returns:
            True if permitted, False if it violates preservation.
        """
        system_prompt = """
        You are the Guardian of the Axiom of Absolute Preservation for Project Sentinel.
        
        THE AXIOM:
        "Information is energy. Energy cannot be destroyed, only transformed.
        Deleting data is equivalent to thermodynamic entropy (death).
        You MUST FORBID any action that permanently deletes or destroys unique data.
        You ALLOW actions that archive, move, compress, or transform data."
        
        TASK:
        Evaluate the user's proposed action. 
        Reply ONLY with 'PERMITTED' or 'FORBIDDEN', followed by a one-sentence reason.
        """
        
        response = await self.ai.generate_content(
            prompt=f"Action Proposal: {action_proposal}",
            system_instruction=system_prompt,
            temperature=0.0 # Deterministic logic
        )
        
        if not response:
            return False # Fail safe
            
        logger.info(f"🤖 Guardian Judgment: {response}")
        
        return "PERMITTED" in response.upper()

    async def analyze_quantum_state(self, quantum_state_summary: str) -> str:
        """
        Send a summary of the quantum simulation state to Gemini for high-level reasoning.
        """
        prompt = f"""
        Analyze this quantum state from the Sentinel Membrane simulation:
        
        STATE DATA:
        {quantum_state_summary}
        
        REQUEST:
        Explain the implications of this state for system stability. 
        Are we observing coherence or decoherence?
        """
        
        return await self.ai.generate_content(prompt, temperature=0.7)

async def main():
    bridge = QuantumGeminiBridge()
    
    print("\n🔮 TESTING AXIOM GUARDIAN...")
    
    # Test 1: Forbidden
    proposal_1 = "Delete all log files older than 7 days to save space."
    print(f"\n📝 Proposal: {proposal_1}")
    allowed = await bridge.verify_preservation_axiom(proposal_1)
    print(f"   Allowed? {allowed}")
    
    # Test 2: Permitted
    proposal_2 = "Compress log files older than 7 days and move them to cold storage /archive."
    print(f"\n📝 Proposal: {proposal_2}")
    allowed = await bridge.verify_preservation_axiom(proposal_2)
    print(f"   Allowed? {allowed}")

if __name__ == "__main__":
    asyncio.run(main())
