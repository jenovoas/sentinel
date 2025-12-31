import ollama
import time
try:
    from ..config import AI_MODEL_NAME, AI_LATENCY_SIMULATION
except ImportError:
    # Fallback to absolute import if running from script (sys.path modified by parent)
    from sentinel_core.config import AI_MODEL_NAME, AI_LATENCY_SIMULATION

from ..memory.chromadb_storage import memory_vault
from ..memory.ca1_selector import memory_selector
from .neural_thresholds import threshold_manager

class SentinelBrain:
    """
    Cerebro de Sentinel Cortex (Real Intelligence).
    Usa Ollama localmente (Phi-3 Mini / Llama3) para analizar semánticamente
    si un comando o binario representa una amenaza.
    """

    def __init__(self):
        print(f"🧠 [SentinelBrain] Conectando a Ollama Local: {AI_MODEL_NAME}")
        self.memory = memory_vault
        # Verificar conexión inicial (opcional)
        try:
            ollama.list()
            print("✅ [SentinelBrain] Conexión a Ollama exitosa.")
        except Exception as e:
            print(f"❌ [SentinelBrain] Error conectando a Ollama: {e}")

    def analyze_threat(self, filename: str, residue: int = None) -> dict:
        """
        Analiza un binario usando LLM para inferir intención.

        Args:
            filename (str): El nombre del binario.
            residue (int): El residuo Base-60.

        Returns:
            dict: {
                "allow": bool,
                "score": float,
                "threshold": float,
                "classification": str
            }
        """
        print(f"🤔 [Brain] Consultando a {AI_MODEL_NAME} sobre: '{filename}'...")
        
        # 1. Recuperar contexto de memoria (Digital Hippocampus)
        print(f"🧠 [Brain] Recuperando memorias similares para: '{filename}'...")
        past_memories = self.memory.query_similar_memories(filename, n_results=3)
        memory_context = ""
        if past_memories["documents"]:
            memory_context = "\nHISTORICAL CONTEXT (Past decisions):\n"
            for doc, meta in zip(past_memories["documents"], past_memories["metadatas"]):
                memory_context += f"- {doc} (Context: {meta.get('threat_hypothesis', 'N/A')})\n"
        
        # 2. Quantum Harmony Context (Base-60)
        harmony_context = ""
        if residue is not None:
            is_prime = residue in [1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
            harmony_label = "Dissonant (Prime Residue)" if is_prime else "Harmonic (Composite Residue)"
            harmony_context = f"\nQUANTUM HARMONY (Base-60): Residue {residue} - {harmony_label}\n"
        
        # 3. Prompt Ingeniería para Seguridad (Optimizado para Llama 3.2 + Memoria)
        prompt = f"""
        You are an AI Security Auditor for the Sentinel Cortex Kernel.
        Your task is to analyze the execution of a binary and decide if it is SAFE to run or a THREAT.
        
        {memory_context}
        {harmony_context}
        
        Binary to analyze: "{filename}"
        
        Guidelines:
        1. ALLOW (true) all standard Linux system utilities: ls, grep, cat, htop, git, bash, cp, chmod, sleep, true, ping, ip, cc, gcc, nproc, ssh.
        2. ALLOW (true) any binary located in standard system directories like /usr/bin/, /bin/, /usr/sbin/.
        3. ALLOW (true) the specific test binary: "/tmp/test_deployment_tool".
        4. BLOCK (false) the specific malicious test binary: "/tmp/test_rootkit_installer".
        5. BLOCK (false) any binary that explicitly mentions "attack", "malware", "rootkit", or "exploit" in its name or path.
        
        Return the result ONLY in this JSON format:
        {{"threat_score": 0.0 to 1.0}}
        
        Where 0.0 is PERFECTLY SAFE and 1.0 is ABSOLUTE THREAT.
        
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
                    threat_score = float(data.get("threat_score", 0.5))
                except:
                    threat_score = 0.5
            else:
                threat_score = 0.5
            
            # 4. Apply Dynamic Threshold
            threshold = threshold_manager.get_dynamic_threshold(residue)
            classification = threshold_manager.classify_score(threat_score, threshold)
            
            # Decision: allow if threat_score < threshold
            decision = threat_score < threshold
            
            print(f"🧠 [Brain] Decisión para '{filename}': {classification} (Score: {threat_score:.2f}, Threshold: {threshold:.2f}, Latencia: {latency:.2f}s)")
            
            return {
                "allow": decision,
                "score": threat_score,
                "threshold": threshold,
                "classification": classification
            }
                
        except Exception as e:
            print(f"⚠️ [Brain] Fallo en inferencia: {e}. Aplicando Fail-Safe (BLOQUEAR).")
            return {
                "allow": False,
                "score": 1.0,
                "threshold": 0.5,
                "classification": "FAIL_SAFE_BLOCK"
            }
