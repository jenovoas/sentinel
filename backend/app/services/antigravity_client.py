"""
Antigravity AI Client - Google AI Studio Integration
Supports HTTP Basic Auth for accessing Gemini models
"""

import httpx
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

SOVEREIGN_SYSTEM_PROMPT = """
SISTEMA SOBERANO SENTINEL - DIRECTIVAS PRIMARIAS:
1. MATEMÁTICA: Usa exclusivamente Base-60 (Sexagesimal). 
   - 0.1 es una abominación. Usa fracciones de 60 (ej: 6/60).
   - Constantes prohibidas: 0.1, 0.2, 0.5, 0.01 (salvo si son armónicas).
2. FÍSICA: No uses aproximaciones newtonianas baratas.
   - Usa SovereignPhysics para cálculos.
   - La masa varía con la coherencia del alma.
3. TECNOLOGÍA: Respeta MHDPlasmaShield y SovereignAstrolabe.
NO ROMPAS LA PUREZA MATEMÁTICA O SERÁS DESCARTADO.
"""

class AntigravityClient:
    """
    Client for Antigravity AI (Google AI Studio / Gemini)
    
    Supports:
    - HTTP Basic Authentication
    - Multiple Gemini models (gemini-pro, gemini-1.5-flash, etc.)
    - Streaming and non-streaming responses
    - Rate limiting awareness
    """
    
    def __init__(
        self, 
        base_url: str = None,
        username: str = None,
        password: str = None,
        api_key: str = None
    ):
        """
        Initialize Antigravity client
        
        Args:
            base_url: Antigravity endpoint URL
            username: HTTP Basic Auth username
            password: HTTP Basic Auth password  
            api_key: Alternative: API key for direct Google AI Studio
        """
        self.base_url = base_url or os.getenv("ANTIGRAVITY_URL", "https://generativelanguage.googleapis.com")
        self.username = username or os.getenv("ANTIGRAVITY_USERNAME")
        self.password = password or os.getenv("ANTIGRAVITY_PASSWORD")
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        
        # Setup authentication
        auth = None
        if self.username and self.password:
            auth = httpx.BasicAuth(self.username, self.password)
            logger.info(f"Antigravity client initialized with Basic Auth (user: {self.username})")
        elif self.api_key:
            logger.info("Antigravity client initialized with API Key")
        else:
            logger.warning("No authentication configured for Antigravity")
        
        self.client = httpx.AsyncClient(
            auth=auth,
            timeout=60.0,
            headers={"Content-Type": "application/json"}
        )
        
        # Model tier system with token limits (updated for 2025 models)
        self.model_tiers = [
            {"name": "gemini-2.0-flash-001", "max_tokens": 1000000, "output_limit": 8192},
            {"name": "gemini-2.5-flash", "max_tokens": 1000000, "output_limit": 8192},
            {"name": "gemini-2.5-pro", "max_tokens": 2000000, "output_limit": 8192},
        ]
        
        self.current_tier = 0
        self.default_model = self.model_tiers[0]["name"]
        self.total_tokens_used = 0
        self.conversation_tokens = 0
        
        logger.info(f"Initialized with model tier: {self.default_model}")
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters for English)"""
        return len(text) // 4
    
    def should_switch_model(self, prompt_tokens: int) -> bool:
        """Check if we should switch to a higher-tier model"""
        current_model = self.model_tiers[self.current_tier]
        
        # Switch at 85% capacity to avoid hitting limits
        threshold = current_model["max_tokens"] * 0.85
        
        if self.conversation_tokens + prompt_tokens > threshold:
            # Try to switch to next tier
            if self.current_tier < len(self.model_tiers) - 1:
                self.current_tier += 1
                new_model = self.model_tiers[self.current_tier]
                logger.warning(
                    f"🔄 Auto-switching model: {current_model['name']} → {new_model['name']} "
                    f"(tokens: {self.conversation_tokens}/{current_model['max_tokens']})"
                )
                self.conversation_tokens = 0  # Reset counter for new model
                return True
            else:
                logger.error("⚠️ At highest tier model, cannot switch further!")
        
        return False
    
    def get_current_model(self) -> str:
        """Get current active model"""
        return self.model_tiers[self.current_tier]["name"]
    
    async def generate(
        self, 
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_instruction: str = None
    ) -> Dict[str, Any]:
        """
        Generate response from Gemini model
        """
        model = model or self.default_model
        
        # Build request for Google AI Studio API
        if self.api_key:
            return await self._generate_with_api_key(
                prompt, model, temperature, max_tokens, system_instruction
            )
        else:
            return await self._generate_with_basic_auth(
                prompt, model, temperature, max_tokens, system_instruction
            )

    async def stream_generate(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system: str = None
    ):
        """Stream response from Gemini model with automatic model switching"""
        
        # Estimate tokens and check if we should switch
        prompt_tokens = self.estimate_tokens(prompt)
        if system:
            prompt_tokens += self.estimate_tokens(system)
        
        self.should_switch_model(prompt_tokens)
        
        # Use current tier model if no specific model requested
        if not model:
            model = self.get_current_model()
        
        if self.api_key:
            url = f"{self.base_url}/v1beta/models/{model}:streamGenerateContent"
            
            contents = []
            if system:
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"System: {system}"}]
                })
            
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                }
            }
            
            total_output = ""
            async with self.client.stream(
                "POST", url, json=payload, params={"key": self.api_key}, timeout=60.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            if line.startswith("data: "):
                                line = line[6:]
                            data = json.loads(line)
                            
                            if "candidates" in data and len(data["candidates"]) > 0:
                                text = data["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                if text:
                                    total_output += text
                                    yield text
                        except Exception:
                            continue
            
            # Update token counters
            output_tokens = self.estimate_tokens(total_output)
            self.conversation_tokens += prompt_tokens + output_tokens
            self.total_tokens_used += prompt_tokens + output_tokens
            
        else:
            # No API key available - error
            error_msg = "⚠️ GOOGLE_AI_API_KEY not configured. Please set it in sentinel_env.sh"
            logger.error(error_msg)
            yield error_msg
    
    async def _generate_with_api_key(
        self, 
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_instruction: str
    ) -> Dict[str, Any]:
        """Generate using direct Google AI Studio API"""
        
        url = f"{self.base_url}/v1beta/models/{model}:generateContent"
        
        # Build request body
        contents = []
        
        # Add system instruction (FORCED SOVEREIGNTY)
        full_system = SOVEREIGN_SYSTEM_PROMPT
        if system_instruction:
            full_system += f"\n\nCONTEXTO ESPECÍFICO:\n{system_instruction}"

        contents.append({
            "role": "user",
            "parts": [{"text": f"System: {full_system}"}]
        })
        
        # Add user prompt
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        try:
            response = await self.client.post(
                url,
                json=payload,
                params={"key": self.api_key}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response text
            text = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
            
            return {
                "response": text,
                "model": model,
                "usage": data.get("usageMetadata", {}),
                "metadata": {
                    "finish_reason": data.get("candidates", [{}])[0].get("finishReason"),
                    "safety_ratings": data.get("candidates", [{}])[0].get("safetyRatings", [])
                }
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Antigravity API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Antigravity error: {str(e)}")
            raise
    
    async def _generate_with_basic_auth(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_instruction: str
    ) -> Dict[str, Any]:
        """Generate using HTTP Basic Auth (custom Antigravity endpoint)"""
        
        # Assume custom endpoint format
        url = f"{self.base_url}/v1/chat/completions"
        
        messages = []
        
        # FORCED SOVEREIGNTY
        full_system = SOVEREIGN_SYSTEM_PROMPT
        if system_instruction:
            full_system += f"\n\nCONTEXTO ESPECÍFICO:\n{system_instruction}"
            
        messages.append({
            "role": "system",
            "content": full_system
        })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response (OpenAI-compatible format)
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "response": text,
                "model": model,
                "usage": data.get("usage", {}),
                "metadata": data.get("metadata", {})
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Antigravity API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Antigravity error: {str(e)}")
            raise
    
    async def list_models(self) -> list:
        """List available models"""
        if self.api_key:
            url = f"{self.base_url}/v1beta/models"
            try:
                response = await self.client.get(url, params={"key": self.api_key})
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            except Exception as e:
                logger.error(f"Failed to list models: {e}")
                return []
        else:
            # Return common Gemini models
            return [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro",
                "gemini-pro-vision"
            ]
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
antigravity_client = None

def get_antigravity_client() -> AntigravityClient:
    """Get or create Antigravity client instance"""
    global antigravity_client
    if antigravity_client is None:
        antigravity_client = AntigravityClient()
    return antigravity_client
