from fastapi import APIRouter

from app.services.monitoring import get_dashboard_snapshot

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/status")
async def dashboard_status():
    """Return database/system snapshot and suggestions."""
    return await get_dashboard_snapshot()
