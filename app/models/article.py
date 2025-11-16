"""
Article model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, CheckConstraint, Index, text
from app.models.base import Base
from app.models.types import UUID, JSONB


class Article(Base):
    """Article model with multilingual content"""
    
    __tablename__ = "articles"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Category and status
    category = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="published", server_default="published")
    
    # Titles
    title_zh = Column(Text, nullable=False)
    title_en = Column(Text, nullable=False)
    
    # Summaries (no length limit - using Text type)
    summary_zh = Column(Text, nullable=False)
    summary_en = Column(Text, nullable=False)
    
    # Lead paragraphs
    lead_zh = Column(Text, nullable=True)
    lead_en = Column(Text, nullable=True)
    
    # Content (JSONB/JSON array of content blocks)
    content_zh = Column(JSONB, nullable=False)
    content_en = Column(JSONB, nullable=False)
    
    # Image
    image_url = Column(Text, nullable=True)
    image_caption_zh = Column(Text, nullable=True)
    image_caption_en = Column(Text, nullable=True)
    
    # Metadata
    author = Column(String(100), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "category IN ('headline', 'regulatory', 'analysis', 'business', 'enterprise', 'outlook')",
            name="valid_category"
        ),
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="valid_status"
        ),
        Index("idx_articles_category_published", "category", "published_at"),
    )
    
    def __repr__(self):
        return f"<Article(id={self.id}, title_zh='{self.title_zh[:30]}...', category='{self.category}')>"

