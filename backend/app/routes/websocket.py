from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.jwt_handler import decode_token
from app.database.db import SessionLocal
from app.models.project import Project
from app.models.user import User
from app.services.websocket_manager import manager

router = APIRouter(tags=["WebSockets"])


def _authenticate_ws_token(token: str, db: Session) -> User | None:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
    except JWTError:
        return None
    if user_id is None:
        return None
    return db.query(User).filter(User.id == int(user_id), User.is_active.is_(True)).first()


@router.websocket("/ws/notifications")
async def notifications_socket(websocket: WebSocket, token: str = Query(...)):
    """
    Personal channel: pushes new notifications to the client the instant
    they are created, and is used to derive online/offline presence.
    """
    db = SessionLocal()
    try:
        user = _authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=4401)
            return

        await manager.connect_user(user.id, websocket)
        try:
            while True:
                # The client doesn't need to send anything; we just keep the
                # connection open and wait for it to disconnect. Any message
                # received is treated as a no-op heartbeat/ping.
                await websocket.receive_text()
        except Exception:
             logger.exception(...)
        finally:
            manager.disconnect_user(user.id, websocket)
    finally:
        db.close()


@router.websocket("/ws/board/{project_id}")
async def board_socket(websocket: WebSocket, project_id: int, token: str = Query(...)):
    """
    Project channel: broadcasts task created/updated/moved/deleted and new
    comment events to everyone currently viewing that project's Kanban board.
    """
    db = SessionLocal()
    try:
        user = _authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=4401)
            return

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            await websocket.close(code=4404)
            return
        is_member = user.role.value == "admin" or project.owner_id == user.id or any(
            m.id == user.id for m in project.members
        )
        if not is_member:
            await websocket.close(code=4403)
            return

        await manager.connect_project(project_id, websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            manager.disconnect_project(project_id, websocket)
    finally:
        db.close()
