from typing import List

from fastapi import WebSocket, HTTPException
from fastapi.security import SecurityScopes
from starlette import status
from starlette.exceptions import WebSocketException

from app.api.deps import get_current_access
from app.models import AccessType
from app.schemas import AlertOut


class ConnectionManager:
    """To handle connections / disconnections via websocket for multiple clients"""
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, token: str) -> None:
        await websocket.accept()
        try:
            await get_current_access(SecurityScopes([AccessType.admin, AccessType.user]), token)
        except HTTPException as e:
            await websocket.send_json(e.detail)
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)
        await websocket.close()

    async def broadcast(self, payload: AlertOut) -> None:
        for connection in self.active_connections:
            await connection.send_json(payload)


manager = ConnectionManager()
