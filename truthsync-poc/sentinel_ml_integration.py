"""
TruthSync ML Integration with Sentinel
Connects TruthSync verification to Sentinel's machine learning system
"""

import json
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TruthSyncFeatures:
    """Features extracted for ML training"""
    text_length: int
    factual_indicator_count: int
    opinion_indicator_count: int
    numeric_data_present: bool
    source_citation_present: bool
    temporal_reference_present: bool
    claim_confidence: float
    verification_result: bool
    processing_time_us: float


class SentinelMLConnector:
    """
    Connects TruthSync to Sentinel's ML system for:
    1. Feature extraction and training data generation
    2. Model updates based on verification results
    3. Adaptive threshold tuning
    4. Anomaly detection in claim patterns
    """
    
    def __init__(self, sentinel_ml_endpoint: str = "http://localhost:8000/ml"):
        self.endpoint = sentinel_ml_endpoint
        self.training_buffer: List[TruthSyncFeatures] = []
        self.buffer_size = 1000  # Send to ML when buffer reaches this size
        
    async def extract_features(self, text: str, claims: List[str], 
                               confidence: float, processing_time: float) -> TruthSyncFeatures:
        """Extract features from processed text for ML training"""
        
        # Count indicators
        factual_indicators = sum(1 for word in ['is', 'are', 'was', 'were', 'has', 'have', 
                                                 'announced', 'reported', 'confirmed']
                                if word in text.lower())
        
        opinion_indicators = sum(1 for word in ['think', 'believe', 'feel', 'should', 
                                                'probably', 'maybe', 'perhaps']
                               if word in text.lower())
        
        # Detect patterns
        numeric_present = any(char.isdigit() for char in text)
        source_present = any(phrase in text.lower() 
                           for phrase in ['according to', 'reported by', 'source:', 'via'])
        temporal_present = any(word in text.lower() 
                             for word in ['today', 'yesterday', 'this week', 'recently'])
        
        return TruthSyncFeatures(
            text_length=len(text),
            factual_indicator_count=factual_indicators,
            opinion_indicator_count=opinion_indicators,
            numeric_data_present=numeric_present,
            source_citation_present=source_present,
            temporal_reference_present=temporal_present,
            claim_confidence=confidence,
            verification_result=len(claims) > 0,
            processing_time_us=processing_time
        )
    
    async def send_training_data(self, features: TruthSyncFeatures):
        """Send features to Sentinel ML for training"""
        self.training_buffer.append(features)
        
        # Send batch when buffer is full
        if len(self.training_buffer) >= self.buffer_size:
            await self._flush_training_buffer()
    
    async def _flush_training_buffer(self):
        """Flush training buffer to Sentinel ML"""
        if not self.training_buffer:
            return
        
        # Convert to JSON
        training_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'truthsync',
            'features': [asdict(f) for f in self.training_buffer],
            'model_type': 'claim_verification'
        }
        
        # In production, this would send to Sentinel's ML API
        # For POC, we'll just log it
        print(f"📊 Sending {len(self.training_buffer)} training samples to Sentinel ML")
        
        # Simulate API call
        # await self._post_to_sentinel_ml(training_data)
        
        # Clear buffer
        self.training_buffer.clear()
    
    async def get_adaptive_threshold(self, current_accuracy: float) -> float:
        """
        Query Sentinel ML for optimal confidence threshold
        based on current accuracy and historical patterns
        """
        
        # In production, this would query Sentinel's ML model
        # For POC, use simple adaptive logic
        
        if current_accuracy < 0.85:
            # Lower threshold to catch more positives
            return 0.65
        elif current_accuracy > 0.95:
            # Raise threshold to reduce false positives
            return 0.80
        else:
            # Optimal range
            return 0.70
    
    async def detect_anomalies(self, recent_features: List[TruthSyncFeatures]) -> Dict:
        """
        Use Sentinel ML to detect anomalies in claim patterns
        (e.g., coordinated misinformation campaigns)
        """
        
        if len(recent_features) < 100:
            return {'anomaly_detected': False}
        
        # Calculate statistics
        avg_confidence = sum(f.claim_confidence for f in recent_features) / len(recent_features)
        verification_rate = sum(1 for f in recent_features if f.verification_result) / len(recent_features)
        
        # Simple anomaly detection (in production, use Sentinel's ML models)
        anomaly_detected = False
        anomaly_type = None
        
        if avg_confidence < 0.3 and verification_rate > 0.8:
            # Low confidence but high verification = potential model drift
            anomaly_detected = True
            anomaly_type = 'model_drift'
        
        elif avg_confidence > 0.9 and verification_rate < 0.2:
            # High confidence but low verification = potential attack
            anomaly_detected = True
            anomaly_type = 'potential_attack'
        
        return {
            'anomaly_detected': anomaly_detected,
            'anomaly_type': anomaly_type,
            'avg_confidence': avg_confidence,
            'verification_rate': verification_rate,
            'sample_size': len(recent_features)
        }
    
    async def update_model(self, verification_results: List[Tuple[bool, float]]):
        """
        Send verification results to Sentinel ML for model updates
        (online learning / continuous improvement)
        """
        
        correct_predictions = sum(1 for correct, _ in verification_results if correct)
        total = len(verification_results)
        accuracy = correct_predictions / total if total > 0 else 0.0
        
        update_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'accuracy': accuracy,
            'total_samples': total,
            'correct_predictions': correct_predictions,
            'model_version': 'truthsync_v1'
        }
        
        print(f"🔄 Updating Sentinel ML model: {accuracy:.1%} accuracy on {total} samples")
        
        # In production: await self._post_to_sentinel_ml(update_data, endpoint='/model/update')


