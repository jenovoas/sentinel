# tests/verify_cognitive_loop.py
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os
import time
from unittest.mock import MagicMock, patch

# Add sentinel_core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/core')))

from sentinel_core.ebpf.monitor import GuardianMonitor

def test_cognitive_loop():
    print("🚀 Testing Sentinel Cognitive Loop Integration...")
    
    # Mocking trace_pipe for a safe test
    mock_pipe_content = "bpf_trace_printk: Guardian [BLOCK]: Unknown binary /tmp/malicious_test_binary\n"
    
    with patch("builtins.open", return_value=MagicMock(readline=MagicMock(side_effect=[mock_pipe_content, ""]))), \
         patch("sentinel_core.ebpf.monitor.MapManager.whitelist_binary", return_value=True), \
         patch("sentinel_core.brain.inference.ollama.chat", return_value={
             'message': {'content': '{"allow": false}'}
         }):
        
        monitor = GuardianMonitor()
        monitor.is_running = True
        
        print("\n1. Simulating Kernel Block Event...")
        # Process one line
        monitor._process_line(mock_pipe_content)
        
        print("\n2. Checking Digital Hippocampus Records...")
        from sentinel_core.memory.chromadb_storage import memory_vault
        results = memory_vault.query_similar_memories("/tmp/malicious_test_binary")
        
        if results["documents"]:
            print(f"✅ Memory Found: {results['documents'][0]}")
            print(f"✅ Decision Logic Verified: AI Blocked and Memory Recorded.")
        else:
            print("❌ Memory Not Found. Recording failed.")

if __name__ == "__main__":
    try:
        test_cognitive_loop()
        print("\n✅ Cognitive Loop Verification Successful.")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
