from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=13, description="用户名")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=20, description="密码，至少8位")

class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class UserResponse(BaseModel):
    id: UUID
    username: str
    created_at: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class AuthResponse(BaseModel):
    message: str
    user: dict
    token: Optional[Token] = None