from pydantic import BaseModel, EmailStr, Field

from app.domain.auth import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    role: UserRole
