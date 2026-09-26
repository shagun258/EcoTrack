"""
Real-time updates over WebSockets.

The frontend connects to ws://<host>/ws/notifications?token=<access_token>
and receives JSON messages whenever a pickup status changes or a
notification is created for that user. This is a simple in-process
connection manager - fine for a single backend instance; for multi-instance
deployments, back it with Redis pub/sub (REDIS_URL is already configured).
"""
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_token

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_to_user(self, user_id: int, message: dict) -> None:
        for connection in self.active_connections.get(user_id, []):
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: str = Query(...)):
    try:
        claims = decode_token(token)
        user_id = int(claims["sub"])
    except (ValueError, KeyError):
        await websocket.close(code=4401)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            # Client doesn't need to send anything; this just keeps the
            # connection alive and lets us detect disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
