"""
Email verification service for sending and verifying codes
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from fastapi import HTTPException, status

from app.models.email_verification import EmailVerification
from app.core.security import generate_verification_code
from app.services.email import EmailService


class VerificationService:
    """Service for email verification operations"""
    
    @staticmethod
    async def send_verification_code(
        db: AsyncSession,
        email: str,
        purpose: str = "register",
        user_id: Optional[int] = None
    ) -> str:
        """
        Send verification code to email
        
        Args:
            db: Database session
            email: Email address
            purpose: Verification purpose (register/reset/change)
            user_id: Optional user ID for existing users
            
        Returns:
            Verification code (for testing purposes)
        """
        # Generate code
        code = generate_verification_code()
        
        # Delete old codes for this email and purpose
        await db.execute(
            delete(EmailVerification)
            .where(EmailVerification.email == email)
            .where(EmailVerification.purpose == purpose)
            .where(EmailVerification.is_used == False)
        )
        
        # Create verification record
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        verification = EmailVerification(
            email=email,
            code=code,
            user_id=user_id,
            purpose=purpose,
            expires_at=expires_at,
            is_used=False
        )
        
        db.add(verification)
        await db.commit()
        
        # Send email
        try:
            await EmailService.send_verification_code(email, code, purpose)
        except Exception as e:
            # Log error but don't fail the request
            print(f"Failed to send verification email: {e}")
        
        return code
    
    @staticmethod
    async def verify_code(
        db: AsyncSession,
        email: str,
        code: str,
        purpose: str = "register"
    ) -> bool:
        """
        Verify email verification code
        
        Args:
            db: Database session
            email: Email address
            code: Verification code
            purpose: Verification purpose
            
        Returns:
            True if code is valid, False otherwise
        """
        # Get verification record
        result = await db.execute(
            select(EmailVerification)
            .where(EmailVerification.email == email)
            .where(EmailVerification.code == code)
            .where(EmailVerification.purpose == purpose)
            .where(EmailVerification.is_used == False)
            .order_by(EmailVerification.created_at.desc())
        )
        verification = result.scalar_one_or_none()
        
        if not verification:
            return False
        
        # Check if expired
        if verification.expires_at < datetime.utcnow():
            return False
        
        # Mark as used
        verification.is_used = True
        await db.commit()
        
        return True
    
    @staticmethod
    async def cleanup_expired_codes(db: AsyncSession) -> int:
        """
        Clean up expired verification codes
        
        Args:
            db: Database session
            
        Returns:
            Number of deleted records
        """
        result = await db.execute(
            delete(EmailVerification)
            .where(EmailVerification.expires_at < datetime.utcnow())
        )
        await db.commit()
        
        return result.rowcount

