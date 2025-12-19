"""
Truth Algorithm - Claim Extraction Engine
==========================================

Extracts verifiable claims from text (TV transcripts, social media, articles).

Features:
- Identifies factual claims vs opinions
- Extracts entities (people, organizations, dates, locations)
- Classifies claim types (statistical, causal, comparative, etc.)
- Outputs structured JSON for verification pipeline

Author: Sentinel Team
License: MIT
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import spacy
from transformers import pipeline

# Load models (lazy loading for performance)
_nlp = None
_classifier = None

def get_nlp():
    """Lazy load spaCy model."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            _nlp = spacy.load("en_core_web_sm")
    return _nlp

def get_classifier():
    """Lazy load zero-shot classifier."""
    global _classifier
    if _classifier is None:
        _classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _classifier


@dataclass
class Entity:
    """Extracted entity from claim."""
    text: str
    type: str  # PERSON, ORG, DATE, GPE, MONEY, etc.
    start: int
    end: int


@dataclass
class Claim:
    """Extracted claim with metadata."""
    text: str
    claim_type: str  # factual, opinion, prediction, etc.
    confidence: float  # 0-1
    entities: List[Entity]
    is_verifiable: bool
    keywords: List[str]
    extracted_at: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            **asdict(self),
            'entities': [asdict(e) for e in self.entities]
        }


class ClaimExtractor:
    """
    Extracts verifiable claims from text.
    
    Usage:
        extractor = ClaimExtractor()
        claims = extractor.extract("Biden said unemployment is at 3.5%")
    """
    
    def __init__(self):
        self.nlp = get_nlp()
        self.classifier = get_classifier()
        
        # Claim type labels for classification
        self.claim_types = [
            "factual statement",
            "opinion",
            "prediction",
            "statistical claim",
            "causal claim",
            "comparative claim"
        ]
        
        # Patterns that indicate factual claims
        self.factual_patterns = [
            r'\b(is|are|was|were|has|have|had)\b',  # State of being
            r'\b\d+%?\b',  # Numbers/percentages
            r'\b(said|stated|announced|reported|claimed)\b',  # Attribution
            r'\b(according to|based on|data shows)\b',  # Evidence
        ]
        
        # Patterns that indicate opinions
        self.opinion_patterns = [
            r'\b(think|believe|feel|opinion|should|must|ought)\b',
            r'\b(good|bad|better|worse|best|worst)\b',
            r'\b(like|love|hate|prefer)\b',
        ]
    
    def extract(self, text: str) -> List[Claim]:
        """
        Extract claims from text.
        
        Args:
            text: Input text (transcript, article, tweet, etc.)
            
        Returns:
            List of extracted claims
        """
        # Split into sentences
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        claims = []
        for sentence in sentences:
            # Skip very short sentences
            if len(sentence.split()) < 5:
                continue
            
            # Extract claim
            claim = self._extract_claim(sentence)
            if claim:
                claims.append(claim)
        
        return claims
    
    def _extract_claim(self, sentence: str) -> Optional[Claim]:
        """Extract a single claim from a sentence."""
        # Check if sentence contains a verifiable claim
        is_verifiable = self._is_verifiable(sentence)
        
        if not is_verifiable:
            return None
        
        # Classify claim type
        claim_type, confidence = self._classify_claim(sentence)
        
        # Extract entities
        entities = self._extract_entities(sentence)
        
        # Extract keywords
        keywords = self._extract_keywords(sentence)
        
        return Claim(
            text=sentence,
            claim_type=claim_type,
            confidence=confidence,
            entities=entities,
            is_verifiable=is_verifiable,
            keywords=keywords,
            extracted_at=datetime.utcnow().isoformat()
        )
    
    def _is_verifiable(self, sentence: str) -> bool:
        """
        Determine if sentence contains a verifiable claim.
        
        Verifiable claims:
        - Contain specific facts (numbers, dates, names)
        - Make assertions about reality
        - Can be checked against sources
        
        Not verifiable:
        - Pure opinions
        - Questions
        - Commands
        - Vague statements
        """
        sentence_lower = sentence.lower()
        
        # Check for opinion patterns (disqualify)
        for pattern in self.opinion_patterns:
            if re.search(pattern, sentence_lower):
                return False
        
        # Check for factual patterns (qualify)
        factual_score = 0
        for pattern in self.factual_patterns:
            if re.search(pattern, sentence_lower):
                factual_score += 1
        
        # Must have at least 1 factual pattern
        if factual_score == 0:
            return False
        
        # Check for specific entities (names, numbers, dates)
        doc = self.nlp(sentence)
        has_entities = any(
            ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY', 'PERCENT', 'CARDINAL']
            for ent in doc.ents
        )
        
        return has_entities
    
    def _classify_claim(self, sentence: str) -> tuple[str, float]:
        """
        Classify claim type using zero-shot classification.
        
        Returns:
            (claim_type, confidence)
        """
        result = self.classifier(
            sentence,
            candidate_labels=self.claim_types,
            multi_label=False
        )
        
        claim_type = result['labels'][0]
        confidence = result['scores'][0]
        
        return claim_type, confidence
    
    def _extract_entities(self, sentence: str) -> List[Entity]:
        """Extract named entities from sentence."""
        doc = self.nlp(sentence)
        
        entities = []
        for ent in doc.ents:
            entities.append(Entity(
                text=ent.text,
                type=ent.label_,
                start=ent.start_char,
                end=ent.end_char
            ))
        
        return entities
    
    def _extract_keywords(self, sentence: str) -> List[str]:
        """Extract important keywords from sentence."""
        doc = self.nlp(sentence)
        
        # Extract nouns and proper nouns
        keywords = [
            token.text.lower()
            for token in doc
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop
        ]
        
        return list(set(keywords))  # Remove duplicates


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_texts = [
        # Factual claims (should extract)
        "Biden said unemployment is at 3.5% in December 2023.",
        "The GDP grew by 2.5% last quarter according to the Federal Reserve.",
        "Elon Musk announced Tesla sold 500,000 cars in Q4.",
        "Climate change has caused temperatures to rise 1.5°C since 1850.",
        
        # Opinions (should NOT extract)
        "I think Biden is doing a great job.",
        "Tesla makes the best cars in the world.",
        "Climate change is the most important issue.",
        
        # Mixed (should extract factual parts)
        "Biden, who I think is great, said unemployment is at 3.5%.",
    ]
    
    print("🔍 Truth Algorithm - Claim Extraction POC\n")
    print("=" * 60)
    
    extractor = ClaimExtractor()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text[:60]}...")
        claims = extractor.extract(text)
        
        if claims:
            for claim in claims:
                print(f"\n✅ CLAIM EXTRACTED:")
                print(f"   Text: {claim.text}")
                print(f"   Type: {claim.claim_type} (confidence: {claim.confidence:.2f})")
                print(f"   Entities: {[f'{e.text} ({e.type})' for e in claim.entities]}")
                print(f"   Keywords: {claim.keywords}")
                print(f"   Verifiable: {claim.is_verifiable}")
        else:
            print("   ❌ No verifiable claims found")
    
    print("\n" + "=" * 60)
    print("✅ POC Complete!")
