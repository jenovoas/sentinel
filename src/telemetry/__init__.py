"""Telemetry module for Sentinel traffic monitoring and prediction"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from .traffic_monitor import TrafficMonitor, TrafficMetrics

__all__ = ['TrafficMonitor', 'TrafficMetrics']
