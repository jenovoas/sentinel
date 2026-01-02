#!/usr/bin/env python3
"""
Sentinel Digital Hippocampus Initializer
Sets up the vector database for first-run.
"""
import chromadb
from pathlib import Path

def init():
    db_path = Path("/home/jnovoas/sentinel/db/chroma")
    db_path.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(db_path))
    collection = client.get_or_create_collection(name="sentinel_events")
    
    print(f"✅ ChromaDB Initialized at {db_path}")
    print(f"📁 Collection 'sentinel_events' ready.")

if __name__ == "__main__":
    init()
