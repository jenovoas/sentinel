#!/usr/bin/env python3
"""
Sentinel Knowledge Base Indexer
Indexes all technical documentation into ChromaDB for RAG retrieval.
This ensures the AI always has full context about Sentinel's architecture.
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import sys
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

SENTINEL_ROOT = Path("/home/jnovoas/sentinel")
CHROMA_PATH = SENTINEL_ROOT / ".chroma_db"

# Directories to index
DOCS_DIRS = [
    SENTINEL_ROOT / "docs",
    SENTINEL_ROOT / "research",
    SENTINEL_ROOT / "guardian-alpha",
    SENTINEL_ROOT / "quantum",
]

# File patterns to index
PATTERNS = ["*.md", "*.py", "*.rs", "*.sh", "*.yaml", "*.json", "*.toml"]

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better retrieval"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks

def index_file(file_path: Path, collection) -> int:
    """Index a single file into ChromaDB"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Skip empty files
        if len(content.strip()) < 50:
            return 0
        
        # Create chunks
        chunks = chunk_text(content)
        
        # Prepare metadata
        rel_path = str(file_path.relative_to(SENTINEL_ROOT))
        
        # Add to collection
        for i, chunk in enumerate(chunks):
            doc_id = f"{rel_path}::chunk_{i}"
            
            collection.add(
                documents=[chunk],
                metadatas=[{
                    "source": rel_path,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "file_type": file_path.suffix,
                }],
                ids=[doc_id]
            )
        
        return len(chunks)
    
    except Exception as e:
        print(f"⚠️  Error indexing {file_path}: {e}")
        return 0

def main():
    print("🧠 Sentinel Knowledge Base Indexer")
    print("=" * 60)
    
    # Initialize ChromaDB
    print(f"📂 Initializing ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Create or get collection
    try:
        collection = client.get_collection("sentinel_knowledge")
        print("🗑️  Deleting existing collection...")
        client.delete_collection("sentinel_knowledge")
    except:
        pass
    
    collection = client.create_collection(
        name="sentinel_knowledge",
        metadata={"description": "Sentinel technical documentation and code"}
    )
    
    # Index all files
    total_files = 0
    total_chunks = 0
    
    for docs_dir in DOCS_DIRS:
        if not docs_dir.exists():
            print(f"⚠️  Skipping {docs_dir} (not found)")
            continue
        
        print(f"\n📖 Indexing {docs_dir.name}/...")
        
        for pattern in PATTERNS:
            for file_path in docs_dir.rglob(pattern):
                # Skip hidden files and __pycache__
                if any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
                    continue
                
                chunks = index_file(file_path, collection)
                if chunks > 0:
                    total_files += 1
                    total_chunks += chunks
                    print(f"  ✓ {file_path.name} ({chunks} chunks)")
    
    print("\n" + "=" * 60)
    print(f"✅ Indexing complete!")
    print(f"   Files indexed: {total_files}")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Database: {CHROMA_PATH}")
    print("\n💡 The AI now has full context about Sentinel's architecture.")

if __name__ == "__main__":
    main()
