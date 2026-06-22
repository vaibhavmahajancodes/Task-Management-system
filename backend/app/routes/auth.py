from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token, decode_token
from app.auth.permissions import get_current_user
from app.auth.security import generate_opaque_token, hash_password, verify_password
from app.config import settings
from app.database.db import get_db
from app.models.refresh_token import PasswordResetToken, RefreshToken
from app.models.user import User
from app.rate_limiter import limiter
from app.schemas.auth import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import Message
from app.schemas.user import UserCreate, UserOut
from app.services.audit_service import log_action
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _issue_token_pair(db: Session, user: User) -> TokenResponse:
    access_token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})

    refresh_value = generate_opaque_token()
    refresh_row = RefreshToken(
        user_id=user.id,
        token=refresh_value,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_row)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_value, user=UserOut.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def register(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email is already registered.")

    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_action(db, user.id, "auth.register", "user", user.id, f"User {user.username} registered", request.client.host if request.client else None)
    return _issue_token_pair(db, user)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter((User.username == payload.identifier) | (User.email == payload.identifier))
        .first()
    )
    invalid_credentials = HTTPException(status_code=401, detail="Incorrect username/email or password.")
    if not user or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated.")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    log_action(db, user.id, "auth.login", "user", user.id, f"User {user.username} logged in", request.client.host if request.client else None)
    return _issue_token_pair(db, user)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_access_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    row = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    invalid = HTTPException(status_code=401, detail="Invalid or expired refresh token.")
    if not row or row.revoked:
        raise invalid
    if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise invalid

    user = db.query(User).filter(User.id == row.user_id).first()
    if not user or not user.is_active:
        raise invalid

    access_token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", response_model=Message)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    row = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if row:
        row.revoked = True
        db.commit()
    return Message(message="Logged out successfully.")


@router.post("/forgot-password", response_model=Message)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    generic_message = Message(message="If that email is registered, a password reset link has been sent.")

    if not user:
        # Avoid leaking whether the email exists.
        return generic_message

    token_value = generate_opaque_token()
    reset_row = PasswordResetToken(
        user_id=user.id,
        token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )
    db.add(reset_row)
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token_value}"
    send_password_reset_email(user.email, reset_link)
    return generic_message


@router.post("/reset-password", response_model=Message)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    row = db.query(PasswordResetToken).filter(PasswordResetToken.token == payload.token).first()
    invalid = HTTPException(status_code=400, detail="Invalid or expired reset token.")
    if not row or row.used:
        raise invalid
    if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise invalid

    user = db.query(User).filter(User.id == row.user_id).first()
    if not user:
        raise invalid

    user.password_hash = hash_password(payload.new_password)
    row.used = True
    # Force re-login on every device after a password reset.
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update({"revoked": True})
    db.commit()

    log_action(db, user.id, "auth.password_reset", "user", user.id, "Password reset via email token")
    return Message(message="Password has been reset. Please log in again.")


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
