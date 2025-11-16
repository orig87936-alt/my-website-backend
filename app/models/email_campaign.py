"""
Email campaign model for managing email campaigns
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, Text
from sqlalchemy.sql import func
import enum

from app.models.base import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"          # 草稿
    SCHEDULED = "scheduled"  # 已计划
    SENDING = "sending"      # 发送中
    SENT = "sent"           # 已发送
    FAILED = "failed"       # 失败


class EmailCampaign(Base):
    """
    Email campaign model
    
    Used for managing bulk email campaigns to subscribers.
    
    Attributes:
        id: Primary key
        name: Campaign name
        subject: Email subject
        content_html: Email HTML content
        content_text: Email plain text content
        subscription_type: Target subscription type (null = all)
        status: Campaign status
        scheduled_at: Scheduled send time
        sent_at: Actual send time
        total_recipients: Total number of recipients
        sent_count: Number of emails sent
        failed_count: Number of failed sends
        created_at: Creation timestamp
        updated_at: Update timestamp
    """
    __tablename__ = "email_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campaign info
    name = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    content_html = Column(Text, nullable=False)
    content_text = Column(Text, nullable=True)
    
    # Target audience
    subscription_type = Column(String(50), nullable=True)  # null = all subscribers
    
    # Status
    status = Column(SQLEnum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    total_recipients = Column(Integer, default=0, nullable=False)
    sent_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<EmailCampaign(id={self.id}, name={self.name}, status={self.status})>"

