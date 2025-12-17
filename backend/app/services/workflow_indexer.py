#!/usr/bin/env python3
"""
Workflow Indexer Service
Analyzes and indexes n8n workflows for semantic search.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class WorkflowMetadata:
    """Metadata extracted from workflow."""
    id: str
    name: str
    description: str
    source: str  # 'djeknet', 'danitilahun', etc
    category: str  # 'security', 'automation', etc
    use_case: str  # 'incident_response', 'monitoring', etc
    complexity: int  # node count
    node_types: List[str]
    has_webhook: bool
    has_http: bool
    has_database: bool
    has_notification: bool


class WorkflowIndexer:
    """Indexes n8n workflows for RAG/RIG queries."""
    
    def __init__(self):
        self.security_keywords = [
            'security', 'incident', 'alert', 'threat',
            'monitoring', 'detection', 'response', 'phishing',
            'malware', 'vulnerability', 'breach'
        ]
        
        self.automation_keywords = [
            'automation', 'workflow', 'process', 'task',
            'schedule', 'trigger', 'webhook'
        ]
        
        self.notification_nodes = [
            'n8n-nodes-base.slack',
            'n8n-nodes-base.discord',
            'n8n-nodes-base.email',
            'n8n-nodes-base.telegram'
        ]
        
        self.database_nodes = [
            'n8n-nodes-base.postgres',
            'n8n-nodes-base.mysql',
            'n8n-nodes-base.mongodb',
            'n8n-nodes-base.airtable'
        ]
    
    def analyze_workflow(self, workflow_json: dict, source: str = 'unknown') -> Optional[WorkflowMetadata]:
        """Extract metadata from workflow."""
        try:
            name = workflow_json.get('name', 'Unnamed')
            description = workflow_json.get('meta', {}).get('description', '')
            nodes = workflow_json.get('nodes', [])
            
            # Extract node types
            node_types = [node.get('type', '') for node in nodes]
            
            # Categorize
            category = self._categorize_workflow(name, description, node_types)
            use_case = self._determine_use_case(name, description, node_types)
            
            # Analyze nodes
            has_webhook = any('webhook' in nt.lower() for nt in node_types)
            has_http = any('http' in nt.lower() for nt in node_types)
            has_database = any(nt in self.database_nodes for nt in node_types)
            has_notification = any(nt in self.notification_nodes for nt in node_types)
            
            return WorkflowMetadata(
                id=workflow_json.get('id', ''),
                name=name,
                description=description,
                source=source,
                category=category,
                use_case=use_case,
                complexity=len(nodes),
                node_types=node_types,
                has_webhook=has_webhook,
                has_http=has_http,
                has_database=has_database,
                has_notification=has_notification
            )
        except Exception as e:
            print(f"Error analyzing workflow: {e}")
            return None
    
    def _categorize_workflow(self, name: str, description: str, node_types: List[str]) -> str:
        """Categorize workflow by content."""
        text = f"{name} {description}".lower()
        
        # Security category
        if any(kw in text for kw in self.security_keywords):
            return 'security'
        
        # Automation category
        if any(kw in text for kw in self.automation_keywords):
            return 'automation'
        
        # AI/LLM category
        if any(kw in text for kw in ['openai', 'gpt', 'ai', 'llm', 'anthropic']):
            return 'ai_llm'
        
        # Communication category
        if any(nt in self.notification_nodes for nt in node_types):
            return 'communication'
        
        # Database category
        if any(nt in self.database_nodes for nt in node_types):
            return 'database'
        
        return 'other'
    
    def _determine_use_case(self, name: str, description: str, node_types: List[str]) -> str:
        """Determine primary use case."""
        text = f"{name} {description}".lower()
        
        if any(kw in text for kw in ['incident', 'response', 'alert']):
            return 'incident_response'
        
        if any(kw in text for kw in ['monitor', 'detect', 'scan']):
            return 'monitoring'
        
        if any(kw in text for kw in ['threat', 'vulnerability', 'security']):
            return 'threat_intelligence'
        
        if any(kw in text for kw in ['compliance', 'audit', 'report']):
            return 'compliance'
        
        if 'webhook' in [nt.lower() for nt in node_types]:
            return 'event_automation'
        
        if 'schedule' in [nt.lower() for nt in node_types]:
            return 'scheduled_task'
        
        return 'general_automation'
    
    def score_workflow(self, metadata: WorkflowMetadata) -> int:
        """Score workflow for Sentinel relevance (0-100)."""
        score = 0
        
        # Category scoring
        category_scores = {
            'security': 30,
            'automation': 20,
            'ai_llm': 15,
            'communication': 10,
            'database': 10,
            'other': 5
        }
        score += category_scores.get(metadata.category, 0)
        
        # Use case scoring
        use_case_scores = {
            'incident_response': 25,
            'monitoring': 20,
            'threat_intelligence': 20,
            'compliance': 15,
            'event_automation': 10,
            'scheduled_task': 5,
            'general_automation': 5
        }
        score += use_case_scores.get(metadata.use_case, 0)
        
        # Feature scoring
        if metadata.has_webhook:
            score += 10
        if metadata.has_http:
            score += 5
        if metadata.has_database:
            score += 5
        if metadata.has_notification:
            score += 5
        
        # Complexity scoring (prefer medium complexity)
        if 5 <= metadata.complexity <= 30:
            score += 10
        elif metadata.complexity > 30:
            score -= 5  # Too complex
        
        return min(score, 100)
    
    def generate_embedding_text(self, metadata: WorkflowMetadata) -> str:
        """Generate text for embedding."""
        return f"{metadata.name} {metadata.description} {metadata.category} {metadata.use_case}"


def select_top_workflows(workflows: List[tuple], n: int = 100) -> List[tuple]:
    """Select top N workflows by score."""
    # Sort by score (descending)
    sorted_workflows = sorted(workflows, key=lambda x: x[1], reverse=True)
    return sorted_workflows[:n]


def main():
    """Demo: Analyze workflows and select top 100."""
    indexer = WorkflowIndexer()
    
    # Example workflow paths
    repos = {
        'ultimate-n8n-ai-workflows': '/home/jnovoas/sentinel/ultimate-n8n-ai-workflows/workflows',
        'n8n-danitilahun-workflows': '/home/jnovoas/sentinel/n8n-danitilahun-workflows/workflows',
        'n8n-zie619-workflows': '/home/jnovoas/sentinel/n8n-zie619-workflows'
    }
    
    all_workflows = []
    
    for source, path in repos.items():
        workflow_path = Path(path)
        if not workflow_path.exists():
            print(f"⚠️  {source}: Path not found")
            continue
        
        json_files = list(workflow_path.rglob('*.json'))
        print(f"📁 {source}: {len(json_files)} workflows")
        
        for json_file in json_files[:100]:  # Limit for demo
            try:
                with open(json_file, 'r') as f:
                    workflow = json.load(f)
                
                metadata = indexer.analyze_workflow(workflow, source)
                if metadata:
                    score = indexer.score_workflow(metadata)
                    all_workflows.append((metadata, score, workflow))
            except Exception as e:
                pass
    
    # Select top 100
    top_100 = select_top_workflows(all_workflows, n=100)
    
    print(f"\n🏆 TOP 100 WORKFLOWS FOR SENTINEL\n")
    print("="*80)
    
    for i, (metadata, score, _) in enumerate(top_100[:20], 1):
        print(f"{i:2}. [{score:3}] {metadata.name[:60]}")
        print(f"    Category: {metadata.category} | Use Case: {metadata.use_case}")
        print(f"    Nodes: {metadata.complexity} | Source: {metadata.source}")
        print()
    
    print(f"\nTotal selected: {len(top_100)} workflows")
    
    # Category distribution
    categories = {}
    for metadata, score, _ in top_100:
        categories[metadata.category] = categories.get(metadata.category, 0) + 1
    
    print("\n📊 Category Distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:20} {count:3} workflows")


if __name__ == '__main__':
    main()
