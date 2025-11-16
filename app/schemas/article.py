"""
Article schemas for request/response validation
"""
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Content block schema
class ContentBlock(BaseModel):
    """Content block for article content"""
    type: str = Field(..., description="Block type: paragraph, heading, list, quote, code, image, markdown")
    text: Optional[str] = Field(None, description="Block text content")
    content: Optional[str] = Field(None, description="Block content (deprecated, use 'text')")
    level: Optional[int] = Field(None, description="Heading level (1-6) for heading type")
    items: Optional[List[str]] = Field(None, description="List items for list type")
    language: Optional[str] = Field(None, description="Code language for code type")
    url: Optional[str] = Field(None, description="Image URL for image type")
    caption: Optional[str] = Field(None, description="Image caption for image type")
    width: Optional[int] = Field(None, description="Image width in pixels for image type")
    height: Optional[int] = Field(None, description="Image height in pixels for image type")

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        allowed_types = ['paragraph', 'heading', 'list', 'quote', 'code', 'image', 'markdown']
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}")
        return v

    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        if v is not None and (v < 1 or v > 6):
            raise ValueError("level must be between 1 and 6")
        return v


# Base article schema
class ArticleBase(BaseModel):
    """Base article schema with common fields"""
    category: str = Field(..., description="Article category")
    status: str = Field(default="published", description="Article status")
    title_zh: str = Field(..., min_length=1, max_length=500, description="Chinese title")
    title_en: str = Field(..., min_length=1, max_length=500, description="English title")
    summary_zh: str = Field(..., min_length=1, description="Chinese summary")
    summary_en: str = Field(..., min_length=1, description="English summary")
    lead_zh: Optional[str] = Field(None, description="Chinese lead paragraph")
    lead_en: Optional[str] = Field(None, description="English lead paragraph")
    image_url: Optional[str] = Field(None, description="Article image URL")
    image_caption_zh: Optional[str] = Field(None, description="Chinese image caption")
    image_caption_en: Optional[str] = Field(None, description="English image caption")
    author: Optional[str] = Field(None, max_length=100, description="Article author")
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        allowed_categories = ['headline', 'regulatory', 'analysis', 'business', 'enterprise', 'outlook']
        if v not in allowed_categories:
            raise ValueError(f"category must be one of {allowed_categories}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        allowed_statuses = ['draft', 'published', 'archived']
        if v not in allowed_statuses:
            raise ValueError(f"status must be one of {allowed_statuses}")
        return v


# Create article schema
class ArticleCreate(ArticleBase):
    """Schema for creating a new article"""
    content_zh: List[ContentBlock] = Field(..., description="Chinese content blocks")
    content_en: List[ContentBlock] = Field(..., description="English content blocks")
    published_at: Optional[datetime] = Field(None, description="Publication date (defaults to now)")


# Update article schema
class ArticleUpdate(BaseModel):
    """Schema for updating an article (all fields optional)"""
    category: Optional[str] = None
    status: Optional[str] = None
    title_zh: Optional[str] = Field(None, min_length=1, max_length=500)
    title_en: Optional[str] = Field(None, min_length=1, max_length=500)
    summary_zh: Optional[str] = Field(None, min_length=1)
    summary_en: Optional[str] = Field(None, min_length=1)
    lead_zh: Optional[str] = None
    lead_en: Optional[str] = None
    content_zh: Optional[List[ContentBlock]] = None
    content_en: Optional[List[ContentBlock]] = None
    image_url: Optional[str] = None
    image_caption_zh: Optional[str] = None
    image_caption_en: Optional[str] = None
    author: Optional[str] = Field(None, max_length=100)
    published_at: Optional[datetime] = None
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None:
            allowed_categories = ['headline', 'regulatory', 'analysis', 'business', 'enterprise', 'outlook']
            if v not in allowed_categories:
                raise ValueError(f"category must be one of {allowed_categories}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['draft', 'published', 'archived']
            if v not in allowed_statuses:
                raise ValueError(f"status must be one of {allowed_statuses}")
        return v


# Article response schema (simplified for list view)
class ArticleListItem(BaseModel):
    """Simplified article schema for list view"""
    id: UUID
    category: str
    status: str
    title_zh: str
    title_en: str
    summary_zh: str
    summary_en: str
    image_url: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Full article response schema
class ArticleResponse(ArticleListItem):
    """Full article schema with content"""
    lead_zh: Optional[str] = None
    lead_en: Optional[str] = None
    content_zh: List[Any]  # JSONB content blocks
    content_en: List[Any]  # JSONB content blocks
    image_caption_zh: Optional[str] = None
    image_caption_en: Optional[str] = None
    
    class Config:
        from_attributes = True


# Paginated article list response
class ArticleListResponse(BaseModel):
    """Paginated list of articles"""
    items: List[ArticleListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1


# Related articles response (for article bottom navigation)
class RelatedArticlesResponse(BaseModel):
    """Related articles for article bottom navigation"""
    articles: List[ArticleListItem]
    total: int
    has_more: bool  # True if there are more than 6 articles

