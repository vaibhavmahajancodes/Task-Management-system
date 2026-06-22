from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import get_current_user, require_role
from app.auth.security import hash_password, verify_password
from app.database.db import get_db
from app.models.user import User, UserRole
from app.schemas.common import Message
from app.schemas.user import ChangePassword, UserOut, UserRoleUpdate, UserSummary, UserUpdate
from app.services.audit_service import log_action
from app.services.websocket_manager import manager

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_my_profile(
    payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", response_model=Message)
def change_my_password(
    payload: ChangePassword, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    log_action(db, current_user.id, "auth.password_changed", "user", current_user.id)
    return Message(message="Password updated successfully.")


@router.get("", response_model=List[UserSummary])
def list_users(
    role: UserRole | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lightweight directory of active users, used for assignment dropdowns / @mentions."""
    query = db.query(User).filter(User.is_active.is_(True))
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.username).all()


@router.get("/online", response_model=List[int])
def get_online_users(current_user: User = Depends(get_current_user)):
    return manager.online_user_ids()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.put("/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    log_action(db, current_user.id, "user.role_changed", "user", user.id, f"Role set to {payload.role.value}")
    return user


@router.put("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account.")
    user.is_active = False
    db.commit()
    db.refresh(user)
    log_action(db, current_user.id, "user.deactivated", "user", user.id)
    return user


@router.put("/{user_id}/activate", response_model=UserOut)
def activate_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = True
    db.commit()
    db.refresh(user)
    log_action(db, current_user.id, "user.activated", "user", user.id)
    return user
