"""
User model for authentication and authorization
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    VISITOR = "VISITOR"      # 访客（注册用户）
    USER = "USER"           # 普通用户
    ADMIN = "ADMIN"         # 管理员


class AuthProvider(str, enum.Enum):
    """Authentication provider enumeration"""
    EMAIL = "EMAIL"         # 邮箱密码登录
    GOOGLE = "GOOGLE"       # Google OAuth
    USERNAME = "USERNAME"   # 用户名密码登录（管理员）


class User(Base):
    """
    User model for both admin and registered users
    
    Attributes:
        id: Primary key
        username: Username (required for admin, optional for users)
        email: Email address (required for email/google auth)
        hashed_password: Bcrypt hashed password
        display_name: Display name / nickname
        avatar_url: User avatar URL
        role: User role (visitor/user/admin)
        auth_provider: Authentication provider
        google_id: Google account ID (for OAuth)
        is_active: Whether user is active
        is_verified: Whether email is verified
        last_login_at: Last login timestamp
        created_at: Creation timestamp
        updated_at: Update timestamp
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    username = Column(String(50), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=True)
    
    # Profile fields
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    # Role and provider
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VISITOR)
    auth_provider = Column(SQLEnum(AuthProvider), nullable=False, default=AuthProvider.EMAIL)
    
    # OAuth fields
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    email_verifications = relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

