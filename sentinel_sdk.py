"""
Sentinel Python SDK for Researchers
====================================

A simple Python SDK for interacting with Sentinel's API endpoints.

Installation:
    pip install requests pandas

Usage:
    from sentinel_sdk import SentinelClient
    
    client = SentinelClient("http://localhost:8000")
    status = client.get_health()
    print(status)

Author: Sentinel Team
License: MIT
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SemanticVectors:
    """Semantic vector measurements"""
    coherence: float
    entropy: float
    tte_us: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AIResponse:
    """AI query response"""
    response: str
    model: str
    enabled: bool
    latency_ms: float = 0


@dataclass
class VerificationResult:
    """TruthSync verification result"""
    text: str
    confidence: float
    status: str
    claims: List[str]
    processing_time_us: float
    cache_hit: bool


class SentinelClient:
    """
    Main client for interacting with Sentinel API
    
    Args:
        base_url: Base URL of Sentinel instance (default: http://localhost:8000)
        timeout: Request timeout in seconds (default: 30)
    
    Example:
        >>> client = SentinelClient()
        >>> health = client.get_health()
        >>> print(health['status'])
        'healthy'
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Sentinel-Python-SDK/1.0'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method, 
                url, 
                timeout=kwargs.pop('timeout', self.timeout),
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    # Health & Status
    
    def get_health(self) -> Dict:
        """
        Get system health status
        
        Returns:
            Dict with status, uptime, and component health
        
        Example:
            >>> health = client.get_health()
            >>> print(health['status'])
            'healthy'
        """
        return self._request('GET', '/api/v1/health')
    
    def get_status(self) -> Dict:
        """
        Get detailed system status
        
        Returns:
            Dict with CPU, memory, network metrics
        """
        return self._request('GET', '/api/v1/dashboard/status')
    
    def get_semantic_vectors(self) -> SemanticVectors:
        """
        Get semantic vector measurements
        
        Returns:
            SemanticVectors object with coherence, entropy, and TTE
        
        Example:
            >>> vectors = client.get_semantic_vectors()
            >>> print(f"Coherence: {vectors.coherence:.2%}")
            'Coherence: 96.00%'
        """
        data = self.get_status()
        return SemanticVectors(
            coherence=data.get('coherence', 0),
            entropy=data.get('entropy', 0),
            tte_us=data.get('tte_us', 0)
        )
    
    # AI Queries
    
    def query_ai(
        self, 
        prompt: str, 
        max_tokens: int = 100, 
        temperature: float = 0.3
    ) -> AIResponse:
        """
        Query the AI model
        
        Args:
            prompt: Text prompt for the AI
            max_tokens: Maximum tokens to generate (default: 100)
            temperature: Sampling temperature 0.0-1.0 (default: 0.3)
        
        Returns:
            AIResponse object with response text and metadata
        
        Example:
            >>> response = client.query_ai("Explain quantum computing")
            >>> print(response.response)
        """
        start_time = time.time()
        
        data = self._request(
            'POST',
            '/api/v1/ai/query',
            json={
                'prompt': prompt,
                'max_tokens': max_tokens,
                'temperature': temperature
            }
        )
        
        latency = (time.time() - start_time) * 1000
        
        return AIResponse(
            response=data.get('response', ''),
            model=data.get('model', ''),
            enabled=data.get('enabled', False),
            latency_ms=latency
        )
    
    def get_ai_health(self) -> Dict:
        """
        Check AI service health
        
        Returns:
            Dict with AI status and available models
        """
        return self._request('GET', '/api/v1/ai/health')
    
    # TruthSync Verification
    
    def verify_claim(
        self, 
        text: str, 
        metadata: Optional[Dict] = None
    ) -> VerificationResult:
        """
        Verify a claim using TruthSync
        
        Args:
            text: Claim text to verify
            metadata: Optional metadata dict
        
        Returns:
            VerificationResult object with confidence and status
        
        Example:
            >>> result = client.verify_claim("Water boils at 100°C")
            >>> print(f"Confidence: {result.confidence:.2%}")
        """
        data = self._request(
            'POST',
            '/api/v1/truthsync/verify',
            json={
                'text': text,
                'metadata': metadata or {}
            }
        )
        
        return VerificationResult(
            text=data.get('text', ''),
            confidence=data.get('confidence', 0),
            status=data.get('status', ''),
            claims=data.get('claims', []),
            processing_time_us=data.get('processing_time_us', 0),
            cache_hit=data.get('cache_hit', False)
        )
    
    def get_truthsync_health(self) -> Dict:
        """Check TruthSync service health"""
        return self._request('GET', '/api/v1/truthsync/health')
    
    # Analytics
    
    def get_analytics(self, hours: int = 24) -> Dict:
        """
        Get analytics data
        
        Args:
            hours: Number of hours of historical data (default: 24)
        
        Returns:
            Dict with statistics and metrics
        """
        return self._request(
            'GET',
            f'/api/v1/analytics/statistics?hours={hours}'
        )
    
    def get_anomalies(self) -> List[Dict]:
        """
        Get detected anomalies
        
        Returns:
            List of anomaly dicts
        """
        return self._request('GET', '/api/v1/analytics/anomalies')
    
    # Monitoring
    
    def monitor_coherence(
        self, 
        duration_seconds: int = 60, 
        interval: float = 1.0,
        callback: Optional[callable] = None
    ) -> List[SemanticVectors]:
        """
        Monitor system coherence over time
        
        Args:
            duration_seconds: How long to monitor (default: 60)
            interval: Sampling interval in seconds (default: 1.0)
            callback: Optional callback function called with each measurement
        
        Returns:
            List of SemanticVectors measurements
        
        Example:
            >>> def print_coherence(vectors):
            ...     print(f"Coherence: {vectors.coherence:.2%}")
            >>> data = client.monitor_coherence(60, callback=print_coherence)
        """
        measurements = []
        end_time = time.time() + duration_seconds
        
        while time.time() < end_time:
            vectors = self.get_semantic_vectors()
            measurements.append(vectors)
            
            if callback:
                callback(vectors)
            
            time.sleep(interval)
        
        return measurements
    
    # Utility Methods
    
    def ping(self) -> bool:
        """
        Check if Sentinel is reachable
        
        Returns:
            True if reachable, False otherwise
        """
        try:
            self.get_health()
            return True
        except:
            return False
    
    def get_version(self) -> str:
        """Get Sentinel version"""
        health = self.get_health()
        return health.get('version', 'unknown')
    
    def export_data(
        self, 
        data: List[Any], 
        filename: str, 
        format: str = 'json'
    ):
        """
        Export data to file
        
        Args:
            data: Data to export
            filename: Output filename
            format: Export format ('json' or 'csv')
        """
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'csv':
            try:
                import pandas as pd
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)
            except ImportError:
                raise Exception("pandas required for CSV export: pip install pandas")
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience functions

