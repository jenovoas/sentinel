"""
Sentinel Vault - TruthSync Verification Service
Integrates Local AI (Ollama) to verify factual claims in real-time.
"""
import httpx
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TruthSyncService:
    """Core Verification Engine using Local AI"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = f"{ollama_url}/api/generate"
        self.model = "phi3:mini"

    async def verify_content(self, text: str, source_url: str) -> Dict:
        """
        Analyze text for misinformation, logical fallacies, and trust score.
        """
        # Truncate text for performance (first 2000 chars)
        abbreviated_text = text[:2000].replace('"', "'")
        
        prompt = f"""Analyze this web content for factual accuracy and trust.
        
        Source: {source_url}
        Content (Snippet): {abbreviated_text}
        
        Evaluate:
        1. Factuality (Is it stating facts or opinions?)
        2. Signs of Manipulation (Clickbait, Logical Fallacies, Emotional Loading)
        3. Trust Score (0-100)
        
        Return JSON ONLY:
        {{
            "score": <0-100>,
            "verdict": "<VERIFIED | SUSPICIOUS | UNVERIFIED | MISINFO>",
            "reasoning": "<Available analysis summary>",
            "flags": ["list", "of", "detected", "issues"]
        }}
        """
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json" # Force JSON mode if supported
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Ollama Error: {response.text}")
                    return self._fallback_analysis()

                result = response.json()
                raw_response = result.get("response", "")
                
                # Robust JSON extraction
                try:
                    start = raw_response.find("{")
                    end = raw_response.rfind("}") + 1
                    json_str = raw_response[start:end]
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Ollama JSON, using heuristics.")
                    return self._fallback_analysis()
                    
        except Exception as e:
            logger.error(f"TruthSync Error: {str(e)}")
            return self._fallback_analysis()

    def _fallback_analysis(self) -> Dict:
        """Fallback if AI is unavailable"""
        return {
            "score": 50,
            "verdict": "UNVERIFIED",
            "reasoning": "AI Service Unavailable. Analysis skipped.",
            "flags": ["service_offline"]
        }
