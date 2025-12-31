#!/usr/bin/env python3
"""
n8n Workflow Security Scanner
Analyzes workflows for security risks before execution.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

class WorkflowSecurityScanner:
    """Scans n8n workflows for security issues."""
    
    def __init__(self):
        self.suspicious_urls = []
        self.hardcoded_credentials = []
        self.code_execution = []
        self.external_calls = []
        self.high_risk_nodes = []
        
        # Patterns to detect
        self.url_pattern = re.compile(r'https?://[^\s"\']+')
        self.credential_patterns = [
            re.compile(r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
            re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
            re.compile(r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
            re.compile(r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
        ]
        
        # High-risk node types
        self.risky_nodes = {
            'n8n-nodes-base.executeCommand',  # Shell execution
            'n8n-nodes-base.code',  # JavaScript execution
            'n8n-nodes-base.function',  # Function execution
            'n8n-nodes-base.httpRequest',  # External HTTP
            'n8n-nodes-base.ssh',  # SSH access
            'n8n-nodes-base.ftp',  # FTP access
        }
        
        # Suspicious domains (common malware/phishing)
        self.suspicious_domains = {
            'bit.ly', 'tinyurl.com', 'goo.gl',  # URL shorteners
            'pastebin.com', 'hastebin.com',  # Code sharing
            '.tk', '.ml', '.ga', '.cf',  # Free TLDs
        }
    
    def scan_workflow(self, filepath: Path) -> Dict:
        """Scan a single workflow file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return {
                'file': str(filepath),
                'error': f'Failed to parse: {e}',
                'risk_level': 'UNKNOWN'
            }
        
        issues = []
        risk_level = 'LOW'
        
        # Extract workflow info
        name = data.get('name', 'Unnamed')
        nodes = data.get('nodes', [])
        
        # Check each node
        for node in nodes:
            node_type = node.get('type', '')
            node_name = node.get('name', '')
            parameters = node.get('parameters', {})
            
            # Check for risky node types
            if node_type in self.risky_nodes:
                issues.append({
                    'type': 'HIGH_RISK_NODE',
                    'node': node_name,
                    'node_type': node_type,
                    'severity': 'HIGH'
                })
                risk_level = 'HIGH'
            
            # Check for hardcoded credentials
            node_str = json.dumps(parameters)
            for pattern in self.credential_patterns:
                matches = pattern.findall(node_str)
                if matches:
                    issues.append({
                        'type': 'HARDCODED_CREDENTIAL',
                        'node': node_name,
                        'pattern': pattern.pattern,
                        'severity': 'CRITICAL'
                    })
                    risk_level = 'CRITICAL'
            
            # Check for external URLs
            urls = self.url_pattern.findall(node_str)
            for url in urls:
                # Check for suspicious domains
                if any(domain in url.lower() for domain in self.suspicious_domains):
                    issues.append({
                        'type': 'SUSPICIOUS_URL',
                        'node': node_name,
                        'url': url,
                        'severity': 'HIGH'
                    })
                    if risk_level == 'LOW':
                        risk_level = 'MEDIUM'
                elif 'http://' in url:  # Non-HTTPS
                    issues.append({
                        'type': 'INSECURE_HTTP',
                        'node': node_name,
                        'url': url,
                        'severity': 'MEDIUM'
                    })
                    if risk_level == 'LOW':
                        risk_level = 'MEDIUM'
        
        return {
            'file': filepath.name,  # Just filename for now
            'name': name,
            'nodes_count': len(nodes),
            'issues': issues,
            'risk_level': risk_level
        }
    
    def scan_directory(self, directory: Path) -> Dict:
        """Scan all workflows in directory."""
        results = {
            'total_files': 0,
            'scanned': 0,
            'errors': 0,
            'risk_summary': defaultdict(int),
            'workflows': []
        }
        
        # Find all JSON files
        json_files = list(directory.rglob('*.json'))
        results['total_files'] = len(json_files)
        
        print(f"Found {len(json_files)} JSON files")
        print("Scanning for security issues...")
        
        for i, filepath in enumerate(json_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(json_files)}")
            
            result = self.scan_workflow(filepath)
            results['workflows'].append(result)
            
            if 'error' in result:
                results['errors'] += 1
            else:
                results['scanned'] += 1
                results['risk_summary'][result['risk_level']] += 1
        
        return results
    
    def generate_report(self, results: Dict, output_file: Path):
        """Generate security report."""
        with open(output_file, 'w') as f:
            f.write("# n8n Workflows Security Scan Report\n\n")
            f.write(f"**Total files**: {results['total_files']}\n")
            f.write(f"**Successfully scanned**: {results['scanned']}\n")
            f.write(f"**Errors**: {results['errors']}\n\n")
            
            f.write("## Risk Summary\n\n")
            for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']:
                count = results['risk_summary'].get(level, 0)
                if count > 0:
                    f.write(f"- **{level}**: {count} workflows\n")
            
            f.write("\n## Critical Issues\n\n")
            critical = [w for w in results['workflows'] if w.get('risk_level') == 'CRITICAL']
            if critical:
                for workflow in critical[:20]:  # Top 20
                    f.write(f"### {workflow['name']}\n")
                    f.write(f"- File: `{workflow['file']}`\n")
                    f.write(f"- Nodes: {workflow['nodes_count']}\n")
                    f.write(f"- Issues:\n")
                    for issue in workflow.get('issues', []):
                        f.write(f"  - **{issue['type']}** ({issue['severity']}): {issue.get('node', 'N/A')}\n")
                    f.write("\n")
            else:
                f.write("No critical issues found.\n\n")
            
            f.write("\n## High Risk Issues\n\n")
            high = [w for w in results['workflows'] if w.get('risk_level') == 'HIGH']
            if high:
                f.write(f"Found {len(high)} high-risk workflows.\n\n")
                for workflow in high[:10]:  # Top 10
                    f.write(f"- `{workflow['file']}`: {workflow['name']}\n")
            else:
                f.write("No high-risk issues found.\n\n")
            
            f.write("\n## Recommendations\n\n")
            f.write("1. **CRITICAL/HIGH workflows**: Review manually before use\n")
            f.write("2. **Hardcoded credentials**: Replace with n8n credentials system\n")
            f.write("3. **External URLs**: Verify domains are legitimate\n")
            f.write("4. **Code execution nodes**: Sandbox or disable if not needed\n")
            f.write("5. **HTTP (non-HTTPS)**: Upgrade to HTTPS where possible\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scan_workflows.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Error: {directory} does not exist")
        sys.exit(1)
    
    scanner = WorkflowSecurityScanner()
    results = scanner.scan_directory(directory)
    
    # Generate report
    report_file = Path('n8n_security_report.md')
    scanner.generate_report(results, report_file)
    
    print(f"\n✅ Scan complete!")
    print(f"Report saved to: {report_file}")
    print(f"\nRisk Summary:")
    for level, count in sorted(results['risk_summary'].items()):
        print(f"  {level}: {count}")
