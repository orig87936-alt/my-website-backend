"""
Translation models for caching and logging
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.types import UUID


class TranslationCache(Base):
    """Translation cache model for storing translated text"""
    
    __tablename__ = "translation_cache"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source text hash (SHA-256) for quick lookup
    source_text_hash = Column(String(64), nullable=False, index=True)
    
    # Source and translated text
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    
    # Language codes (zh, en)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False, 
                       default=lambda: datetime.utcnow() + timedelta(days=30))
    
    # Composite unique constraint on hash + language pair
    __table_args__ = (
        Index('idx_translation_cache_hash', 'source_text_hash', 'source_lang', 'target_lang'),
        Index('idx_translation_cache_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<TranslationCache {self.source_lang}->{self.target_lang} hash={self.source_text_hash[:8]}>"


class TranslationLog(Base):
    """Translation log model for tracking translation history"""
    
    __tablename__ = "translation_logs"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to article (optional - can be null for non-article translations)
    article_id = Column(UUID, ForeignKey('articles.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # Field name that was translated (e.g., 'title', 'summary', 'content')
    field_name = Column(String(50), nullable=False)
    
    # Source and translated text
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    
    # Language codes
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    
    # Manual editing tracking
    manually_edited = Column(Boolean, nullable=False, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship to article (if applicable)
    # article = relationship("Article", back_populates="translation_logs")
    
    def __repr__(self):
        edited = " (edited)" if self.manually_edited else ""
        return f"<TranslationLog {self.field_name} {self.source_lang}->{self.target_lang}{edited}>"

