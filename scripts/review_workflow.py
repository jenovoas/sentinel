#!/usr/bin/env python3
"""
n8n Workflow Manual Review Tool
Interactive script to review workflows one by one.

Usage:
    python review_workflow.py <workflow_file.json>
    
    # Or review all in a category:
    python review_workflow.py --category AI-LLM
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

class WorkflowReviewer:
    """Interactive workflow reviewer."""
    
    def __init__(self):
        self.approved = []
        self.rejected = []
        self.flagged = []
    
    def analyze_workflow(self, filepath: Path) -> Dict:
        """Analyze a single workflow."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        name = data.get('name', 'Unnamed')
        nodes = data.get('nodes', [])
        
        # Extract useful info
        info = {
            'name': name,
            'file': filepath.name,
            'nodes_count': len(nodes),
            'node_types': [],
            'external_urls': [],
            'credentials_used': [],
            'description': data.get('meta', {}).get('description', 'No description')
        }
        
        # Analyze nodes
        for node in nodes:
            node_type = node.get('type', '')
            node_name = node.get('name', '')
            
            info['node_types'].append({
                'type': node_type,
                'name': node_name
            })
            
            # Check for credentials
            if 'credentials' in node:
                info['credentials_used'].append(node['credentials'])
        
        return info
    
    def display_workflow(self, info: Dict):
        """Display workflow information."""
        print("\n" + "="*80)
        print(f"📄 Workflow: {info['name']}")
        print("="*80)
        print(f"File: {info['file']}")
        print(f"Nodes: {info['nodes_count']}")
        print(f"\nDescription: {info['description']}")
        
        print(f"\n🔧 Node Types ({len(info['node_types'])}):")
        node_type_counts = {}
        for node in info['node_types']:
            node_type = node['type'].replace('n8n-nodes-base.', '')
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
        
        for node_type, count in sorted(node_type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {node_type}: {count}")
        
        if info['credentials_used']:
            print(f"\n🔑 Credentials Used:")
            for cred in info['credentials_used']:
                print(f"  - {cred}")
    
    def review_workflow(self, filepath: Path) -> str:
        """Review a single workflow interactively."""
        info = self.analyze_workflow(filepath)
        self.display_workflow(info)
        
        print("\n" + "-"*80)
        print("Options:")
        print("  [a] Approve - Safe for Sentinel")
        print("  [r] Reject - Not useful/too risky")
        print("  [f] Flag - Needs modification")
        print("  [s] Skip - Review later")
        print("  [q] Quit")
        print("-"*80)
        
        while True:
            choice = input("\nYour decision: ").lower().strip()
            
            if choice == 'a':
                self.approved.append(filepath)
                print("✅ Approved")
                return 'approved'
            elif choice == 'r':
                reason = input("Reason for rejection: ")
                self.rejected.append((filepath, reason))
                print("❌ Rejected")
                return 'rejected'
            elif choice == 'f':
                notes = input("What needs to be modified: ")
                self.flagged.append((filepath, notes))
                print("🚩 Flagged")
                return 'flagged'
            elif choice == 's':
                print("⏭️  Skipped")
                return 'skipped'
            elif choice == 'q':
                return 'quit'
            else:
                print("Invalid choice. Please choose a, r, f, s, or q.")
    
    def save_results(self, output_dir: Path):
        """Save review results."""
        output_dir.mkdir(exist_ok=True)
        
        # Save approved
        if self.approved:
            approved_dir = output_dir / 'approved'
            approved_dir.mkdir(exist_ok=True)
            with open(approved_dir / 'list.txt', 'w') as f:
                for filepath in self.approved:
                    f.write(f"{filepath}\n")
        
        # Save rejected
        if self.rejected:
            with open(output_dir / 'rejected.txt', 'w') as f:
                for filepath, reason in self.rejected:
                    f.write(f"{filepath}: {reason}\n")
        
        # Save flagged
        if self.flagged:
            with open(output_dir / 'flagged.txt', 'w') as f:
                for filepath, notes in self.flagged:
                    f.write(f"{filepath}: {notes}\n")
        
        # Summary
        with open(output_dir / 'summary.txt', 'w') as f:
            f.write(f"Review Summary\n")
            f.write(f"==============\n\n")
            f.write(f"Approved: {len(self.approved)}\n")
            f.write(f"Rejected: {len(self.rejected)}\n")
            f.write(f"Flagged: {len(self.flagged)}\n")
        
        print(f"\n📊 Results saved to {output_dir}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Review n8n workflows manually')
    parser.add_argument('workflow', nargs='?', help='Workflow file to review')
    parser.add_argument('--category', help='Review all workflows in category')
    parser.add_argument('--dir', default='n8n-workflows-safe', help='Base directory')
    parser.add_argument('--output', default='workflow-reviews', help='Output directory')
    
    args = parser.parse_args()
    
    reviewer = WorkflowReviewer()
    base_dir = Path(args.dir)
    
    # Get workflows to review
    workflows = []
    if args.workflow:
        workflows = [Path(args.workflow)]
    elif args.category:
        cat_dir = base_dir / args.category
        if not cat_dir.exists():
            print(f"Error: Category {args.category} not found")
            sys.exit(1)
        workflows = list(cat_dir.glob('*.json'))
    else:
        print("Error: Specify a workflow file or --category")
        sys.exit(1)
    
    print(f"📋 Found {len(workflows)} workflows to review")
    
    # Review each workflow
    for i, workflow in enumerate(workflows):
        print(f"\n[{i+1}/{len(workflows)}]")
        result = reviewer.review_workflow(workflow)
        
        if result == 'quit':
            print("\n👋 Quitting...")
            break
    
    # Save results
    reviewer.save_results(Path(args.output))
    
    print("\n✅ Review complete!")
    print(f"   Approved: {len(reviewer.approved)}")
    print(f"   Rejected: {len(reviewer.rejected)}")
    print(f"   Flagged: {len(reviewer.flagged)}")


if __name__ == '__main__':
    main()
