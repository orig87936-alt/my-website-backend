"""
Subscription model for email subscriptions
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class SubscriptionType(str, enum.Enum):
    """Subscription type enumeration"""
    ALL = "all"                    # 所有更新
    HEADLINE = "headline"          # 头条新闻
    REGULATORY = "regulatory"      # 监管动态
    ANALYSIS = "analysis"          # 深度分析
    BUSINESS = "business"          # 商业资讯
    ENTERPRISE = "enterprise"      # 企业动态
    OUTLOOK = "outlook"            # 市场展望


class SubscriptionFrequency(str, enum.Enum):
    """Subscription frequency enumeration"""
    DAILY = "daily"        # 每日
    WEEKLY = "weekly"      # 每周
    MONTHLY = "monthly"    # 每月


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enumeration"""
    PENDING = "pending"        # 待确认
    ACTIVE = "active"          # 已激活
    UNSUBSCRIBED = "unsubscribed"  # 已退订


class Subscription(Base):
    """
    Email subscription model
    
    Attributes:
        id: Primary key
        email: Subscriber email address
        subscription_type: Type of content to subscribe
        frequency: Email frequency
        status: Subscription status
        confirmation_token: Token for email confirmation
        unsubscribe_token: Token for unsubscribe link
        confirmed_at: Confirmation timestamp
        unsubscribed_at: Unsubscribe timestamp
        last_sent_at: Last email sent timestamp
        created_at: Creation timestamp
        updated_at: Update timestamp
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Subscriber info
    email = Column(String(255), nullable=False, index=True)
    
    # Subscription preferences
    subscription_type = Column(SQLEnum(SubscriptionType), nullable=False, default=SubscriptionType.ALL)
    frequency = Column(SQLEnum(SubscriptionFrequency), nullable=False, default=SubscriptionFrequency.WEEKLY)
    
    # Status
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.PENDING)
    
    # Tokens
    confirmation_token = Column(String(255), unique=True, nullable=False, index=True)
    unsubscribe_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Timestamps
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    last_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    logs = relationship("SubscriptionLog", back_populates="subscription", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, email={self.email}, status={self.status})>"


class SubscriptionLog(Base):
    """
    Subscription activity log
    
    Tracks all subscription-related activities:
    - Subscription creation
    - Email confirmation
    - Email sent
    - Unsubscribe
    
    Attributes:
        id: Primary key
        subscription_id: Associated subscription ID
        action: Action type (created/confirmed/sent/unsubscribed)
        details: Additional details (JSON)
        ip_address: User IP address
        user_agent: User agent string
        created_at: Creation timestamp
    """
    __tablename__ = "subscription_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Association
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Action info
    action = Column(String(50), nullable=False)  # created, confirmed, sent, unsubscribed
    details = Column(Text, nullable=True)  # JSON string for additional info
    
    # Request info
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="logs")
    
    def __repr__(self):
        return f"<SubscriptionLog(id={self.id}, action={self.action})>"

