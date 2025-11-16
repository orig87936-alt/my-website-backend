"""
User service for user management operations
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.user import User, UserRole, AuthProvider
from app.core.security import hash_password, verify_password


class UserService:
    """Service for user management"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_google_id(db: AsyncSession, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        result = await db.execute(
            select(User).where(User.google_id == google_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        password: str,
        display_name: str,
        role: UserRole = UserRole.VISITOR,
        auth_provider: AuthProvider = AuthProvider.EMAIL,
        is_verified: bool = False,
        google_id: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Create a new user"""
        hashed_password = hash_password(password) if password else None
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            display_name=display_name,
            role=role,
            auth_provider=auth_provider,
            is_verified=is_verified,
            google_id=google_id,
            avatar_url=avatar_url,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def create_admin(
        db: AsyncSession,
        username: str,
        password: str,
        email: str,
        display_name: str
    ) -> User:
        """Create an admin user"""
        hashed_password = hash_password(password)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            display_name=display_name,
            role=UserRole.ADMIN,
            auth_provider=AuthProvider.USERNAME,
            is_verified=True,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user: User,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """Update user profile"""
        if display_name is not None:
            user.display_name = display_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_password(
        db: AsyncSession,
        user: User,
        old_password: str,
        new_password: str
    ) -> bool:
        """Update user password"""
        # Verify old password
        if not user.hashed_password or not verify_password(old_password, user.hashed_password):
            return False
        
        # Update password
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return True
    
    @staticmethod
    async def reset_password(
        db: AsyncSession,
        user: User,
        new_password: str
    ) -> User:
        """Reset user password (without old password verification)"""
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def verify_email(db: AsyncSession, user: User) -> User:
        """Mark user email as verified"""
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> User:
        """Update user's last login timestamp"""
        user.last_login_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user by email and password"""
        user = await UserService.get_by_email(db, email)
        
        if not user:
            return None
        
        if not user.hashed_password:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    async def authenticate_admin(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate admin by username and password"""
        user = await UserService.get_by_username(db, username)
        
        if not user:
            return None
        
        if user.role != UserRole.ADMIN:
            return None
        
        if not user.hashed_password:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user

