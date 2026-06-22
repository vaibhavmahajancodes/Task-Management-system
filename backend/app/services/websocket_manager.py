"""
In-memory WebSocket connection registry.

Two channels are supported:
  - "user:{user_id}"     -> personal notifications + online presence
  - "project:{project_id}" -> live task/board updates for everyone viewing that project

This is intentionally a simple in-process manager. For a multi-worker /
multi-server deployment, swap the in-memory dicts for a Redis pub/sub
backend (the public methods below would not need to change).
"""
import json
from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        self.project_connections: Dict[int, Set[WebSocket]] = {}

    # --- user / notification channel -------------------------------------------------
    async def connect_user(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.user_connections.setdefault(user_id, set()).add(websocket)

    def disconnect_user(self, user_id: int, websocket: WebSocket) -> None:
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        connections = self.user_connections.get(user_id, set())
        dead = set()
        for ws in connections:
            try:
                await ws.send_text(json.dumps(payload, default=str))
            except Exception:
                dead.add(ws)
        for ws in dead:
            connections.discard(ws)

    def online_user_ids(self) -> list:
        return list(self.user_connections.keys())

    # --- project / board channel -------------------------------------------------------
    async def connect_project(self, project_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.project_connections.setdefault(project_id, set()).add(websocket)

    def disconnect_project(self, project_id: int, websocket: WebSocket) -> None:
        if project_id in self.project_connections:
            self.project_connections[project_id].discard(websocket)
            if not self.project_connections[project_id]:
                del self.project_connections[project_id]

    async def broadcast_to_project(self, project_id: int, payload: dict) -> None:
        connections = self.project_connections.get(project_id, set())
        dead = set()
        for ws in connections:
            try:
                await ws.send_text(json.dumps(payload, default=str))
            except Exception:
                dead.add(ws)
        for ws in dead:
            connections.discard(ws)


# A single shared instance used across the app (imported by routes/services).
manager = ConnectionManager()
