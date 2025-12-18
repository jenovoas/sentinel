"""
TruthSync Client for Sentinel Backend
Provides async interface to TruthSync verification service
"""

import httpx
from typing import List, Dict, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class TruthSyncClient:
    """
    Async client for TruthSync truth verification service
    
    Usage:
        client = TruthSyncClient()
        result = await client.verify("The unemployment rate is 3.5%")
    """
    
    def __init__(self, base_url: str = "http://truthsync:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"TruthSync client initialized: {base_url}")
    
    async def verify(self, text: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Verify a single claim
        
        Args:
            text: Text to verify
            metadata: Optional metadata
            
        Returns:
            {
                "claims": List[str],
                "confidence": float,
                "cache_hit": bool,
                "processing_time_us": float
            }
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/verify",
                json={"text": text, "metadata": metadata}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"TruthSync verification failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Truth verification service unavailable"
            )
    
    async def verify_batch(self, texts: List[str]) -> List[Dict]:
        """
        Verify multiple claims in batch
        
        Args:
            texts: List of texts to verify
            
        Returns:
            List of verification results
        """
        try:
            requests = [{"text": text} for text in texts]
            response = await self.client.post(
                f"{self.base_url}/verify/batch",
                json=requests
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"TruthSync batch verification failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Truth verification service unavailable"
            )
    
    async def health_check(self) -> Dict:
        """Check TruthSync service health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return {"status": "unhealthy"}
    
    async def get_stats(self) -> Dict:
        """Get TruthSync statistics"""
        try:
            response = await self.client.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get TruthSync stats: {e}")
            return {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global instance
truthsync_client = TruthSyncClient()
