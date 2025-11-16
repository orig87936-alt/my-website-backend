"""
User schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole, AuthProvider


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: Optional[EmailStr] = None
    display_name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    verification_code: Optional[str] = Field(None, min_length=6, max_length=6)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserUpdatePassword(BaseModel):
    """Schema for updating password"""
    old_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(c.isalpha() for c in v):
            raise ValueError('密码必须包含字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v


# Response schemas
class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: Optional[str] = None
    email: Optional[str] = None
    display_name: str
    avatar_url: Optional[str] = None
    role: UserRole
    auth_provider: AuthProvider
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    """Schema for public user info (limited fields)"""
    id: int
    display_name: str
    avatar_url: Optional[str] = None
    
    model_config = {"from_attributes": True}

