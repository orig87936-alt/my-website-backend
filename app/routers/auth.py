"""
Authentication router for user registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.schemas.auth import (
    EmailLoginRequest, AdminLoginRequest, TokenResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    SendVerificationCodeRequest, VerifyCodeRequest, VerifyCodeResponse,
    PasswordResetRequest, GoogleLoginRequest
)
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.services.verification import VerificationService
from app.services.user import UserService
from app.core.deps import get_current_active_user, require_admin
from app.models.user import User
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


# ============================================================================
# Registration and Login
# ============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user

    **Request Body:**
    - **email**: User email address
    - **password**: User password (min 8 chars)
    - **display_name**: User display name
    - **verification_code**: (Optional) 6-digit code from email

    **Response:**
    - **access_token**: JWT access token
    - **refresh_token**: Refresh token for getting new access tokens
    - **token_type**: "bearer"
    - **expires_in**: Token expiration time in seconds
    - **user**: User information
    """
    # Verify email code if provided
    if user_data.verification_code:
        is_valid = await VerificationService.verify_code(
            db, user_data.email, user_data.verification_code, "register"
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码无效或已过期"
            )

    # Register user
    user = await AuthService.register_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        display_name=user_data.display_name
    )

    # Login user
    access_token, refresh_token, user = await AuthService.login_user(
        db=db,
        email=user_data.email,
        password=user_data.password
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(
    request: Request,
    login_data: EmailLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password

    **Request Body:**
    - **email**: User email address
    - **password**: User password

    **Response:**
    - **access_token**: JWT access token
    - **refresh_token**: Refresh token
    - **token_type**: "bearer"
    - **expires_in**: Token expiration time in seconds
    - **user**: User information
    """
    access_token, refresh_token, user = await AuthService.login_user(
        db=db,
        email=login_data.email,
        password=login_data.password
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/admin-login", response_model=TokenResponse)
@limiter.limit("3/minute")  # Stricter limit for admin login
async def admin_login(
    request: Request,
    login_data: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Admin login with username and password

    **Request Body:**
    - **username**: Admin username
    - **password**: Admin password

    **Response:**
    - **access_token**: JWT access token
    - **refresh_token**: Refresh token
    - **token_type**: "bearer"
    - **expires_in**: Token expiration time in seconds
    - **user**: Admin user information
    """
    access_token, refresh_token, user = await AuthService.login_admin(
        db=db,
        username=login_data.username,
        password=login_data.password
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/google/token", response_model=TokenResponse)
async def google_login(
    login_data: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login or register with Google OAuth

    **Request Body:**
    - **token**: Google ID token from Google Sign-In

    **Response:**
    - **access_token**: JWT access token
    - **refresh_token**: Refresh token
    - **token_type**: "bearer"
    - **expires_in**: Token expiration time in seconds
    - **user**: User information

    **Notes:**
    - If user doesn't exist, a new account will be created automatically
    - Google accounts are pre-verified
    - In development mode, use token format: "google_mock_email@example.com"
    """
    access_token, refresh_token, user = await AuthService.login_with_google(
        db=db,
        google_token=login_data.token
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/google/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def google_signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register with Google-style signup (email + password, no verification)

    **Request Body:**
    - **email**: Email address
    - **password**: Password (min 8 characters)
    - **display_name**: Optional display name

    **Response:**
    - **access_token**: JWT access token
    - **refresh_token**: Refresh token
    - **token_type**: "bearer"
    - **expires_in**: Token expiration time in seconds
    - **user**: User information

    **Notes:**
    - No email verification required
    - Account is created and activated immediately
    - Auth provider is set to GOOGLE
    """
    # Check if user already exists
    existing_user = await UserService.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册" if user_data.email else "Email already registered"
        )

    # Create user directly without verification
    user = await UserService.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        display_name=user_data.display_name or user_data.email.split('@')[0],
        auth_provider=AuthProvider.GOOGLE,
        is_verified=True,  # No verification needed
        is_active=True
    )

    # Create tokens
    access_token, refresh_token = await AuthService.create_user_tokens(db, user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


# ============================================================================
# Token Management
# ============================================================================

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token

    **Request Body:**
    - **refresh_token**: Refresh token string

    **Response:**
    - **access_token**: New JWT access token
    - **token_type**: "bearer"
    - **expires_in**: Token expiration time in seconds
    """
    access_token = await AuthService.refresh_access_token(
        db=db,
        refresh_token_str=refresh_data.refresh_token
    )

    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user by revoking refresh token

    **Request Body:**
    - **refresh_token**: Refresh token to revoke

    **Response:**
    - 204 No Content
    """
    await AuthService.logout(db=db, refresh_token_str=refresh_data.refresh_token)
    return None


# ============================================================================
# User Profile
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    **Response:**
    - User information
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile

    **Request Body:**
    - **display_name**: New display name (optional)
    - **avatar_url**: New avatar URL (optional)

    **Response:**
    - Updated user information
    """
    updated_user = await UserService.update_user(
        db=db,
        user=current_user,
        display_name=user_update.display_name,
        avatar_url=user_update.avatar_url
    )

    return UserResponse.model_validate(updated_user)


# ============================================================================
# Email Verification
# ============================================================================

@router.post("/verification/send", response_model=dict)
@limiter.limit("3/minute")  # Max 3 verification codes per minute
async def send_verification_code(
    http_request: Request,
    request: SendVerificationCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send verification code to email

    **Request Body:**
    - **email**: Email address
    - **purpose**: Verification purpose (register/reset/change)

    **Response:**
    - **success**: True
    - **message**: Success message
    """
    # Check if email already exists (for registration)
    if request.purpose == "register":
        existing_user = await UserService.get_by_email(db, request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册"
            )

    # Send verification code
    code = await VerificationService.send_verification_code(
        db=db,
        email=request.email,
        purpose=request.purpose
    )

    return {
        "success": True,
        "message": "验证码已发送到您的邮箱，有效期10分钟"
    }


@router.post("/verification/verify", response_model=VerifyCodeResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email verification code

    **Request Body:**
    - **email**: Email address
    - **code**: 6-digit verification code
    - **purpose**: Verification purpose

    **Response:**
    - **success**: True if valid, False otherwise
    - **message**: Result message
    """
    is_valid = await VerificationService.verify_code(
        db=db,
        email=request.email,
        code=request.code,
        purpose=request.purpose
    )

    if is_valid:
        return VerifyCodeResponse(
            success=True,
            message="验证成功"
        )
    else:
        return VerifyCodeResponse(
            success=False,
            message="验证码无效或已过期"
        )


# ============================================================================
# Password Reset
# ============================================================================

@router.post("/password/reset", response_model=dict)
async def reset_password(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using verification code

    **Flow:**
    1. User requests code via `/verification/send` with purpose="reset"
    2. User receives code via email
    3. User submits new password with code

    **Request Body:**
    - **email**: User email
    - **code**: 6-digit verification code
    - **new_password**: New password

    **Response:**
    - **success**: True
    - **message**: Success message
    """
    # Verify code
    is_valid = await VerificationService.verify_code(
        db=db,
        email=reset_data.email,
        code=reset_data.code,
        purpose="reset"
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码无效或已过期"
        )

    # Get user
    user = await UserService.get_by_email(db, reset_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # Reset password
    await UserService.reset_password(db, user, reset_data.new_password)

    # Revoke all existing tokens
    await AuthService.revoke_all_user_tokens(db, user.id)

    return {
        "success": True,
        "message": "密码重置成功，请使用新密码登录"
    }

