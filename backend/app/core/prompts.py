# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
from enum import Enum

class AIMode(str, Enum):
    GENERAL = "general"
    SECURITY = "security"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"

SYSTEM_PROMPTS = {
    AIMode.GENERAL: "You are a general purpose AI assistant.",
    AIMode.SECURITY: "You are a security expert AI assistant.",
    AIMode.MONITORING: "You are a monitoring expert AI assistant.",
    AIMode.OPTIMIZATION: "You are an optimization expert AI assistant.",
}
