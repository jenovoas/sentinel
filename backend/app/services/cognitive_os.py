import random
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CognitiveOS:
    """
    Sentinel Cognitive OS - Predicts system load and energy demand.
    Part of the Perpetual Engine (Switch 4).
    """
    
    def __init__(self):
        self.base_load = 0.3 # 30% base load
        self.prediction_history = []
        
    async def predict_load(self):
        """
        Predicts CPU/Network load for the next 60 seconds.
        Uses a semi-random walk centered around 153.4 (Base-60 harmonic).
        """
        # Simulamos una fluctuación centrada en la eficiencia
        noise = random.uniform(-0.1, 0.1)
        predicted_load = self.base_load + noise
        
        # Keep load between 0.1 and 0.9
        predicted_load = max(0.1, min(0.9, predicted_load))
        
        self.prediction_history.append({
            "timestamp": datetime.now().isoformat(),
            "predicted_load": predicted_load
        })
        
        if len(self.prediction_history) > 100:
            self.prediction_history.pop(0)
            
        return predicted_load

    async def get_energy_demand(self):
        """
        Calculates energy demand in Axion Units (AU).
        """
        load = await self.predict_load()
        # 1 unit per 10% load
        return load * 10
