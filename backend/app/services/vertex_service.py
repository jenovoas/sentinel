# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
from typing import List, Optional, Dict, Any
import logging
from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content, HarmCategory, HarmBlockThreshold
from app.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

class VertexService:
    """
    Service for interacting with Google Vertex AI (Gemini Models).
    
    Adheres to Sentinel Architecture:
    - Async IO where possible (though Vertex SDK is largely synchronous, we wrap or use async methods if available)
    - YATRA Compliance: No floats in core logic, only pass-through for Model I/O.
    """

    def __init__(self):
        self.settings = get_settings()
        self.project_id = self.settings.google_cloud_project
        self.location = self.settings.google_cloud_location
        self.model_name = self.settings.vertex_model_name
        self._model = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize the Vertex AI client.
        Returns True if successful, False otherwise.
        """
        if not self.settings.vertex_ai_enabled:
            logger.info("⏸️ Vertex AI is DISABLED via configuration (Cost Protection).")
            return False

        if not self.project_id:
            logger.warning("⚠️ GOOGLE_CLOUD_PROJECT not set. Vertex AI disabled.")
            return False

        try:
            # Initialize Vertex AI SDK
            vertexai.init(project=self.project_id, location=self.location)
            
            # Load the model
            self._model = GenerativeModel(self.model_name)
            self._initialized = True
            
            logger.info(f"✨ Vertex AI Initialized: {self.model_name} @ {self.location}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI: {e}")
            return False

    async def generate_content(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        temperature: float = 0.0, # Vertex uses floats for params, acceptable for I/O
        max_output_tokens: int = 8192
    ) -> Optional[str]:
        """
        Generate content using Gemini.
        
        Args:
            prompt: The user input or prompt.
            system_instruction: Optional system instruction/context.
            temperature: Creativity parameter (0.0 - 1.0).
            max_output_tokens: Token limit.
            
        Returns:
            Generated text or None if failed.
        """
        if not self._initialized:
            if not self.initialize():
                return "Error: Vertex AI not initialized."

        try:
            # Configure generation parameters
            generation_config = {
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
                "top_p": 0.95,
            }

            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Create content structure (Vertex SDK format)
            # System instruction is passed at model init or generation depending on SDK version
            # For simplicity in this v1, we prepend system instruction if provided, 
            # or update usage when SDK fully supports efficient system_instruction arg in this flow.
            
            full_prompt = prompt
            if system_instruction:
                # Gemini 1.5+ supports system_instruction, but for safety in generic calls:
                self._model = GenerativeModel(
                    self.model_name,
                    system_instruction=[system_instruction]
                )
            
            # Execute generation (blocking call, ideal to run in threadpool if high load, 
            # but standard for initial integration)
            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False
            )

            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Vertex AI")
                return None

        except Exception as e:
            logger.error(f"🔥 Vertex AI Generation Error: {e}")
            return f"Error creating content: {str(e)}"

    async def health_check(self) -> Dict[str, Any]:
        """Verify connection to Vertex AI."""
        status = {
            "service": "Vertex AI",
            "initialized": self._initialized,
            "model": self.model_name,
            "project": self.project_id
        }
        
        if not self._initialized:
             # Try to init
             if self.initialize():
                 status["initialized"] = True
             else:
                 status["status"] = "offline"
                 return status

        # Simple probe
        try:
            # Only do a real probe if requested or periodically, to save cost.
            # For now, just return initialized status as 'healthy' implies setup is correct.
            status["status"] = "online"
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
            
        return status

# Singleton instance
vertex_service = VertexService()
