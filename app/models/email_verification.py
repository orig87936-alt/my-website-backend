"""
Email verification model for email verification codes
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class EmailVerification(Base):
    """
    Email verification code model
    
    Used for:
    - User registration email verification
    - Password reset verification
    - Email change verification
    
    Attributes:
        id: Primary key
        email: Email address to verify
        code: 6-digit verification code
        user_id: Associated user ID (nullable for new registrations)
        purpose: Verification purpose (register/reset/change)
        is_used: Whether code has been used
        expires_at: Expiration timestamp (10 minutes from creation)
        created_at: Creation timestamp
    """
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    
    # Email and code
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    
    # User association (nullable for new registrations)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Purpose: register, reset, change
    purpose = Column(String(20), nullable=False, default="register")
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="email_verifications")
    
    def __repr__(self):
        return f"<EmailVerification(id={self.id}, email={self.email}, purpose={self.purpose})>"

