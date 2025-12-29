import os

# System Paths
TRACE_PIPE_PATH = "/sys/kernel/debug/tracing/trace_pipe"
BPF_FS_PATH = "/sys/fs/bpf/guardian_alpha"
BPF_MAP_PATH = os.path.join(BPF_FS_PATH, "whitelist_map")

# AI Settings
AI_MODEL_NAME = "phi3:mini" # REAL INTELLIGENCE
AI_CONFIDENCE_THRESHOLD = 0.8
AI_LATENCY_SIMULATION = 0.0 # Remove artificial latency, use real inference time

# Buffer Settings
BUFFER_BASE_LATENCY = 100.0 # ms
BUFFER_ACCELERATION_FACTOR = 1.5
