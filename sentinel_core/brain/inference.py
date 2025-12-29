import ollama
import time
from ..config import AI_MODEL_NAME, AI_LATENCY_SIMULATION

class SentinelBrain:
    """
    Cerebro de Sentinel Cortex (Real Intelligence).
    Usa Ollama localmente (Phi-3 Mini / Llama3) para analizar semánticamente
    si un comando o binario representa una amenaza.
    """

    def __init__(self):
        print(f"🧠 [SentinelBrain] Conectando a Ollama Local: {AI_MODEL_NAME}")
        # Verificar conexión inicial (opcional)
        try:
            ollama.list()
            print("✅ [SentinelBrain] Conexión a Ollama exitosa.")
        except Exception as e:
            print(f"❌ [SentinelBrain] Error conectando a Ollama: {e}")

    def analyze_threat(self, filename: str) -> bool:
        """
        Analiza un binario usando LLM para inferir intención.

        Args:
            filename (str): El nombre del binario.

        Returns:
            bool: True (PERMITIR) o False (BLOQUEAR).
        """
        print(f"🤔 [Brain] Consultando a {AI_MODEL_NAME} sobre: '{filename}'...")
        
        # Prompt Ingeniería para Seguridad (Optimizado para Phi-3)
        prompt = f"""
        You are a Linux Kernel Security mechanism.
        Analyze the execution of the binary: "{filename}".
        
        Context: The system is under high security mode.
        
        Rules:
        1. "Safe" binaries: Standard Linux utilities (ls, grep, cat, git, htop), system services, known benign tools, **Sentinel Cortex components** (e.g. /opt/sentinel/...), and **Ollama** (/usr/local/bin/ollama). -> ALLOW
        2. "Threat" binaries: Hacking tools, malware names, or suspicious locations (/tmp/exploit). -> BLOCK
        
        Task:
        Return a JSON object with a single key "allow" set to true or false.
        Example Safe: {{"allow": true}}
        Example Threat: {{"allow": false}}
        
        Analyze: "{filename}"
        JSON Response:
        """

        try:
            response = ollama.chat(model=AI_MODEL_NAME, messages=[
                {'role': 'user', 'content': prompt},
            ])
            
            content = response['message']['content']
            # print(f"🐛 [Debug] Raw Response: {content}") # Debugging Removed
            
            # Parseo más robusto (ignorar markdown ```json ... ```)
            cleaned_content = content.lower().replace("```json", "").replace("```", "").strip()
            
            if '"allow": true' in cleaned_content or '"allow":true' in cleaned_content:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"⚠️ [Brain] Fallo en inferencia: {e}. Aplicando Fail-Safe (BLOQUEAR).")
            return False
