#!/usr/bin/env python3
"""
Psychology-to-n8n Pipeline (Truth Algorithm Layer 7)
Extracts behavioral deception patterns from psychology/psychiatry literature
and auto-generates n8n workflows for real-time truth detection.

Usage:
    python psychology_to_n8n_pipeline.py --input ekman_emotions_revealed.txt --output ekman_workflow.json
"""

import re
import json
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class TruthPattern:
    """Behavioral truth/deception pattern from scientific literature"""
    category: str  # microexpression, verbal, body, linguistic
    name: str  # Unique identifier
    trigger: str  # Regex pattern for detection in text
    n8n_node_type: str  # gpt_vision, regex_analyzer, silence_detector, etc.
    weight: float  # Scientific weight (0.0-1.0)
    f1_score: float  # Validation metric from literature
    description: str  # Human-readable explanation
    source: str  # Ekman, DePaulo, Burgoon, etc.
    threshold: Optional[float] = None  # Numerical threshold if applicable
    context: str = ""  # Surrounding text from source


class PsychologyParser:
    """Parse psychology books for deception patterns"""
    
    # Pre-defined patterns with scientific validation
    KNOWN_PATTERNS = {
        "eyes_averted": TruthPattern(
            category="microexpression",
            name="eyes_averted",
            trigger=r"eyes?\s+(?:averted|deviated|shifted)\s+(?:for\s+)?(?:>|more than|over)\s*([0-9.]+)\s*(?:s|sec|seconds)",
            n8n_node_type="gpt_vision",
            weight=0.90,
            f1_score=0.85,
            description="Ekman: Eyes averted >0.3s indicates stress/deception",
            source="Ekman (1970s)",
            threshold=0.3
        ),
        "pupil_dilation": TruthPattern(
            category="microexpression",
            name="pupil_dilation",
            trigger=r"pupil(?:s)?\s+dilat(?:ed|ion)",
            n8n_node_type="gpt_vision",
            weight=0.80,
            f1_score=0.78,
            description="Physiological arousal indicator",
            source="Ekman (1970s)"
        ),
        "lip_compression": TruthPattern(
            category="microexpression",
            name="lip_compression",
            trigger=r"lip(?:s)?\s+(?:pressed|compressed|tight)",
            n8n_node_type="gpt_vision",
            weight=0.75,
            f1_score=0.78,
            description="Emotion suppression indicator",
            source="Ekman (1970s)"
        ),
        "body": [
            r"hand(?:s)?\s+(?:to|touching|covering)\s+(?:face|mouth|nose)",
            r"feet?\s+(?:point(?:ing)?|orient(?:ed)?)\s+(?:to|toward)\s+(?:door|exit)",
            r"(?:closed|defensive)\s+posture",
            r"(?:self-)?(?:touch|soothing)\s+(?:>|more than)\s*([0-9]+)x\s*/\s*min",
            r"arm(?:s)?\s+cross(?:ed|ing)",
            r"lean(?:ing)?\s+(?:away|back)",
        ],
        "linguistic": [
            r"pronoun\s+(?:shift|change|avoidance)",
            r"(?:temporal|time)\s+inconsisten(?:cy|cies)",
            r"(?:lack of|reduced)\s+detail",
            r"passive\s+voice",
            r"distancing\s+language",
        ]
    }
    
    # Known sources and their baseline accuracy
    SOURCE_ACCURACY = {
        "ekman": 0.85,  # Microexpression research
        "depaulo": 0.70,  # Verbal cues meta-analysis
        "burgoon": 0.65,  # Body language
        "vrij": 0.60,  # Cognitive load
        "porter": 0.65,  # Psychology of lies
    }
    
    def parse_book(self, text: str, source: str) -> List[DeceptionPattern]:
        """Extract all deception patterns from book text"""
        patterns = []
        
        for category, regexes in self.PATTERN_REGEXES.items():
            for regex in regexes:
                matches = re.finditer(regex, text, re.IGNORECASE)
                for match in matches:
                    # Extract context around match
                    context = self._extract_context(text, match.start(), match.end())
                    
                    # Extract accuracy if mentioned
                    accuracy = self._extract_accuracy(context)
                    
                    # Use source baseline if no specific accuracy found
                    if accuracy is None:
                        accuracy = self._get_source_accuracy(source)
                    
                    # Extract threshold if present
                    threshold = self._extract_threshold(match)
                    
                    pattern = DeceptionPattern(
                        category=category,
                        pattern=match.group(0),
                        threshold=threshold,
                        accuracy=accuracy,
                        source=source,
                        n8n_template=self._generate_n8n_template(
                            category, match.group(0), threshold
                        ),
                        context=context[:100]  # First 100 chars of context
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _extract_accuracy(self, context: str) -> Optional[float]:
        """Extract accuracy percentage from context"""
        accuracy_match = re.search(
            r"([0-9]{1,3})%\s+(?:accuracy|correct|reliable|success)",
            context,
            re.IGNORECASE
        )
        if accuracy_match:
            return float(accuracy_match.group(1)) / 100.0
        return None
    
    def _get_source_accuracy(self, source: str) -> float:
        """Get baseline accuracy for known source"""
        source_lower = source.lower()
        for key, accuracy in self.SOURCE_ACCURACY.items():
            if key in source_lower:
                return accuracy
        return 0.70  # Default accuracy
    
    def _extract_threshold(self, match: re.Match) -> Optional[float]:
        """Extract numerical threshold from pattern"""
        if match.groups():
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                pass
        return None
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 200) -> str:
        """Extract surrounding context for pattern"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _generate_n8n_template(
        self,
        category: str,
        pattern: str,
        threshold: Optional[float]
    ) -> str:
        """Generate n8n workflow node template for pattern"""
        
        if category == "microexpression":
            if "eyes" in pattern.lower() or "avert" in pattern.lower():
                return "gpt4_vision_eye_aversion"
            elif "pupil" in pattern.lower():
                return "gpt4_vision_pupil_dilation"
            elif "lip" in pattern.lower():
                return "gpt4_vision_lip_compression"
            elif "brow" in pattern.lower():
                return "gpt4_vision_brow_furrow"
            elif "nostril" in pattern.lower():
                return "gpt4_vision_nostril_flare"
        
        elif category == "verbal":
            if "filler" in pattern.lower():
                return "whisper_filler_detection"
            elif "pause" in pattern.lower():
                return "whisper_pause_analysis"
            elif "repetition" in pattern.lower():
                return "nlp_repetition_detection"
            elif "pitch" in pattern.lower():
                return "whisper_pitch_analysis"
            elif "speech rate" in pattern.lower():
                return "whisper_speech_rate"
        
        elif category == "body":
            if "hand" in pattern.lower():
                return "gpt4_vision_hand_to_face"
            elif "feet" in pattern.lower() or "foot" in pattern.lower():
                return "gpt4_vision_foot_orientation"
            elif "posture" in pattern.lower():
                return "gpt4_vision_posture_analysis"
            elif "arm" in pattern.lower():
                return "gpt4_vision_arm_crossing"
            elif "lean" in pattern.lower():
                return "gpt4_vision_leaning"
        
        elif category == "linguistic":
            if "pronoun" in pattern.lower():
                return "nlp_pronoun_analysis"
            elif "temporal" in pattern.lower() or "time" in pattern.lower():
                return "nlp_temporal_consistency"
            elif "detail" in pattern.lower():
                return "nlp_detail_analysis"
            elif "passive" in pattern.lower():
                return "nlp_passive_voice"
            elif "distancing" in pattern.lower():
                return "nlp_distancing_language"
        
        return f"{category}_generic"


class N8nWorkflowGenerator:
    """Generate n8n workflows from deception patterns"""
    
    # Node templates for different analysis types
    NODE_TEMPLATES = {
        "gpt4_vision_eye_aversion": {
            "name": "Microexp_EyeAversion",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 1,
            "position": [0, 0],
            "parameters": {
                "method": "POST",
                "url": "={{ $env.GPT4_VISION_ENDPOINT }}",
                "authentication": "predefinedCredentialType",
                "nodeCredentialType": "openAiApi",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {
                            "name": "model",
                            "value": "gpt-4-vision-preview"
                        },
                        {
                            "name": "messages",
                            "value": [{
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyze this video frame. Are the subject's eyes averted for >0.3 seconds? Return JSON: {averted: boolean, duration: float, confidence: float}"
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": "={{ $json.frame_url }}"}
                                    }
                                ]
                            }]
                        }
                    ]
                }
            }
        },
        
        "whisper_filler_detection": {
            "name": "Verbal_FillerDetection",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [0, 0],
            "parameters": {
                "functionCode": """
