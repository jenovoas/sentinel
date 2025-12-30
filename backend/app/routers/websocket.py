from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.managers.connection_manager import manager
import logging

router = APIRouter(tags=["websocket"])

logger = logging.getLogger(__name__)

@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming real-time security events
    to the Battlefield Dashboard.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive. We don't expect much input from the client
            # for the dashboard, but we need to await receive to keep the socket open.
            data = await websocket.receive_text()
            # Optional: Handle client messages (e.g., "ping")
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Battlefield Dashboard disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
