from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.jwt_handler import decode_token
from app.database.db import get_db
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decodes the bearer JWT, loads the corresponding active user, or raises 401.
    Every protected route depends on this (directly or via require_role).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise credentials_exception
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for RBAC, e.g.:
        @router.delete(...)
        def delete_project(current_user: User = Depends(require_role(UserRole.ADMIN))):
    Admins implicitly pass every role check since they are the superuser role.
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == UserRole.ADMIN:
            return current_user
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_checker


def is_project_member_or_admin(project, user: User) -> bool:
    """True if the user can view/act on a project: admin, owner, or member."""
    if user.role == UserRole.ADMIN:
        return True
    if project.owner_id == user.id:
        return True
    return any(member.id == user.id for member in project.members)


def can_manage_project(project, user: User) -> bool:
    """True if the user can edit/delete a project: admin, owner, or a project manager who is a member."""
    if user.role == UserRole.ADMIN:
        return True
    if project.owner_id == user.id:
        return True
    if user.role == UserRole.PROJECT_MANAGER and any(m.id == user.id for m in project.members):
        return True
    return False
