from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: Optional[UserRole] = UserRole.TEAM_MEMBER


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    job_title: Optional[str] = None
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
