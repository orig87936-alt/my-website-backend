"""
Authentication service for user registration, login, and token management
"""
from typing import Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests

from app.models.user import User, UserRole, AuthProvider
from app.models.refresh_token import RefreshToken
from app.core.security import create_access_token, create_refresh_token
from app.config import get_settings
from app.services.user import UserService

settings = get_settings()


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    async def register_user(
        db: AsyncSession,
        email: str,
        password: str,
        display_name: str
    ) -> User:
        """
        Register a new user
        
        Args:
            db: Database session
            email: User email
            password: User password
            display_name: User display name
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_user = await UserService.get_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注�?
            )
        
        # Create user
        user = await UserService.create_user(
            db=db,
            email=email,
            password=password,
            display_name=display_name,
            role=UserRole.VISITOR,
            auth_provider=AuthProvider.EMAIL,
            is_verified=True  # Already verified via email code
        )
        
        return user
    
    @staticmethod
    async def login_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Tuple[str, str, User]:
        """
        Login user with email and password
        
        Args:
            db: Database session
            email: User email
            password: User password
            
        Returns:
            Tuple of (access_token, refresh_token, user)
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Authenticate user
        user = await UserService.authenticate_user(db, email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错�?
            )
        
        # Update last login
        await UserService.update_last_login(db, user)
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value}
        )
        refresh_token_str = create_refresh_token()
        
        # Save refresh token to database
        await AuthService.save_refresh_token(db, user.id, refresh_token_str)
        
        return access_token, refresh_token_str, user
    
    @staticmethod
    async def login_admin(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Tuple[str, str, User]:
        """
        Login admin with username and password
        
        Args:
            db: Database session
            username: Admin username
            password: Admin password
            
        Returns:
            Tuple of (access_token, refresh_token, user)
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Authenticate admin
        user = await UserService.authenticate_admin(db, username, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # Update last login
        await UserService.update_last_login(db, user)
        
        # Create tokens
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value,
                "is_admin": True  # Admin login always sets is_admin to True
            }
        )
        refresh_token_str = create_refresh_token()
        
        # Save refresh token to database
        await AuthService.save_refresh_token(db, user.id, refresh_token_str)
        
        return access_token, refresh_token_str, user
    
    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token_str: str
    ) -> str:
        """
        Refresh access token using refresh token
        
        Args:
            db: Database session
            refresh_token_str: Refresh token string
            
        Returns:
            New access token
            
        Raises:
            HTTPException: If refresh token is invalid or expired
        """
        # Get refresh token from database
        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.token == refresh_token_str)
            .where(RefreshToken.is_revoked == False)
        )
        refresh_token = result.scalar_one_or_none()
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令�?
            )
        
        # Check if expired
        if refresh_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="刷新令牌已过�?
            )
        
        # Get user
        user = await UserService.get_by_id(db, refresh_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # Create new access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role.value
            }
        )
        
        return access_token
    
    @staticmethod
    async def logout(
        db: AsyncSession,
        refresh_token_str: str
    ) -> None:
        """
        Logout user by revoking refresh token
        
        Args:
            db: Database session
            refresh_token_str: Refresh token to revoke
        """
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        )
        refresh_token = result.scalar_one_or_none()
        
        if refresh_token:
            refresh_token.is_revoked = True
            await db.commit()
    
    @staticmethod
    async def save_refresh_token(
        db: AsyncSession,
        user_id: int,
        token: str
    ) -> RefreshToken:
        """
        Save refresh token to database
        
        Args:
            db: Database session
            user_id: User ID
            token: Refresh token string
            
        Returns:
            Created RefreshToken object
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            is_revoked=False
        )
        
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        
        return refresh_token
    
    @staticmethod
    async def revoke_all_user_tokens(
        db: AsyncSession,
        user_id: int
    ) -> None:
        """
        Revoke all refresh tokens for a user
        
        Args:
            db: Database session
            user_id: User ID
        """
        await db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        await db.commit()

    @staticmethod
    async def login_with_google(
        db: AsyncSession,
        google_token: str
    ) -> Tuple[str, str, User]:
        """
        Login or register user with Google OAuth

        Args:
            db: Database session
            google_token: Google ID token

        Returns:
            Tuple of (access_token, refresh_token, user)

        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Verify Google token
            # Note: In production, you should specify your Google Client ID
            # For now, we'll skip verification in development mode
            if settings.ENVIRONMENT == "development":
                # In development, we'll accept a mock token format: "google_mock_email@example.com"
                if google_token.startswith("google_mock_"):
                    email = google_token.replace("google_mock_", "")
                    google_user_info = {
                        "email": email,
                        "name": email.split("@")[0],
                        "picture": None
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Google token format for development mode"
                    )
            else:
                # Production: Verify real Google token
                # You need to set GOOGLE_CLIENT_ID in settings
                idinfo = id_token.verify_oauth2_token(
                    google_token,
                    requests.Request(),
                    settings.GOOGLE_CLIENT_ID
                )

                google_user_info = {
                    "email": idinfo.get("email"),
                    "name": idinfo.get("name"),
                    "picture": idinfo.get("picture")
                }

            email = google_user_info["email"]
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无法�?Google 获取邮箱信息"
                )

            # Check if user exists
            user = await UserService.get_by_email(db, email)

            if user:
                # User exists - update auth provider if needed
                if user.auth_provider != AuthProvider.GOOGLE:
                    user.auth_provider = AuthProvider.GOOGLE
                    if google_user_info.get("picture"):
                        user.avatar_url = google_user_info["picture"]
                    await db.commit()
                    await db.refresh(user)
            else:
                # Create new user
                user = User(
                    email=email,
                    display_name=google_user_info.get("name", email.split("@")[0]),
                    avatar_url=google_user_info.get("picture"),
                    role=UserRole.VISITOR,
                    auth_provider=AuthProvider.GOOGLE,
                    is_verified=True,  # Google accounts are pre-verified
                    is_active=True
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

            # Create tokens
            access_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": user.role.value
                }
            )

            refresh_token_str = create_refresh_token()

            # Save refresh token
            refresh_token = RefreshToken(
                user_id=user.id,
                token=refresh_token_str,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            )
            db.add(refresh_token)
            await db.commit()

            return access_token, refresh_token_str, user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google 登录失败: {str(e)}"
            )

