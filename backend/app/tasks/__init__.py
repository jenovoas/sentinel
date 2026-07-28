# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Celery Tasks Module
Explicitly imports all tasks for autodiscovery
"""

from app.tasks import health, monitoring, cleanup

__all__ = ["health", "monitoring", "cleanup"]
