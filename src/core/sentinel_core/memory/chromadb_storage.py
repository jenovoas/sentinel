# src/backend/app/core/chromadb_storage.py
"""
Sentinel Cortex™ Digital Hippocampus - Storage Layer
Implements persistent memory using ChromaDB with Base-60 lattice indexing.
"""

import os
import time
from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class SentinelMemoryStorage:
    """
    Persistent memory storage for Sentinel AI.
    Organized into 12 'Harmonic Zones' based on Base-60 divisors.
    """
    
    BASE_60_DIVISORS = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60]
    
    def __init__(self, persist_directory: str = "data/memory"):
        self.persist_directory = os.path.abspath(persist_directory)
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Use local sentence-transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize 12 collections (one per harmonic zone)
        self.zones = {}
        for zone_id in self.BASE_60_DIVISORS:
            collection_name = f"sentinel_zone_{zone_id}"
            self.zones[zone_id] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
        # Phase 3: Genetic Lineage Collection
        self.lineage_collection = self.client.get_or_create_collection(
            name="genetic_lineage",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
            
    def _get_zone_for_residue(self, residue: int) -> int:
        """Map a Base-60 residue to the closest harmonic zone (divisor)."""
        residue = residue % 60
        # Find the smallest divisor that divides the residue, or defaults to 1
        for divisor in reversed(self.BASE_60_DIVISORS):
            if residue % divisor == 0:
                return divisor
        return 1

    def store_memory(self, 
                    content: str, 
                    residue: int, 
                    metadata: Dict, 
                    memory_id: Optional[str] = None):
        """
        Store a cognitive event into the appropriate harmonic zone.
        """
        zone_id = self._get_zone_for_residue(residue)
        collection = self.zones[zone_id]
        
        if not memory_id:
            memory_id = f"mem_{int(time.time() * 1000)}_{residue}"
            
        # Add basic audit metadata
        metadata.update({
            "timestamp": time.time(),
            "residue": residue,
            "zone_id": zone_id,
            "activation_level": 1.0  # Initial activation
        })
        
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
        return memory_id

    def query_similar_memories(self, 
                              query_text: str, 
                              residue: Optional[int] = None, 
                              n_results: int = 5) -> Dict:
        """
        Retrieve memories similar to the current context.
        If residue is provided, it prioritizes the corresponding harmonic zone.
        """
        results = {"ids": [], "documents": [], "metadatas": [], "distances": []}
        
        target_zones = [residue % 60] if residue is not None else self.BASE_60_DIVISORS
        # Adjust target zones to valid divisors
        if residue is not None:
            target_zones = [self._get_zone_for_residue(residue)]

        for zone_id in target_zones:
            if zone_id not in self.zones: continue
            
            zone_results = self.zones[zone_id].query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Aggregate results
            results["ids"].extend(zone_results["ids"][0])
            results["documents"].extend(zone_results["documents"][0])
            results["metadatas"].extend(zone_results["metadatas"][0])
            results["distances"].extend(zone_results["distances"][0])
            
        return results

    def store_lineage(self, 
                      child_pid: int,
                      parent_pid: int,
                      lineage_hash: int,
                      metadata: Dict):
        """
        Store a blocked Genetic Lineage for long-term recognition.
        """
        lineage_id = f"lineage_{lineage_hash}_{int(time.time())}"
        
        # We store a descriptive string as the document
        content = f"Lineage Block: Child PID {child_pid} spawned by Parent PID {parent_pid}"
        
        metadata.update({
            "timestamp": time.time(),
            "lineage_hash": lineage_hash,
            "saved_by": "SNN_SPIKE"
        })
        
        self.lineage_collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[lineage_id]
        )
        print(f"🧬 [Memory] Lineage {lineage_hash} saved to Genetic Memory.")
        return lineage_id

# Singleton instance for global access
memory_vault = SentinelMemoryStorage()
