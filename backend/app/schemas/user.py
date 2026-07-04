from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_]+$)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
       if (
          len(value) < 8
          or not re.search(r"[A-Z]", value)
          or not re.search(r"[a-z]", value)
          or not re.search(r"\d", value)
          or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value)
       ):
          raise ValueError(
              "Password must contain uppercase, lowercase, number, and special character."
          )
    return value
    
     role: UserRole = UserRole.TEAM_MEMBER


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=100)
    job_title: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = None
    theme_preference: Optional[str] = Field(default=None, pattern="^(light|dark)$")


class UserRoleUpdate(BaseModel):
    role: UserRole


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    avatar_url: Optional[str] = None
    job_title: Optional[str] = None
    is_active: bool
    theme_preference: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserSummary(BaseModel):
    """Lightweight representation used when nesting a user inside other resources."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
