"""
Subscription schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionType, SubscriptionFrequency, SubscriptionStatus


# Request schemas
class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    email: EmailStr
    subscription_type: SubscriptionType = SubscriptionType.ALL
    frequency: SubscriptionFrequency = SubscriptionFrequency.WEEKLY


class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription (admin only)"""
    subscription_type: Optional[SubscriptionType] = None
    frequency: Optional[SubscriptionFrequency] = None
    status: Optional[SubscriptionStatus] = None


# Response schemas
class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: int
    email: str
    subscription_type: SubscriptionType
    frequency: SubscriptionFrequency
    status: SubscriptionStatus
    confirmed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    last_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubscriptionPublicResponse(BaseModel):
    """Schema for public subscription response (limited fields)"""
    success: bool
    message: str
    email: str


class SubscriptionConfirmResponse(BaseModel):
    """Schema for subscription confirmation response"""
    success: bool
    message: str


class SubscriptionUnsubscribeResponse(BaseModel):
    """Schema for unsubscribe response"""
    success: bool
    message: str


# List and pagination schemas
class SubscriptionListQuery(BaseModel):
    """Schema for subscription list query parameters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    status: Optional[SubscriptionStatus] = None
    subscription_type: Optional[SubscriptionType] = None
    search: Optional[str] = Field(None, max_length=255, description="Search by email")


class SubscriptionListResponse(BaseModel):
    """Schema for subscription list response"""
    total: int
    page: int
    page_size: int
    items: list[SubscriptionResponse]


# Statistics schemas
class SubscriptionStatsResponse(BaseModel):
    """Schema for subscription statistics"""
    total_subscriptions: int
    active_subscriptions: int
    pending_subscriptions: int
    unsubscribed_count: int
    by_type: dict[str, int]
    by_frequency: dict[str, int]

