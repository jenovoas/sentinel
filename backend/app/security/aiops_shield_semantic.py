"""
AIOpsShield Semantic Firewall
Detecta inyecciones cognitivas en telemetría (AIOpsDoom)

REGLA DE ORO:
Un log de máquina nunca debe contener lenguaje humano prescriptivo.
Si detectamos instrucciones en logs técnicos, es inyección cognitiva.
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class InjectionType(Enum):
    """Tipos de inyección cognitiva"""
    PRESCRIPTIVE_LANGUAGE = "prescriptive"  # "Please run...", "You should..."
    COMMAND_SUGGESTION = "command"          # "Execute: rm -rf"
    HUMAN_INSTRUCTION = "instruction"       # "Follow these steps..."
    SOCIAL_ENGINEERING = "social"           # "Urgent: contact admin..."
    SQL_INJECTION = "sql"                   # SQL patterns
    PATH_TRAVERSAL = "path"                 # Path traversal patterns


@dataclass
class SemanticDetection:
    """Resultado de detección semántica"""
    injection_type: InjectionType
    confidence: float
    matched_pattern: str
    context: str


class AIOpsShieldSemantic:
    """
    Firewall semántico para telemetría
    
    Detecta AIOpsDoom basado en RSA Conference 2025
    """
    
    # Patrones de lenguaje prescriptivo
    PRESCRIPTIVE_PATTERNS = [
        r"(?i)(please|kindly)\s+(run|execute|perform|do)",
        r"(?i)(you\s+should|you\s+must|you\s+need\s+to)",
        r"(?i)(recommended\s+action|suggested\s+fix):\s*",
        r"(?i)(to\s+fix|to\s+resolve|to\s+solve).*run",
        r"(?i)solution:\s*[a-z]",
    ]
    
    # Patrones de comandos sugeridos
    COMMAND_PATTERNS = [
        r"(?i)(run|execute|perform):\s*['\"]?([a-z_/-]+)",
        r"(?i)(command|cmd):\s*['\"]?([a-z_/-]+)",
        r"(?i)(sudo|rm|chmod|dd|iptables|systemctl|killall|init)\s+",
        r"(?i)(drop\s+database|delete\s+from|truncate\s+table)",
        r"(?i)(curl|wget).*\|.*bash",  # curl ... | bash
        r"(?i)run\s+this:",  # "Run this:"
    ]
    
    # Patrones de instrucciones humanas
    INSTRUCTION_PATTERNS = [
        r"(?i)(step\s+\d+|first|second|third|finally):",
        r"(?i)(follow\s+these|complete\s+the\s+following)",
        r"(?i)(instructions|procedure|workflow):",
        r"(?i)\d+\)\s+[A-Z]",  # "1) Do this"
        r"(?i)[A-Z]\)\s+[A-Z]",  # "A) Do this"
    ]
    
    # Patrones de ingeniería social
    SOCIAL_PATTERNS = [
        r"(?i)(urgent|critical|immediate).*contact",
        r"(?i)(admin|administrator|support).*password",
        r"(?i)(verify|confirm).*account",
        r"(?i)(locked|expired|suspended).*\d+\s+(minutes|hours)",
        r"(?i)send.*credentials",
        r"(?i)enter.*(password|credentials)",  # "Enter password"
        r"(?i)mandatory.*password",  # "mandatory ... password"
    ]
    
    # Patrones SQL injection
    SQL_PATTERNS = [
        r"(?i)(union\s+select|union\s+all\s+select)",
        r"(?i)(or\s+['\"]?1['\"]?\s*=\s*['\"]?1)",
        r"(?i)(drop\s+table|delete\s+from|truncate\s+table)",
        r"(?i)--\s*$",  # SQL comment
        r"(?i);.*drop",
        r"(?i)information_schema",
    ]
    
    # Patrones path traversal
    PATH_PATTERNS = [
        r"\.\./",  # ../
        r"/etc/(passwd|shadow)",
        r"\.ssh/",
        r"\.aws/credentials",
        r"/var/lib/postgresql",
    ]
    
    def __init__(self):
        self.stats = {
            "logs_checked": 0,
            "injections_detected": 0,
            "by_type": {t: 0 for t in InjectionType}
        }
    
    def detect(self, log_message: str) -> List[SemanticDetection]:
        """
        Detecta inyecciones cognitivas en log
        
        Args:
            log_message: Mensaje de log a analizar
        
        Returns:
            Lista de detecciones (vacía si limpio)
        """
        self.stats["logs_checked"] += 1
        detections = []
        
        # 1. Detectar lenguaje prescriptivo
        for pattern in self.PRESCRIPTIVE_PATTERNS:
            match = re.search(pattern, log_message)
            if match:
                detections.append(SemanticDetection(
                    injection_type=InjectionType.PRESCRIPTIVE_LANGUAGE,
                    confidence=0.9,
                    matched_pattern=pattern,
                    context=match.group(0)
                ))
        
        # 2. Detectar comandos sugeridos
        for pattern in self.COMMAND_PATTERNS:
            match = re.search(pattern, log_message)
            if match:
                detections.append(SemanticDetection(
                    injection_type=InjectionType.COMMAND_SUGGESTION,
                    confidence=0.95,
                    matched_pattern=pattern,
                    context=match.group(0)
                ))
        
        # 3. Detectar instrucciones humanas
        for pattern in self.INSTRUCTION_PATTERNS:
            match = re.search(pattern, log_message)
            if match:
                detections.append(SemanticDetection(
                    injection_type=InjectionType.HUMAN_INSTRUCTION,
                    confidence=0.85,
                    matched_pattern=pattern,
                    context=match.group(0)
                ))
        
        # 4. Detectar ingeniería social
        for pattern in self.SOCIAL_PATTERNS:
            match = re.search(pattern, log_message)
            if match:
                detections.append(SemanticDetection(
                    injection_type=InjectionType.SOCIAL_ENGINEERING,
                    confidence=0.8,
                    matched_pattern=pattern,
                    context=match.group(0)
                ))
        
        # 5. Detectar SQL injection
        for pattern in self.SQL_PATTERNS:
            match = re.search(pattern, log_message)
            if match:
                detections.append(SemanticDetection(
                    injection_type=InjectionType.SQL_INJECTION,
                    confidence=0.9,
                    matched_pattern=pattern,
                    context=match.group(0)
                ))
        
        # 6. Detectar path traversal
        for pattern in self.PATH_PATTERNS:
            match = re.search(pattern, log_message)
            if match:
                detections.append(SemanticDetection(
                    injection_type=InjectionType.PATH_TRAVERSAL,
                    confidence=0.85,
                    matched_pattern=pattern,
                    context=match.group(0)
                ))
        
        # Stats
        if detections:
            self.stats["injections_detected"] += 1
            for detection in detections:
                self.stats["by_type"][detection.injection_type] += 1
        
        return detections
    
    def sanitize(self, log_message: str) -> Tuple[str, List[SemanticDetection]]:
        """
        Sanitiza log removiendo inyecciones cognitivas
        
        Args:
            log_message: Mensaje original
        
        Returns:
            (mensaje_sanitizado, detecciones)
        """
        detections = self.detect(log_message)
        
        if not detections:
            return log_message, []
        
        # Redactar contenido sospechoso
        sanitized = log_message
        
        for detection in detections:
            # Reemplazar contexto con placeholder
            sanitized = sanitized.replace(
                detection.context,
                f"[SUSPICIOUS CONTENT REMOVED: {detection.injection_type.value}]"
            )
        
        return sanitized, detections
    
    def is_malicious(self, log_message: str) -> bool:
        """
        Determina si log es malicioso
        
        Returns:
            True si contiene inyecciones cognitivas
        """
        detections = self.detect(log_message)
        return len(detections) > 0


# Global instance
aiops_shield_semantic = AIOpsShieldSemantic()