const transcript = $input.item.json.transcript;
const fillers = (transcript.match(/\\b(um|uh|eh|ah|like|you know|basically|actually)\\b/gi) || []).length;
const duration_min = $input.item.json.duration / 60;
const fillers_per_min = fillers / duration_min;

return {
  json: {
    category: 'verbal',
    fillers_total: fillers,
    fillers_per_min: fillers_per_min,
    stress_indicator: fillers_per_min > 5,
    score: fillers_per_min > 5 ? 0.7 : 0.3,
    confidence: 0.7
  }
};
"""
            }
        },
        
        # Add more templates as needed...
    }
    
    def generate_workflow(
        self,
        patterns: List[DeceptionPattern],
        workflow_name: str
    ) -> Dict:
        """Generate complete n8n workflow from patterns"""
        
        nodes = []
        connections = {}
        
        # 1. Add trigger node (webhook)
        nodes.append({
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300],
            "webhookId": f"truth-{workflow_name.lower()}",
            "parameters": {
                "path": f"truth-analysis-{workflow_name.lower()}",
                "responseMode": "responseNode",
                "responseData": "allEntries"
            }
        })
        
        # 2. Add frame extraction node (for video analysis)
        nodes.append({
            "name": "FrameExtractor",
            "type": "n8n-nodes-base.executeCommand",
            "typeVersion": 1,
            "position": [450, 300],
            "parameters": {
                "command": "ffmpeg -i {{ $json.stream_url }} -vf fps=10 -f image2pipe -"
            }
        })
        
        # 3. Add pattern detection nodes
        y_offset = 150
        pattern_nodes = []
        for i, pattern in enumerate(patterns):
            template_name = pattern.n8n_template
            if template_name in self.NODE_TEMPLATES:
                node = self.NODE_TEMPLATES[template_name].copy()
                node["position"] = [650, 200 + (i * y_offset)]
                nodes.append(node)
                pattern_nodes.append(node["name"])
        
        # 4. Add consensus node
        nodes.append({
            "name": "BehavioralConsensus",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [900, 300],
            "parameters": {
                "functionCode": self._generate_consensus_code(patterns)
            }
        })
        
        # 5. Add response node
        nodes.append({
            "name": "RespondToWebhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [1100, 300],
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{ $json }}"
            }
        })
        
        # 6. Generate connections
        connections = self._generate_connections(pattern_nodes)
        
        return {
            "name": workflow_name,
            "nodes": nodes,
            "connections": connections,
            "active": True,
            "settings": {},
            "tags": ["truth-algorithm", "behavioral-analysis", "auto-generated"]
        }
    
    def _generate_consensus_code(self, patterns: List[DeceptionPattern]) -> str:
        """Generate JavaScript code for weighted consensus"""
        
        # Category weights based on scientific evidence
        weights = {
            "microexpression": 0.30,
            "verbal": 0.25,
            "body": 0.20,
            "linguistic": 0.15,
            "temporal": 0.10
        }
        
        code = """
