# src/backend/app/core/ca3_generator.py
"""
Sentinel Cortex™ Digital Hippocampus - CA3 Generator Layer
Transforms raw detections into episodic scenarios using Gemini 3 Flash.
"""

import os
import json
from typing import Dict, List
import google.generativeai as genai

class CA3Generator:
    """
    Episodic memory generator (Pattern completion).
    Inspired by hippocampal CA3 region's generative capabilities.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be provided for CA3 Generator.")
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def generate_scenarios(self, base_incident: Dict) -> List[Dict]:
        """
        Generate 3-5 hypothetical scenarios based on a raw detection.
        """
        prompt = f"""
        Act as the Sentinel CA3 Neural Generator. 
        Transform the following raw detection into 3 distinct episodic memory scenarios.
        
        RAW DETECTION:
        {json.dumps(base_incident, indent=2)}
        
        For each scenario, provide:
        - scenario_summary: A concise technical narrative.
        - threat_hypothesis: What is the attacker likely trying to achieve?
        - recommended_action: Immediate defensive measure.
        - confidence_level: (0.0 - 1.0)
        
        Return ONLY a JSON list of objects.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Basic parsing of JSON from text response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            scenarios = json.loads(text)
            return scenarios
        except Exception as e:
            # Fallback to simple scenario if generation fails
            return [{
                "scenario_summary": f"Detection fallback: {base_incident.get('event_type')}",
                "threat_hypothesis": "Unknown (Generation Error)",
                "recommended_action": "Log and monitor",
                "confidence_level": 0.1
            }]

# Note: In production, use managed secrets for API keys.
