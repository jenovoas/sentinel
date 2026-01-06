from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os

# System Paths
TRACE_PIPE_PATH = "/sys/kernel/debug/tracing/trace_pipe"
BPF_FS_PATH = "/sys/fs/bpf/guardian_alpha"
BPF_MAP_PATH = os.path.join(BPF_FS_PATH, "whitelist_map")

# AI Configuration
AI_MODEL_NAME = "llama3.2:3b"  # Switched to Llama 3.2 for better reasoning
AI_CONFIDENCE_THRESHOLD = 0.8
AI_LATENCY_SIMULATION = S60(0, 0, 0) # Remove artificial latency, use real inference time

# Buffer Settings
BUFFER_BASE_LATENCY = 100.0 # ms
BUFFER_ACCELERATION_FACTOR = 1.5