def quick_health_check(base_url: str = "http://localhost:8000") -> bool:
    """
    Quick health check
    
    Args:
        base_url: Sentinel instance URL
    
    Returns:
        True if healthy, False otherwise
    
    Example:
        >>> if quick_health_check():
        ...     print("Sentinel is healthy!")
    """
    with SentinelClient(base_url) as client:
        return client.ping()


def get_current_coherence(base_url: str = "http://localhost:8000") -> float:
    """
    Get current system coherence
    
    Args:
        base_url: Sentinel instance URL
    
    Returns:
        Current coherence value (0.0-1.0)
    
    Example:
        >>> coherence = get_current_coherence()
        >>> print(f"Coherence: {coherence:.2%}")
    """
    with SentinelClient(base_url) as client:
        vectors = client.get_semantic_vectors()
        return vectors.coherence


# Example usage
if __name__ == "__main__":
    # Basic usage
    print("Sentinel Python SDK - Example Usage\n")
    print("="*60)
    
    # Create client
    client = SentinelClient()
    
    # Check health
    print("\n1. Health Check:")
    if client.ping():
        health = client.get_health()
        print(f"   Status: {health['status']}")
        print(f"   Uptime: {health.get('uptime_seconds', 0):.1f}s")
    else:
        print("   ❌ Sentinel is not reachable")
        exit(1)
    
    # Get semantic vectors
    print("\n2. Semantic Vectors:")
    vectors = client.get_semantic_vectors()
    print(f"   Coherence: {vectors.coherence:.2%}")
    print(f"   Entropy: {vectors.entropy:.4f}")
    print(f"   TTE: {vectors.tte_us:.2f}μs")
    
    # Query AI
    print("\n3. AI Query:")
    response = client.query_ai("What is machine learning?", max_tokens=50)
    print(f"   Model: {response.model}")
    print(f"   Latency: {response.latency_ms:.2f}ms")
    print(f"   Response: {response.response[:100]}...")
    
    # Verify claim
    print("\n4. TruthSync Verification:")
    result = client.verify_claim("The Earth orbits the Sun")
    print(f"   Confidence: {result.confidence:.2%}")
    print(f"   Status: {result.status}")
    print(f"   Processing: {result.processing_time_us}μs")
    
    # Monitor coherence
    print("\n5. Monitoring Coherence (10 seconds):")
    def print_measurement(v):
        print(f"   {v.timestamp.strftime('%H:%M:%S')} - Coherence: {v.coherence:.4f}")
    
    measurements = client.monitor_coherence(
        duration_seconds=10,
        interval=2.0,
        callback=print_measurement
    )
    
    print(f"\n   Collected {len(measurements)} measurements")
    
    # Close client
    client.close()
    
    print("\n" + "="*60)
    print("✅ SDK example completed successfully!")
