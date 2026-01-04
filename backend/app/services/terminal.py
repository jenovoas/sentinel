import os
import json
import logging
import subprocess
import shlex
import re
import httpx
from typing import Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TerminalResponse(BaseModel):
    success: bool
    output: str
    risk_score: float = 0.0
    reasoning: str = ""

class TerminalService:
    """
    Semantic Shell Service - Inspired by SemSH.
    Integrates AI risk analysis for system commands.
    """
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        self.strict_deny_patterns = [
            r"/etc/shadow", r"/etc/passwd", r"/root/.ssh",
            r"rm -rf /", r"mkfs", r"drop table", r"truncate"
        ]

    async def analyze_risk(self, command: str) -> Dict:
        """Analyze command risk using local LLM"""
        try:
            prompt = (
                f"Analista de Seguridad de Sistemas. Evalúa el siguiente comando de shell. "
                f"Responde SOLO en formato JSON: {{'risk_score': 0.X, 'reasoning': '...'}} "
                f"Donde risk_score es de 0.0 (seguro) a 1.0 (crítico). "
                f"Comando: '{command}'"
            )
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "format": "json",
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return json.loads(data.get("response", "{}"))
        except Exception as e:
            logger.warning(f"⚠️ Risk analysis failed: {e}")
        
        return {"risk_score": 0.5, "reasoning": "Error en análisis de IA. Precaución."}

    def is_deterministically_blocked(self, command: str) -> Optional[str]:
        """Check for strictly forbidden patterns"""
        for pattern in self.strict_deny_patterns:
            if re.search(pattern, command.lower()):
                return pattern
        return None

    async def execute(self, command: str, shell_type: str = "bash", user_role: str = "Unauthorized") -> TerminalResponse:
        """Execute command safely"""
        # 1. Deterministic block
        blocked_pattern = self.is_deterministically_blocked(command)
        if blocked_pattern:
            return TerminalResponse(
                success=False,
                output=f"🚫 BLOQUEO DETERMINISTA: El patrón '{blocked_pattern}' está prohibido.",
                risk_score=1.0,
                reasoning="Intento de acceso a archivos sensibles o comandos destructivos."
            )

        # 2. AI Risk Analysis
        analysis = await self.analyze_risk(command)
        risk = analysis.get("risk_score", 1.0)
        reasoning = analysis.get("reasoning", "")

        # 3. RBAC Enforcement
        risk_threshold = 0.8 if user_role == "Sovereign" else 0.3
        
        if risk > risk_threshold:
            return TerminalResponse(
                success=False,
                output=f"🚫 BLOQUEO POR RIESGO ({risk:.2f}): {reasoning}",
                risk_score=risk,
                reasoning=reasoning
            )

        # 4. Execution
        try:
            # Use specific shell if requested
            shell_cmd = command
            if shell_type == "zsh":
                shell_cmd = f"zsh -c {shlex.quote(command)}"
            
            # Use subprocess.run for simplicity in the API context
            # In production, consider streaming or long-running task management
            result = subprocess.run(
                shell_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30.0
            )
            
            output = result.stdout + result.stderr
            return TerminalResponse(
                success=result.returncode == 0,
                output=output if output else "Comando ejecutado sin salida.",
                risk_score=risk,
                reasoning=reasoning
            )
        except subprocess.TimeoutExpired:
            return TerminalResponse(
                success=False,
                output="⌛ Tiempo de espera agotado (30s).",
                risk_score=risk,
                reasoning="Comando de larga duración interrumpido."
            )
        except Exception as e:
            return TerminalResponse(
                success=False,
                output=f"❌ Error de ejecución: {str(e)}",
                risk_score=risk,
                reasoning=reasoning
            )
