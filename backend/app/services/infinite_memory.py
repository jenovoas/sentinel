"""
Infinite Memory System for Sentinel TUI
Implements hierarchical memory compression to maintain unlimited conversation history.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings


class InfiniteMemory:
    """
    Hierarchical memory system with automatic compression.
    
    Architecture:
    - Working Memory: Last 50 messages (full detail)
    - Short-term Memory: Last 500 messages (compressed summaries)
    - Long-term Memory: All history (ChromaDB semantic search)
    """
    
    def __init__(self, user_id: str = "jnovoas"):
        self.user_id = user_id
        self.working_memory: List[Dict] = []
        self.short_term_memory: List[Dict] = []
        
        # Initialize ChromaDB for long-term memory
        chroma_path = Path("/home/jnovoas/sentinel/.chroma_db")
        self.chroma_client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create conversation memory collection
        try:
            self.memory_collection = self.chroma_client.get_collection("conversation_memory")
        except:
            self.memory_collection = self.chroma_client.create_collection(
                name="conversation_memory",
                metadata={"description": "Long-term conversation memory"}
            )
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to working memory with automatic compression"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.working_memory.append(message)
        
        # Compress when working memory exceeds 50 messages
        if len(self.working_memory) > 50:
            self._compress_to_short_term()
        
        # Archive when short-term exceeds 500 messages
        if len(self.short_term_memory) > 500:
            self._archive_to_long_term()
    
    def _compress_to_short_term(self):
        """Compress oldest working memory messages to short-term"""
        # Take oldest 10 messages
        to_compress = self.working_memory[:10]
        self.working_memory = self.working_memory[10:]
        
        # Create compressed summary
        summary = self._create_summary(to_compress)
        
        self.short_term_memory.append({
            "type": "summary",
            "messages_count": len(to_compress),
            "summary": summary,
            "timestamp_range": (
                to_compress[0]["timestamp"],
                to_compress[-1]["timestamp"]
            )
        })
    
    def _archive_to_long_term(self):
        """Archive short-term memory to ChromaDB"""
        for item in self.short_term_memory[:100]:
            doc_id = f"{self.user_id}::{item['timestamp_range'][0]}"
            
            self.memory_collection.add(
                documents=[item["summary"]],
                metadatas=[{
                    "user_id": self.user_id,
                    "message_count": item["messages_count"],
                    "start_time": item["timestamp_range"][0],
                    "end_time": item["timestamp_range"][1]
                }],
                ids=[doc_id]
            )
        
        # Remove archived items
        self.short_term_memory = self.short_term_memory[100:]
    
    def _create_summary(self, messages: List[Dict]) -> str:
        """Create intelligent summary of message batch"""
        # Extract key information
        user_queries = [m["content"] for m in messages if m["role"] == "user"]
        ai_responses = [m["content"] for m in messages if m["role"] == "assistant"]
        
        # Simple summary (in production, use LLM for better compression)
        summary = f"Conversation segment ({len(messages)} messages):\n"
        
        if user_queries:
            summary += f"User topics: {', '.join(user_queries[:3])}\n"
        
        if ai_responses:
            # Extract key actions (SEARCH, WRITE, EXECUTE)
            actions = []
            for resp in ai_responses:
                if "[SEARCH:" in resp:
                    actions.append("searched")
                if "[WRITE:" in resp:
                    actions.append("wrote files")
                if "[EXECUTE:" in resp:
                    actions.append("executed commands")
            
            if actions:
                summary += f"Actions: {', '.join(set(actions))}"
        
        return summary
    
    def get_context(self, query: Optional[str] = None, max_messages: int = 50) -> str:
        """
        Get relevant context for current query.
        
        Returns:
        - All working memory (last 50 messages)
        - Relevant short-term summaries
        - Semantic search results from long-term memory (if query provided)
        """
        context_parts = []
        
        # 1. Working memory (always included)
        for msg in self.working_memory[-max_messages:]:
            context_parts.append(f"{msg['role'].upper()}: {msg['content']}")
        
        # 2. Recent short-term summaries
        if self.short_term_memory:
            context_parts.insert(0, "\n[RECENT HISTORY SUMMARY]")
            for summary in self.short_term_memory[-5:]:
                context_parts.insert(1, summary["summary"])
        
        # 3. Semantic search in long-term memory
        if query and len(query) > 10:
            try:
                results = self.memory_collection.query(
                    query_texts=[query],
                    n_results=3
                )
                
                if results["documents"] and results["documents"][0]:
                    context_parts.insert(0, "\n[RELEVANT PAST CONVERSATIONS]")
                    for doc in results["documents"][0]:
                        context_parts.insert(1, doc)
            except:
                pass
        
        return "\n\n".join(context_parts)
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            "working_memory": len(self.working_memory),
            "short_term_memory": len(self.short_term_memory),
            "long_term_entries": self.memory_collection.count(),
            "total_messages_tracked": (
                len(self.working_memory) +
                sum(item["messages_count"] for item in self.short_term_memory)
            )
        }
