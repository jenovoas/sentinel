from enum import Enum

class AIMode(str, Enum):
    GENERAL = "general"
    SECURITY = "security"
    OPTIMIZATION = "optimization"

SYSTEM_PROMPTS = {
    AIMode.GENERAL: "You are a helpful assistant.",
    AIMode.SECURITY: "You are a security expert.",
    AIMode.OPTIMIZATION: "You are an optimization expert.",
}
