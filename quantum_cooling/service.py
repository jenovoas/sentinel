#!/usr/bin/env python3
"""
Quantum Cooling Service - Production Ready

Integrates Prometheus metrics with Quantum Cooling V2 for real-time buffer optimization.
"""

import time
import yaml
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent / 'research' / 'cosmic_patterns'))
from quantum_cooling_v2 import QuantumCoolingPredictorV2, BufferState
from prometheus_client import PrometheusClient, BufferMetrics


@dataclass
class Config:
    """Service configuration"""
    prometheus_url: str
    poll_interval: float  # seconds
    min_buffer_size: int
    max_buffer_size: int
    enable_auto_resize: bool
    log_level: str


class QuantumCoolingService:
    """
    Production service that runs Quantum Cooling continuously.
    
    Flow:
    1. Poll Prometheus for metrics
    2. Feed to Quantum Cooling predictor
    3. Get buffer size recommendation
    4. Apply resize (if enabled)
    5. Log results
    6. Repeat
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.prometheus = PrometheusClient(config.prometheus_url)
        self.predictor = QuantumCoolingPredictorV2()
        self.running = False
        
        # Stats
        self.total_predictions = 0
        self.total_resizes = 0
        self.total_drops_prevented = 0
        
    def start(self):
        """Start the service loop."""
        print("="*70)
        print("🧊⚛️ QUANTUM COOLING SERVICE - STARTING")
        print("="*70)
        print()
        print(f"Prometheus: {self.config.prometheus_url}")
        print(f"Poll interval: {self.config.poll_interval}s")
        print(f"Auto-resize: {self.config.enable_auto_resize}")
        print()
        
        # Health check
        if not self.prometheus.health_check():
            print("❌ Prometheus is not reachable!")
            print("   Make sure Prometheus is running")
            return
        
        print("✅ Prometheus is healthy")
        print()
        print("Starting quantum cooling loop...")
        print()
        
        self.running = True
        
        try:
            while self.running:
                self._process_cycle()
                time.sleep(self.config.poll_interval)
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down gracefully...")
            self.stop()
    
    def _process_cycle(self):
        """Process one cooling cycle."""
        # 1. Fetch metrics
        metrics = self.prometheus.get_current_metrics()
        
        if not metrics:
            print("⚠️  Could not fetch metrics, skipping cycle")
            return
        
        # 2. Convert to BufferState
        state = BufferState(
            size=metrics.buffer_size,
            utilization=metrics.utilization,
            drop_rate=metrics.drop_rate,
            timestamp=metrics.timestamp
        )
        
        # 3. Get prediction
        new_size, action = self.predictor.predict(state)
        self.total_predictions += 1
        
        # 4. Apply safety limits
        new_size = max(self.config.min_buffer_size, 
                      min(new_size, self.config.max_buffer_size))
        
        # 5. Log action
        if new_size != state.size:
            print(f"[{time.strftime('%H:%M:%S')}] {action}")
            
            if self.config.enable_auto_resize:
                self._apply_buffer_resize(new_size)
                self.total_resizes += 1
            else:
                print(f"          | Would resize to {new_size} (auto-resize disabled)")
        
        # 6. Update stats
        if metrics.drop_rate > 0:
            # Estimate drops prevented
            old_drops = metrics.drop_rate * self.config.poll_interval
            expansion_ratio = new_size / state.size if state.size > 0 else 1.0
            new_drops = old_drops / expansion_ratio
            drops_prevented = old_drops - new_drops
            self.total_drops_prevented += drops_prevented
    
    def _apply_buffer_resize(self, new_size: int):
        """
        Apply buffer resize via sysctl.
        
        NOTE: This requires root privileges.
        For production, use eBPF or proper kernel module.
        """
        try:
            # Example: resize network receive buffer
            # Adjust sysctl parameter to match your system
            import subprocess
            
            result = subprocess.run(
                ['sudo', 'sysctl', '-w', f'net.core.rmem_default={new_size}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"          | ✅ Buffer resized to {new_size}")
            else:
                print(f"          | ❌ Resize failed: {result.stderr}")
        
        except Exception as e:
            print(f"          | ❌ Resize error: {e}")
    
    def stop(self):
        """Stop the service."""
        self.running = False
        
        print()
        print("="*70)
        print("📊 QUANTUM COOLING SERVICE - STATS")
        print("="*70)
        print()
        print(f"Total predictions: {self.total_predictions}")
        print(f"Total resizes: {self.total_resizes}")
        print(f"Drops prevented (estimated): {self.total_drops_prevented:.0f}")
        print()
        print("Service stopped.")
        print()
    
    def get_stats(self) -> dict:
        """Get current service statistics."""
        return {
            'total_predictions': self.total_predictions,
            'total_resizes': self.total_resizes,
            'total_drops_prevented': self.total_drops_prevented,
            'running': self.running
        }


def load_config(config_file: str = 'config.yaml') -> Config:
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / config_file
    
    if not config_path.exists():
        # Default config
        return Config(
            prometheus_url='http://localhost:9090',
            poll_interval=1.0,
            min_buffer_size=512,
            max_buffer_size=16384,
            enable_auto_resize=False,  # Safe default
            log_level='INFO'
        )
    
    with open(config_path) as f:
        data = yaml.safe_load(f)
    
    return Config(**data)


def main():
    """Main entry point."""
    config = load_config()
    service = QuantumCoolingService(config)
    
    try:
        service.start()
    except Exception as e:
        print(f"❌ Service error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
