from typing import List
from fastapi import WebSocket

class ConnectionManager:
    """
    Manages active WebSocket connections for real-time broadcasting.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # If sending fails, we assume the connection might be dead/closed
                # and relying on disconnect to clean it up, or we could remove it here.
                # For safety in this MVP, we just catch the error to prevent blocking other sends.
                pass

manager = ConnectionManager()
