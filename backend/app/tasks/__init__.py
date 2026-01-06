"""
Celery Tasks Module
Explicitly imports all tasks for autodiscovery
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from app.tasks import health, monitoring, cleanup

__all__ = ["health", "monitoring", "cleanup"]
