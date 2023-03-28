# Copyright (C) 2022-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from fastapi import WebSocket

from app.schemas import AlertOut


class ConnectionManager:
    """To handle connections / disconnections via websocket for multiple clients
    (from https://fastapi.tiangolo.com/advanced/websockets/#handling-disconnections-and-multiple-clients)"""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, payload: AlertOut) -> None:
        for connection in self.active_connections:
            await connection.send_json(payload)


manager = ConnectionManager()
