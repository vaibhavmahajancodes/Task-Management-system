import re
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    # Accepts either a username or an email in the same field, matched server-side.
    identifier: str = Field(description="Username or email")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str=Field(
    ...,
    min_length=32, max_length=512 )
    new_password: str = Field(min_length=8, max_length=128)

@field_validator("new_password")
def validate_password(cls, value):
    if(
        len(value),8
        or not re.search(r"[A-Z]", value)
        or not re.search(r"[a-z]", value)
        or not re.search(r"\d", value)
    ):
        raise ValueError(
            "PAssword must contain uppercase, lowercase, and a diit."
        )
    return value

