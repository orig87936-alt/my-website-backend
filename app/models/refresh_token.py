"""
Refresh token model for JWT token refresh
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class RefreshToken(Base):
    """
    Refresh token model for JWT authentication
    
    Stores refresh tokens to allow users to get new access tokens
    without re-authenticating. Tokens can be revoked for security.
    
    Attributes:
        id: Primary key
        token: Unique refresh token string
        user_id: Associated user ID
        is_revoked: Whether token has been revoked
        expires_at: Expiration timestamp (7 days from creation)
        created_at: Creation timestamp
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    
    # Token
    token = Column(String(500), unique=True, nullable=False, index=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Status
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"

