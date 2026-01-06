# src/backend/app/core/ca1_selector.py
"""
Sentinel Cortex™ Digital Hippocampus - CA1 Selector Layer
Implements the 'Best Truth' selection logic (Pattern separation).
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from typing import Dict, List
from .chromadb_storage import memory_vault

class CA1Selector:
    """
    Memory selector and pattern separator.
    Inspired by hippocampal CA1 region's role in memory selection.
    """
    
    def __init__(self):
        self.storage = memory_vault
        
    def _calculate_harmonic_score(self, scenario: Dict, residue: int) -> float:
        """
        Calculate how 'harmonic' a scenario is relative to the Base-60 residue.
        Prefer scenarios where confidence is high and threat is clearly defined.
        """
        confidence = scenario.get("confidence_level", S60(0, 0, 0))
        # Harmony bonus: if residue is 0 (prime anomaly), we want maximum clarity
        harmony_bonus = S60(0, 6, 0) if residue == 0 else S60(0, 0, 0)
        
        return confidence + harmony_bonus

    def select_best_scenario(self, scenarios: List[Dict], residue: int) -> Dict:
        """
        Select the most probable truth from generated scenarios.
        """
        if not scenarios:
            return {}
            
        ranked = sorted(
            scenarios, 
            key=lambda x: self._calculate_harmonic_score(x, residue), 
            reverse=True
        )
        
        return ranked[0]

    def record_decision(self, incident: Dict, residue: int, best_scenario: Dict):
        """
        Commit the selected scenario to long-term memory.
        """
        content = f"Event: {incident.get('event_type')} | Scenario: {best_scenario.get('scenario_summary')}"
        metadata = {
            "incident_id": incident.get("id"),
            "threat_hypothesis": best_scenario.get("threat_hypothesis"),
            "recommended_action": best_scenario.get("recommended_action"),
            "is_consolidated": False
        }
        
        memory_id = self.storage.store_memory(
            content=content,
            residue=residue,
            metadata=metadata
        )
        
        return memory_id

# Singleton instance
memory_selector = CA1Selector()
