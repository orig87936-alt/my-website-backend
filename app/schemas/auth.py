"""
Authentication schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.schemas.user import UserResponse


# Login schemas
class EmailLoginRequest(BaseModel):
    """Schema for email login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class AdminLoginRequest(BaseModel):
    """Schema for admin login"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class GoogleLoginRequest(BaseModel):
    """Schema for Google OAuth login"""
    token: str = Field(..., description="Google ID token")


# Token schemas
class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


# Verification schemas
class SendVerificationCodeRequest(BaseModel):
    """Schema for sending verification code"""
    email: EmailStr
    purpose: str = Field(default="register", pattern="^(register|reset|change)$")


class VerifyCodeRequest(BaseModel):
    """Schema for verifying code"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    purpose: str = Field(default="register", pattern="^(register|reset|change)$")


class VerifyCodeResponse(BaseModel):
    """Schema for verification code response"""
    success: bool
    message: str


# Password reset schemas
class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=100)


# Google OAuth schemas
class GoogleAuthUrlResponse(BaseModel):
    """Schema for Google OAuth URL response"""
    auth_url: str


class GoogleCallbackRequest(BaseModel):
    """Schema for Google OAuth callback"""
    code: str
    state: Optional[str] = None


# Legacy schemas (for backward compatibility)
class LoginRequest(BaseModel):
    """Login request schema (legacy)"""
    username: str = Field(..., min_length=1, max_length=100, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class Token(BaseModel):
    """JWT token response schema (legacy)"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_admin: bool = False

