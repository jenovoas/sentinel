# tests/verify_snn_synapse.py
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import sys
import os

# Adjust path to find src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.sentinel_core.brain.snn_core import GeneticImmunitySystem
from src.core.sentinel_core.memory.chromadb_storage import memory_vault
import time

def test_synapse():
    print("🧠 [Test] Initializing Akashic Immunity System...")
    snn = GeneticImmunitySystem()
    
    # Stimulus 1: Low threat (Score 20)
    print("⚡ [Test] Injecting Low Threat (Score 20)...")
    # New API: process_stimulus(filename, score, residue)
    result = snn.process_stimulus("safe_process.sh", 20, 10) # Residue 10 (Composite)
    print(f"   -> Result: {result}")
    assert result == "LEAK", "Low threat should just leak"
    
    # Stimulus 2: High Threat (Score 95 - Anomaly)
    print("⚡ [Test] Injecting HIGH Threat (Score 95)...")
    # Score 95 -> Normalized ~1.9 -> Instant Spike (Threshold 1.2)
    result = snn.process_stimulus("malicious_child.sh", 95, 7) # Residue 7 (Prime)
    print(f"   -> Result: {result}")
    
    if result == "SPIKE":
        print("🧬 [Test] Spike confirmed. Checking persistence...")
        # Since process_stimulus in Phase 3 proof-of-concept doesn't actually call store_lineage
        # (it returns "SPIKE" and expects caller to store), we simulate storage here.
        
        lineage_id = memory_vault.store_lineage(
            child_pid=1234,
            parent_pid=5678,
            lineage_hash=hash("malicious_child.sh"),
            metadata={"test": "akashic_verification"}
        )
        print(f"✅ [Test] Lineage stored with ID: {lineage_id}")
        
        # Verify retrieval
        print("🔍 [Test] Verifying persistence...")
        coll = memory_vault.lineage_collection
        res = coll.get(ids=[lineage_id])
        if res['ids']:
            print("✅ [Test] Memory retrieval SUCCESS.")
        else:
            print("❌ [Test] Memory retrieval FAILED.")
    else:
        print("❌ [Test] High threat FAILED to trigger spike.")

if __name__ == "__main__":
    test_synapse()
