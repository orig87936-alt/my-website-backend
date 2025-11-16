"""
FAQ model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Index, text
from app.models.base import Base
from app.models.types import UUID


class FAQ(Base):
    """FAQ knowledge base model"""
    
    __tablename__ = "faqs"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Content
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False)  # Comma-separated keywords for SQLite compatibility
    
    # Organization
    category = Column(String(50), nullable=True)
    priority = Column(Integer, nullable=False, default=0, server_default="0")  # Higher = more important
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    
    # Usage tracking
    usage_count = Column(Integer, nullable=False, default=0, server_default="0")
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        # Index for keyword search
        Index("idx_faqs_keywords", "keywords"),
        # Index for active FAQs ordered by priority
        Index(
            "idx_faqs_priority_active",
            "priority"
        ),
    )
    
    def __repr__(self):
        return f"<FAQ(id={self.id}, question='{self.question[:50]}...', priority={self.priority}, is_active={self.is_active})>"

