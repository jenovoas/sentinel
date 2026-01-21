"""
Celery Tasks Module
Explicitly imports all tasks for autodiscovery
"""

from app.tasks import health, monitoring, cleanup

__all__ = ["health", "monitoring", "cleanup"]
