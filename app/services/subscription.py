"""
Subscription service for managing email subscriptions
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, or_
from fastapi import HTTPException, status

from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionType, SubscriptionFrequency
from app.core.security import generate_token
from app.services.email import EmailService


class SubscriptionService:
    """Service for subscription management operations"""
    
    @staticmethod
    async def create_subscription(
        db: AsyncSession,
        email: str,
        subscription_type: SubscriptionType = SubscriptionType.ALL,
        frequency: SubscriptionFrequency = SubscriptionFrequency.WEEKLY
    ) -> Subscription:
        """
        Create a new subscription
        
        Args:
            db: Database session
            email: Subscriber email
            subscription_type: Type of content to subscribe
            frequency: Email frequency
            
        Returns:
            Created subscription
            
        Raises:
            HTTPException: If email already subscribed
        """
        # Check if email already subscribed
        result = await db.execute(
            select(Subscription).where(Subscription.email == email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # If already active, update preferences
            if existing.status == SubscriptionStatus.ACTIVE:
                existing.subscription_type = subscription_type
                existing.frequency = frequency
                existing.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(existing)
                return existing

            # If unsubscribed, reactivate
            elif existing.status == SubscriptionStatus.UNSUBSCRIBED:
                existing.subscription_type = subscription_type
                existing.frequency = frequency
                existing.status = SubscriptionStatus.ACTIVE
                existing.confirmed_at = datetime.utcnow()
                existing.unsubscribed_at = None
                existing.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(existing)
                return existing

            # If pending, update and keep pending
            else:
                existing.subscription_type = subscription_type
                existing.frequency = frequency
                existing.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(existing)
                return existing

        # Generate tokens
        confirmation_token = generate_token()
        unsubscribe_token = generate_token()

        # Create subscription - directly set as ACTIVE (no email verification needed)
        subscription = Subscription(
            email=email,
            subscription_type=subscription_type,
            frequency=frequency,
            status=SubscriptionStatus.ACTIVE,  # Changed from PENDING to ACTIVE
            confirmation_token=confirmation_token,
            unsubscribe_token=unsubscribe_token,
            confirmed_at=datetime.utcnow()  # Set confirmation time
        )

        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

        # Email confirmation is disabled - subscription is immediately active
        # await EmailService.send_subscription_confirmation(
        #     to_email=email,
        #     confirmation_token=confirmation_token
        # )

        return subscription
    
    @staticmethod
    async def confirm_subscription(
        db: AsyncSession,
        token: str
    ) -> Subscription:
        """
        Confirm a subscription
        
        Args:
            db: Database session
            token: Confirmation token
            
        Returns:
            Confirmed subscription
            
        Raises:
            HTTPException: If token is invalid
        """
        result = await db.execute(
            select(Subscription).where(Subscription.confirmation_token == token)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="无效的确认链接"
            )
        
        if subscription.status == SubscriptionStatus.ACTIVE:
            return subscription  # Already confirmed
        
        # Update status
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.confirmed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(subscription)
        
        # Send welcome email
        await EmailService.send_subscription_welcome(
            to_email=subscription.email,
            subscription_type=subscription.subscription_type.value
        )
        
        return subscription
    
    @staticmethod
    async def unsubscribe(
        db: AsyncSession,
        token: str
    ) -> Subscription:
        """
        Unsubscribe from emails
        
        Args:
            db: Database session
            token: Unsubscribe token
            
        Returns:
            Unsubscribed subscription
            
        Raises:
            HTTPException: If token is invalid
        """
        result = await db.execute(
            select(Subscription).where(Subscription.unsubscribe_token == token)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="无效的退订链接"
            )
        
        if subscription.status == SubscriptionStatus.UNSUBSCRIBED:
            return subscription  # Already unsubscribed
        
        # Update status
        subscription.status = SubscriptionStatus.UNSUBSCRIBED
        subscription.unsubscribed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    async def get_subscriptions(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[SubscriptionStatus] = None,
        subscription_type: Optional[SubscriptionType] = None
    ) -> List[Subscription]:
        """
        Get subscriptions with filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            subscription_type: Filter by subscription type
            
        Returns:
            List of subscriptions
        """
        query = select(Subscription)
        
        # Apply filters
        filters = []
        if status:
            filters.append(Subscription.status == status)
        if subscription_type:
            filters.append(Subscription.subscription_type == subscription_type)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.offset(skip).limit(limit).order_by(Subscription.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_subscription_by_id(
        db: AsyncSession,
        subscription_id: int
    ) -> Optional[Subscription]:
        """Get subscription by ID"""
        result = await db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_subscription(
        db: AsyncSession,
        subscription_id: int,
        subscription_type: Optional[SubscriptionType] = None,
        frequency: Optional[SubscriptionFrequency] = None,
        status: Optional[SubscriptionStatus] = None
    ) -> Subscription:
        """
        Update subscription (admin only)
        
        Args:
            db: Database session
            subscription_id: Subscription ID
            subscription_type: New subscription type
            frequency: New frequency
            status: New status
            
        Returns:
            Updated subscription
            
        Raises:
            HTTPException: If subscription not found
        """
        subscription = await SubscriptionService.get_subscription_by_id(db, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订阅不存在"
            )
        
        # Update fields
        if subscription_type is not None:
            subscription.subscription_type = subscription_type
        if frequency is not None:
            subscription.frequency = frequency
        if status is not None:
            subscription.status = status
            if status == SubscriptionStatus.UNSUBSCRIBED:
                subscription.unsubscribed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    async def delete_subscription(
        db: AsyncSession,
        subscription_id: int
    ) -> bool:
        """
        Delete subscription (admin only)
        
        Args:
            db: Database session
            subscription_id: Subscription ID
            
        Returns:
            True if deleted
            
        Raises:
            HTTPException: If subscription not found
        """
        subscription = await SubscriptionService.get_subscription_by_id(db, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订阅不存在"
            )
        
        await db.delete(subscription)
        await db.commit()
        
        return True

