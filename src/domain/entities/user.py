from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserBase(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    role: UserRole = UserRole.USER
    branch: int = Field(..., ge=1, le=100)

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Сырой пароль")

class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    branch: Optional[int] = Field(None, ge=1, le=100)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

UserCreate.model_rebuild()
UserUpdate.model_rebuild()
UserResponse.model_rebuild()