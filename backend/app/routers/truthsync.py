"""
TruthSync Router - Truth Verification Service
Exposes TruthSync client to the frontend for claim verification
"""

import logging
import asyncio
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.truthsync import truthsync_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/truthsync", tags=["TruthSync"])

class VerificationRequest(BaseModel):
    text: str
    metadata: Optional[Dict] = None

@router.post("/verify")
async def verify_claim(request: VerificationRequest):
    """
    Verify a claim or query using TruthSync service
    """
    try:
        result = await truthsync_client.verify(request.text, request.metadata)
        return result
    except Exception as e:
        logger.error(f"Error in truth verification: {e}")
        return {
            "verified": False,
            "confidence": 0.0,
            "status": "ERROR",
            "explanation": f"Service error: {str(e)}"
        }

@router.get("/search")
async def search_truth(query: str = Query(...), max_results: int = 5):
    """
    Direct search for information using TruthAlgorithm providers (DuckDuckGo/Google)
    """
    try:
        from app.services.truthsync import truthsync_client
        # Usamos el engine interno para buscar sin necesariamente verificar un claim complejo
        loop = asyncio.get_event_loop()
        # El motor local ya tiene acceso al engine de búsqueda
        if hasattr(truthsync_client, 'algorithm') and truthsync_client.algorithm:
            results = await loop.run_in_executor(
                None, 
                truthsync_client.algorithm.search_engine.search, 
                query, 
                max_results
            )
            return {
                "query": query,
                "results": [
                    {
                        "title": r.title,
                        "url": r.url,
                        "snippet": r.snippet,
                        "source_type": r.source_type,
                        "confidence": r.confidence
                    } for r in results
                ]
            }
        return {"error": "Search algorithm not initialized"}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def truthsync_health():
    """Check TruthSync service health"""
    return await truthsync_client.health_check()
