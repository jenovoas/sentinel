#!/usr/bin/env python3
"""
n8n Workflow Automated Review Pipeline
Automatically categorizes and scores workflows for Sentinel integration.

Usage:
    python auto_review_workflows.py --input n8n-workflows-safe --output workflow-analysis
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class AutomatedReviewer:
    """Automated workflow reviewer with scoring."""
    
    def __init__(self):
        # Scoring weights
        self.sentinel_relevant_nodes = {
            'n8n-nodes-base.httpRequest': 5,  # API integration
            'n8n-nodes-base.webhook': 8,  # Event-driven
            'n8n-nodes-base.postgres': 7,  # Database
            'n8n-nodes-base.slack': 6,  # Notifications
            'n8n-nodes-base.discord': 6,
            'n8n-nodes-base.email': 5,
            'n8n-nodes-base.schedule': 7,  # Automation
            'n8n-nodes-base.if': 4,  # Logic
            'n8n-nodes-base.switch': 4,
            'n8n-nodes-base.merge': 3,
            'n8n-nodes-base.set': 2,
        }
        
        # SIEM-specific keywords
        self.siem_keywords = [
            'alert', 'incident', 'threat', 'security',
            'log', 'monitor', 'detect', 'response',
            'vulnerability', 'scan', 'audit', 'compliance'
        ]
    
    def score_workflow(self, filepath: Path) -> Tuple[int, Dict]:
        """Score workflow for Sentinel relevance (0-100)."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        score = 0
        details = {
            'name': data.get('name', 'Unnamed'),
            'file': filepath.name,
            'category': filepath.parent.name,
            'nodes_count': len(data.get('nodes', [])),
            'reasons': []
        }
        
        # Check name/description for SIEM keywords
        text = (details['name'] + ' ' + 
                data.get('meta', {}).get('description', '')).lower()
        
        for keyword in self.siem_keywords:
            if keyword in text:
                score += 10
                details['reasons'].append(f"Contains keyword: {keyword}")
        
        # Score nodes
        for node in data.get('nodes', []):
            node_type = node.get('type', '')
            if node_type in self.sentinel_relevant_nodes:
                points = self.sentinel_relevant_nodes[node_type]
                score += points
                details['reasons'].append(
                    f"Has {node_type.replace('n8n-nodes-base.', '')}: +{points}"
                )
        
        # Bonus for webhooks (event-driven)
        if any(node.get('type') == 'n8n-nodes-base.webhook' 
               for node in data.get('nodes', [])):
            score += 15
            details['reasons'].append("Event-driven (webhook): +15")
        
        # Cap at 100
        score = min(score, 100)
        details['score'] = score
        
        return score, details
    
    def categorize_by_use_case(self, details: Dict) -> str:
        """Categorize workflow by Sentinel use case."""
        name = details['name'].lower()
        reasons = ' '.join(details['reasons']).lower()
        
        if any(kw in name or kw in reasons for kw in ['alert', 'incident', 'response']):
            return 'Incident Response'
        elif any(kw in name or kw in reasons for kw in ['log', 'monitor', 'detect']):
            return 'Monitoring & Detection'
        elif any(kw in name or kw in reasons for kw in ['threat', 'vulnerability', 'scan']):
            return 'Threat Intelligence'
        elif any(kw in name or kw in reasons for kw in ['compliance', 'audit', 'report']):
            return 'Compliance & Reporting'
        elif 'webhook' in reasons:
            return 'Event Automation'
        elif 'schedule' in reasons:
            return 'Scheduled Tasks'
        else:
            return 'General Automation'
    
    def analyze_directory(self, input_dir: Path) -> List[Dict]:
        """Analyze all workflows in directory."""
        results = []
        
        print(f"Analyzing workflows in {input_dir}...")
        
        for json_file in input_dir.rglob('*.json'):
            try:
                score, details = self.score_workflow(json_file)
                details['use_case'] = self.categorize_by_use_case(details)
                details['filepath'] = str(json_file)
                results.append(details)
            except Exception as e:
                print(f"Error analyzing {json_file}: {e}")
        
        return results
    
    def generate_report(self, results: List[Dict], output_dir: Path):
        """Generate analysis report."""
        output_dir.mkdir(exist_ok=True)
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Top candidates
        top_50 = results[:50]
        
        # By use case
        by_use_case = defaultdict(list)
        for r in results:
            by_use_case[r['use_case']].append(r)
        
        # Write main report
        with open(output_dir / 'analysis_report.md', 'w') as f:
            f.write("# n8n Workflows - Automated Analysis for Sentinel\n\n")
            f.write(f"**Total Analyzed**: {len(results)}\n\n")
            
            f.write("## Top 50 Candidates for Sentinel Integration\n\n")
            for i, workflow in enumerate(top_50, 1):
                f.write(f"### {i}. {workflow['name']} (Score: {workflow['score']})\n")
                f.write(f"- **File**: `{workflow['file']}`\n")
                f.write(f"- **Category**: {workflow['category']}\n")
                f.write(f"- **Use Case**: {workflow['use_case']}\n")
                f.write(f"- **Nodes**: {workflow['nodes_count']}\n")
                f.write(f"- **Reasons**:\n")
                for reason in workflow['reasons'][:5]:
                    f.write(f"  - {reason}\n")
                f.write("\n")
            
            f.write("\n## By Use Case\n\n")
            for use_case, workflows in sorted(by_use_case.items(), 
                                             key=lambda x: len(x[1]), 
                                             reverse=True):
                f.write(f"### {use_case} ({len(workflows)})\n\n")
                top_5 = sorted(workflows, key=lambda x: x['score'], reverse=True)[:5]
                for w in top_5:
                    f.write(f"- {w['name']} (Score: {w['score']})\n")
                f.write("\n")
        
        # Export top candidates as JSON
        with open(output_dir / 'top_candidates.json', 'w') as f:
            json.dump(top_50, f, indent=2)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Report: {output_dir / 'analysis_report.md'}")
        print(f"   Top 50: {output_dir / 'top_candidates.json'}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated workflow analysis')
    parser.add_argument('--input', default='n8n-workflows-safe', 
                       help='Input directory with safe workflows')
    parser.add_argument('--output', default='workflow-analysis',
                       help='Output directory for analysis')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    if not input_dir.exists():
        print(f"Error: {input_dir} not found")
        sys.exit(1)
    
    reviewer = AutomatedReviewer()
    results = reviewer.analyze_directory(input_dir)
    reviewer.generate_report(results, Path(args.output))


if __name__ == '__main__':
    main()
