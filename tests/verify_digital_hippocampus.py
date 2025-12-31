# tests/verify_digital_hippocampus.py
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/backend')))

from app.core.chromadb_storage import memory_vault
from app.core.ca1_selector import memory_selector

def test_storage():
    print("Testing ChromaDB Storage...")
    content = "Test incident: Unauthorized sudo attempt on /etc/shadow"
    residue = 0  # Prime zone
    metadata = {"type": "security_alert", "severity": "high"}
    
    mem_id = memory_vault.store_memory(content, residue, metadata)
    print(f"Stored memory ID: {mem_id}")
    
    print("Querying similar memories...")
    results = memory_vault.query_similar_memories("sudo attempt", residue=0)
    print(f"Found {len(results['documents'])} results.")
    for doc, meta in zip(results['documents'], results['metadatas']):
        print(f" - [{meta['zone_id']}] {doc}")

if __name__ == "__main__":
    try:
        test_storage()
        print("\n✅ Digital Hippocampus Storage Verified.")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
