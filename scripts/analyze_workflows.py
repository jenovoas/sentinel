#!/usr/bin/env python3
"""
Workflow Analyzer - POC
Scans 8,320+ n8n workflows and generates metadata index
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import re

# Security/AI keywords for scoring
SECURITY_KEYWORDS = {
    'phishing', 'malware', 'threat', 'incident', 'security', 'vulnerability',
    'attack', 'breach', 'ioc', 'indicator', 'compromise', 'ransomware',
    'exploit', 'cve', 'siem', 'soc', 'dfir', 'forensic', 'detection',
    'alert', 'suspicious', 'malicious', 'intrusion', 'firewall', 'ids',
    'ips', 'edr', 'antivirus', 'scan', 'audit', 'compliance', 'risk'
}

AI_KEYWORDS = {
    'ai', 'llm', 'gpt', 'openai', 'anthropic', 'claude', 'gemini',
    'machine learning', 'ml', 'nlp', 'sentiment', 'classification',
    'prediction', 'model', 'training', 'inference', 'embedding'
}

AUTOMATION_KEYWORDS = {
    'automation', 'workflow', 'orchestration', 'integration', 'api',
    'webhook', 'trigger', 'schedule', 'cron', 'batch', 'pipeline'
}

# Workflow repositories to scan
WORKFLOW_REPOS = [
    'ultimate-n8n-ai-workflows',
    'n8n-zie619-workflows',
    'n8n-danitilahun-workflows',
    'n8n-workflows-safe',
    'n8n-automation-2025-AI-Agent-Suite',
    'securityonion-n8n-workflows',
]


class WorkflowAnalyzer:
    def __init__(self, base_path: str = '/home/jnovoas/sentinel'):
        self.base_path = Path(base_path)
        self.workflows = []
        self.stats = defaultdict(int)
        
    def scan_repository(self, repo_name: str) -> List[Dict]:
        """Scan a single repository for workflow JSON files"""
        repo_path = self.base_path / repo_name
        workflows = []
        
        if not repo_path.exists():
            print(f"⚠️  Repository not found: {repo_name}")
            return workflows
            
        print(f"📂 Scanning {repo_name}...")
        
        # Find all JSON files
        json_files = list(repo_path.rglob('*.json'))
        print(f"   Found {len(json_files)} JSON files")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Extract workflow metadata
                workflow = self.extract_metadata(data, json_file, repo_name)
                if workflow:
                    workflows.append(workflow)
                    self.stats['processed'] += 1
                    
            except Exception as e:
                self.stats['errors'] += 1
                # Skip invalid JSON files silently
                continue
                
        return workflows
    
    def extract_metadata(self, data: Dict, file_path: Path, repo: str) -> Dict:
        """Extract relevant metadata from workflow JSON"""
        try:
            # Basic metadata
            workflow = {
                'id': str(file_path.relative_to(self.base_path)),
                'name': data.get('name', file_path.stem),
                'description': data.get('description', ''),
                'repository': repo,
                'file_path': str(file_path),
            }
            
            # Extract nodes and integrations
            nodes = data.get('nodes', [])
            workflow['node_count'] = len(nodes)
            workflow['node_types'] = list(set(node.get('type', '') for node in nodes))
            
            # Extract integrations (from node types)
            integrations = set()
            for node in nodes:
                node_type = node.get('type', '')
                if node_type:
                    integrations.add(node_type)
            workflow['integrations'] = list(integrations)
            
            # Calculate scores
            workflow['security_score'] = self.calculate_security_score(workflow)
            workflow['ai_score'] = self.calculate_ai_score(workflow)
            workflow['automation_score'] = self.calculate_automation_score(workflow)
            workflow['complexity_score'] = self.calculate_complexity_score(workflow)
            
            # Overall relevance score
            workflow['relevance_score'] = (
                workflow['security_score'] * 3 +  # Security is 3x important
                workflow['ai_score'] * 2 +         # AI is 2x important
                workflow['automation_score']
            ) / 6
            
            # Categorize
            workflow['categories'] = self.categorize_workflow(workflow)
            
            return workflow
            
        except Exception as e:
            return None
    
    def calculate_security_score(self, workflow: Dict) -> float:
        """Calculate security relevance score (0-1)"""
        text = f"{workflow['name']} {workflow['description']}".lower()
        matches = sum(1 for keyword in SECURITY_KEYWORDS if keyword in text)
        return min(matches / 5, 1.0)  # Cap at 1.0
    
    def calculate_ai_score(self, workflow: Dict) -> float:
        """Calculate AI relevance score (0-1)"""
        text = f"{workflow['name']} {workflow['description']}".lower()
        matches = sum(1 for keyword in AI_KEYWORDS if keyword in text)
        
        # Check for AI-related node types
        ai_nodes = ['openai', 'anthropic', 'huggingface', 'cohere', 'ai']
        node_matches = sum(1 for node_type in workflow['node_types'] 
                          if any(ai in node_type.lower() for ai in ai_nodes))
        
        return min((matches + node_matches) / 5, 1.0)
    
    def calculate_automation_score(self, workflow: Dict) -> float:
        """Calculate automation relevance score (0-1)"""
        text = f"{workflow['name']} {workflow['description']}".lower()
        matches = sum(1 for keyword in AUTOMATION_KEYWORDS if keyword in text)
        return min(matches / 5, 1.0)
    
    def calculate_complexity_score(self, workflow: Dict) -> float:
        """Calculate workflow complexity (0-1)"""
        node_count = workflow['node_count']
        integration_count = len(workflow['integrations'])
        
        # Simple heuristic: more nodes + more integrations = more complex
        complexity = (node_count / 50 + integration_count / 20) / 2
        return min(complexity, 1.0)
    
    def categorize_workflow(self, workflow: Dict) -> List[str]:
        """Categorize workflow based on scores"""
        categories = []
        
        if workflow['security_score'] > 0.3:
            categories.append('security')
        if workflow['ai_score'] > 0.3:
            categories.append('ai')
        if workflow['automation_score'] > 0.3:
            categories.append('automation')
        if workflow['complexity_score'] > 0.6:
            categories.append('complex')
        elif workflow['complexity_score'] < 0.3:
            categories.append('simple')
            
        if not categories:
            categories.append('general')
            
        return categories
    
    def analyze_all(self) -> List[Dict]:
        """Scan all repositories and analyze workflows"""
        print("🚀 Starting workflow analysis...\n")
        
        all_workflows = []
        for repo in WORKFLOW_REPOS:
            workflows = self.scan_repository(repo)
            all_workflows.extend(workflows)
            print(f"   ✅ {len(workflows)} workflows processed\n")
        
        self.workflows = all_workflows
        return all_workflows
    
    def get_top_workflows(self, category: str = None, limit: int = 200) -> List[Dict]:
        """Get top workflows by relevance score"""
        workflows = self.workflows
        
        if category:
            workflows = [w for w in workflows if category in w['categories']]
        
        # Sort by relevance score
        sorted_workflows = sorted(workflows, key=lambda w: w['relevance_score'], reverse=True)
        return sorted_workflows[:limit]
    
    def generate_report(self) -> Dict:
        """Generate summary report"""
        total = len(self.workflows)
        
        # Count by category
        category_counts = defaultdict(int)
        for workflow in self.workflows:
            for category in workflow['categories']:
                category_counts[category] += 1
        
        # Top integrations
        integration_counts = defaultdict(int)
        for workflow in self.workflows:
            for integration in workflow['integrations']:
                integration_counts[integration] += 1
        
        top_integrations = sorted(integration_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        report = {
            'total_workflows': total,
            'repositories_scanned': len(WORKFLOW_REPOS),
            'category_distribution': dict(category_counts),
            'top_integrations': dict(top_integrations),
            'stats': dict(self.stats),
            'top_security_workflows': len([w for w in self.workflows if w['security_score'] > 0.5]),
            'top_ai_workflows': len([w for w in self.workflows if w['ai_score'] > 0.5]),
        }
        
        return report
    
    def save_index(self, output_path: str = 'workflow_index.json'):
        """Save workflow index to JSON file"""
        output_file = self.base_path / output_path
        
        data = {
            'metadata': {
                'total_workflows': len(self.workflows),
                'generated_at': '2025-12-16T20:37:00-03:00',
                'repositories': WORKFLOW_REPOS,
            },
            'workflows': self.workflows,
            'report': self.generate_report(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Index saved to: {output_file}")
        return output_file


def main():
    """Main execution"""
    analyzer = WorkflowAnalyzer()
    
    # Analyze all workflows
    workflows = analyzer.analyze_all()
    
    # Generate report
    report = analyzer.generate_report()
    
    print("\n" + "="*60)
    print("📊 WORKFLOW ANALYSIS REPORT")
    print("="*60)
    print(f"Total workflows analyzed: {report['total_workflows']}")
    print(f"Repositories scanned: {report['repositories_scanned']}")
    print(f"\nCategory Distribution:")
    for category, count in sorted(report['category_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {count}")
    
    print(f"\nTop Security Workflows: {report['top_security_workflows']}")
    print(f"Top AI Workflows: {report['top_ai_workflows']}")
    
    print(f"\nTop 10 Integrations:")
    for integration, count in list(report['top_integrations'].items())[:10]:
        print(f"  - {integration}: {count}")
    
    # Save index
    analyzer.save_index()
    
    # Show top 10 security workflows
    print("\n" + "="*60)
    print("🔒 TOP 10 SECURITY WORKFLOWS")
    print("="*60)
    top_security = analyzer.get_top_workflows(category='security', limit=10)
    for i, workflow in enumerate(top_security, 1):
        print(f"{i}. {workflow['name']}")
        print(f"   Score: {workflow['security_score']:.2f} | Nodes: {workflow['node_count']}")
        print(f"   Repo: {workflow['repository']}")
        print()


if __name__ == '__main__':
    main()