const results = $input.all();
let weighted_score = 0.0;
let total_weight = 0.0;
const evidence = {};

"""
        
        # Add weighted scoring for each category
        for category in weights.keys():
            weight = weights[category]
            code += f"""
// {category.capitalize()} analysis
const {category}_results = results.filter(r => r.json.category === '{category}');
if ({category}_results.length > 0) {{
  const {category}_avg = {category}_results.reduce((sum, r) => sum + r.json.score, 0) / {category}_results.length;
  weighted_score += {category}_avg * {weight};
  total_weight += {weight};
  evidence['{category}'] = {{
    score: {category}_avg,
    count: {category}_results.length,
    details: {category}_results.map(r => r.json)
  }};
}}

"""
        
        code += """
// Calculate final truth score (inverted - high stress = low truth)
const truth_score = total_weight > 0 ? 1.0 - (weighted_score / total_weight) : 0.5;

// Determine verdict
let verdict;
if (truth_score > 0.7) {
  verdict = "TRUTHFUL";
} else if (truth_score > 0.4) {
  verdict = "SUSPICIOUS";
} else {
  verdict = "DECEPTIVE";
}

return {
  json: {
    truth_score: truth_score,
    verdict: verdict,
    confidence: total_weight,
    evidence: evidence,
    timestamp: new Date().toISOString()
  }
};
"""
        return code
    
    def _generate_connections(self, pattern_nodes: List[str]) -> Dict:
        """Generate node connections"""
        connections = {
            "Webhook": {
                "main": [[{"node": "FrameExtractor", "type": "main", "index": 0}]]
            },
            "FrameExtractor": {
                "main": [[{"node": node, "type": "main", "index": 0} for node in pattern_nodes]]
            }
        }
        
        # Connect all pattern nodes to consensus
        for node in pattern_nodes:
            connections[node] = {
                "main": [[{"node": "BehavioralConsensus", "type": "main", "index": 0}]]
            }
        
        # Connect consensus to response
        connections["BehavioralConsensus"] = {
            "main": [[{"node": "RespondToWebhook", "type": "main", "index": 0}]]
        }
        
        return connections


def main():
    parser = argparse.ArgumentParser(
        description="Generate n8n workflows from psychology literature"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input text file (psychology book)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file (n8n workflow)"
    )
    parser.add_argument(
        "--source",
        default="Unknown",
        help="Source name (e.g., 'Ekman', 'DePaulo')"
    )
    parser.add_argument(
        "--workflow-name",
        help="Workflow name (default: derived from source)"
    )
    parser.add_argument(
        "--report",
        help="Optional: Generate pattern report JSON"
    )
    
    args = parser.parse_args()
    
    # Read input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Parse patterns
    print(f"Parsing {args.source} for deception patterns...")
    psychology_parser = PsychologyParser()
    patterns = psychology_parser.parse_book(text, args.source)
    
    print(f"Found {len(patterns)} behavioral patterns:")
    for category in ["microexpression", "verbal", "body", "linguistic"]:
        count = sum(1 for p in patterns if p.category == category)
        print(f"  - {category}: {count} patterns")
    
    # Generate workflow name
    workflow_name = args.workflow_name or f"{args.source}_BehavioralAnalysis_v1"
    
    # Generate n8n workflow
    print(f"\nGenerating n8n workflow: {workflow_name}")
    generator = N8nWorkflowGenerator()
    workflow = generator.generate_workflow(patterns, workflow_name)
    
    # Write output
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2)
    
    print(f"✅ Workflow saved to: {args.output}")
    print(f"   Nodes: {len(workflow['nodes'])}")
    print(f"   Ready for n8n import!")
    
    # Optional: Generate pattern report
    if args.report:
        report = {
            "source": args.source,
            "total_patterns": len(patterns),
            "patterns_by_category": {
                category: [
                    {
                        "pattern": p.pattern,
                        "threshold": p.threshold,
                        "accuracy": p.accuracy,
                        "n8n_template": p.n8n_template
                    }
                    for p in patterns if p.category == category
                ]
                for category in ["microexpression", "verbal", "body", "linguistic"]
            }
        }
        
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Pattern report saved to: {args.report}")
    
    return 0


if __name__ == "__main__":
    exit(main())