class TruthSyncMLPipeline:
    """
    Complete ML pipeline integrating TruthSync with Sentinel
    """
    
    def __init__(self):
        self.connector = SentinelMLConnector()
        self.recent_features: List[TruthSyncFeatures] = []
        self.max_recent = 1000
    
    async def process_and_learn(self, text: str, claims: List[str], 
                               confidence: float, processing_time: float,
                               was_correct: bool) -> Dict:
        """
        Complete processing pipeline:
        1. Extract features
        2. Send to ML for training
        3. Detect anomalies
        4. Update model
        """
        
        # Extract features
        features = await self.connector.extract_features(
            text, claims, confidence, processing_time
        )
        
        # Store for anomaly detection
        self.recent_features.append(features)
        if len(self.recent_features) > self.max_recent:
            self.recent_features.pop(0)
        
        # Send to ML training
        await self.connector.send_training_data(features)
        
        # Detect anomalies
        anomalies = await self.connector.detect_anomalies(self.recent_features)
        
        # Get adaptive threshold
        current_accuracy = sum(1 for f in self.recent_features if f.verification_result) / len(self.recent_features)
        optimal_threshold = await self.connector.get_adaptive_threshold(current_accuracy)
        
        return {
            'features_extracted': True,
            'anomaly_status': anomalies,
            'recommended_threshold': optimal_threshold,
            'current_accuracy': current_accuracy
        }


# Example usage
async def demo_ml_integration():
    """Demo of TruthSync ML integration"""
    
    pipeline = TruthSyncMLPipeline()
    
    # Simulate processing
    test_texts = [
        ("The unemployment rate is 3.5% according to BLS.", True, 0.92),
        ("I think the economy is doing well.", False, 0.35),
        ("Tesla announced a new car priced at $25,000.", True, 0.88),
    ]
    
    print("="*60)
    print("TRUTHSYNC ML INTEGRATION DEMO")
    print("="*60)
    
    for text, had_claims, confidence in test_texts:
        claims = ["extracted claim"] if had_claims else []
        
        result = await pipeline.process_and_learn(
            text=text,
            claims=claims,
            confidence=confidence,
            processing_time=15.5,
            was_correct=True
        )
        
        print(f"\nProcessed: {text[:50]}...")
        print(f"  Recommended threshold: {result['recommended_threshold']:.2f}")
        print(f"  Current accuracy: {result['current_accuracy']:.1%}")
        
        if result['anomaly_status']['anomaly_detected']:
            print(f"  ⚠️  Anomaly detected: {result['anomaly_status']['anomaly_type']}")


if __name__ == '__main__':
    asyncio.run(demo_ml_integration())
