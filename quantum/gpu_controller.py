#!/usr/bin/env python3
# 🛡️ YATRA LOCKED: BASE-60 ONLY 🛡️
# -----------------------------------------------------------------------------
# GPU CONTROLLER (HYBRID ADAPTIVE LATENCY)
# -----------------------------------------------------------------------------
# Implements Control Logic from BUFFER_CONTROL_PATTERN.md
# Law: Buffer = Base + K * (Throughput - Baseline)
# Adapted for GPU Batch Size:
# BatchSize = Min + K * Load
# -----------------------------------------------------------------------------

import time
import os
import sys

sys.path.append(os.getcwd())

# Import legacy wisdom if needed, but we implement clean logic here.
from quantum.yatra_core import S60

class GPUController:
    # Constants from Legacy Analysis
    K_GAIN = 0.1610  # Gain factor
    BASELINE_MS = 20.0 # Target frame time (50fps)
    
    def __init__(self):
        self.current_batch_size = 1000 # Start safe
        self.min_batch = 100
        self.max_batch = 65536 # 16-bit phase max
        self.history_latency = []
        
        print(f"🎮 GPU Controller Online | Target Latency: {self.BASELINE_MS}ms")

    def adjust_batch_size(self, latency_ms: float):
        """
        Adjusts batch size based on observed latency.
        proportional control: P-Controller
        """
        # Error = Target - Actual
        # If Latency is HIGH (Actual > Target), Error is NEGATIVE.
        # We need to REDUCE load.
        
        # But wait, Legacy Analysis said:
        # "Alta latencia -> Aumentar buffers (más batch reduce overhead)"
        # This is counter-intuitive for GPU Compute but true for IO.
        # For GPU Compute: Larger Batch = High Latency per Batch but High Throughput.
        # Smaller Batch = Low Latency per Batch but Lower Throughput (overhead).
        
        # We want to maintain 20ms cycles for "Real Time" feel (Fluidity).
        # If latency > 20ms, the batch is too big for the GPU to process in real-time frame.
        # So we should REDUCE batch size to keep frame rate high.
        
        # Wait, the BUFFER_CONTROL_PATTERN says:
        # "Alta latencia -> Aumentar buffers" (para absorber picos I/O).
        # "Baja latencia -> Reducir buffers" (ahorrar memoria).
        
        # Our "Fluid Diffusion" is a COMPUTE task, not just I/O.
        # If we take too long, we block the main thread (if sync).
        
        # Let's apply a simple Latency Target logic:
        # Latency ~ k * BatchSize
        # NewBatch = OldBatch * (Target / Actual)
        
        scale_factor = self.BASELINE_MS / (latency_ms + 0.1) # Avoid div0
        
        # Clamp reaction (avoid oscillation)
        scale_factor = max(0.5, min(1.5, scale_factor))
        
        new_batch = int(self.current_batch_size * scale_factor)
        new_batch = max(self.min_batch, min(self.max_batch, new_batch))
        
        self.current_batch_size = new_batch
        
        self.history_latency.append(latency_ms)
        if len(self.history_latency) > 100: self.history_latency.pop(0)

    def get_optimal_batch(self) -> int:
        return self.current_batch_size

    def report_status(self):
        avg = sum(self.history_latency) / max(1, len(self.history_latency))
        print(f"🎮 GPU Status: Batch={self.current_batch_size} | Avg Latency={avg:.2f}ms")

# Singleton
gpu_controller = GPUController()
