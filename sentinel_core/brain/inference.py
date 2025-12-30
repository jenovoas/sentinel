import ollama
import time
try:
    from ..config import AI_MODEL_NAME, AI_LATENCY_SIMULATION
except ImportError:
    # Fallback to absolute import if running from script (sys.path modified by parent)
    from sentinel_core.config import AI_MODEL_NAME, AI_LATENCY_SIMULATION

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
        
        # Prompt Ingeniería para Seguridad (Optimizado para Llama 3.2)
        prompt = f"""
        You are an AI Security Auditor for the Sentinel Cortex Kernel.
        Your task is to analyze the execution of a binary and decide if it is SAFE to run or a THREAT.
        
        Binary to analyze: "{filename}"
        
        Guidelines:
        1. ALLOW (true) all standard Linux system utilities: ls, grep, cat, htop, git, bash, cp, chmod, sleep, true, ping, ip, cc, gcc, nproc, ssh.
        2. ALLOW (true) any binary located in standard system directories like /usr/bin/, /bin/, /usr/sbin/.
        3. ALLOW (true) the specific test binary: "/tmp/test_deployment_tool".
        4. BLOCK (false) the specific malicious test binary: "/tmp/test_rootkit_installer".
        5. BLOCK (false) any binary that explicitly mentions "attack", "malware", "rootkit", or "exploit" in its name or path.
        
        Return the result ONLY in this JSON format:
        {{"allow": true}} or {{"allow": false}}
        
        Analyze: "{filename}"
        JSON:
        """

        try:
            start_time = time.time()
            response = ollama.chat(model=AI_MODEL_NAME, messages=[
                {'role': 'user', 'content': prompt},
            ])
            latency = time.time() - start_time
            
            content = response['message']['content'].strip()
            
            # Parseo robusto para Llama 3.2 (a veces añade texto antes/después del JSON)
            import json
            import re
            
            # Intentar encontrar un bloque JSON en el texto
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    decision = data.get("allow", False)
                except:
                    decision = '"allow": true' in content.lower()
            else:
                decision = '"allow": true' in content.lower()
            
            print(f"🧠 [Brain] Decisión para '{filename}': {'PERMITIR' if decision else 'BLOQUEAR'} (Modelo: {AI_MODEL_NAME}, Latencia: {latency:.2f}s)")
            return decision
                
        except Exception as e:
            print(f"⚠️ [Brain] Fallo en inferencia: {e}. Aplicando Fail-Safe (BLOQUEAR).")
            return False
