"""
Translation schemas for request/response validation
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Translation request schemas
class TranslateRequest(BaseModel):
    """Request schema for single field translation"""
    text: str = Field(..., min_length=1, max_length=50000, description="Text to translate (up to 50000 characters)")
    source_lang: Optional[str] = Field(None, pattern="^(zh|en)$", description="Source language (auto-detect if not provided)")
    target_lang: str = Field(..., pattern="^(zh|en)$", description="Target language")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class BatchTranslateField(BaseModel):
    """Single field in batch translation request"""
    field_name: str = Field(..., min_length=1, max_length=50, description="Field name (e.g., 'title', 'summary')")
    text: str = Field(..., min_length=1, max_length=50000, description="Text to translate (up to 50000 characters)")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class BatchTranslateRequest(BaseModel):
    """Request schema for batch translation"""
    fields: List[BatchTranslateField] = Field(..., min_length=1, max_length=10, description="Fields to translate")
    source_lang: Optional[str] = Field(None, pattern="^(zh|en)$", description="Source language (auto-detect if not provided)")
    target_lang: str = Field(..., pattern="^(zh|en)$", description="Target language")
    article_id: Optional[UUID] = Field(None, description="Article ID for logging (optional)")


class DetectLanguageRequest(BaseModel):
    """Request schema for language detection"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to detect language")


# Translation response schemas
class TranslateResponse(BaseModel):
    """Response schema for single field translation"""
    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Detected or provided source language")
    target_lang: str = Field(..., description="Target language")
    cached: bool = Field(..., description="Whether result was from cache")
    
    model_config = {"from_attributes": True}


class BatchTranslateFieldResult(BaseModel):
    """Single field result in batch translation response"""
    field_name: str = Field(..., description="Field name")
    translated_text: str = Field(..., description="Translated text")
    cached: bool = Field(..., description="Whether result was from cache")


class BatchTranslateResponse(BaseModel):
    """Response schema for batch translation"""
    results: List[BatchTranslateFieldResult] = Field(..., description="Translation results")
    source_lang: str = Field(..., description="Detected or provided source language")
    target_lang: str = Field(..., description="Target language")
    total_fields: int = Field(..., description="Total number of fields translated")
    cached_count: int = Field(..., description="Number of results from cache")
    
    model_config = {"from_attributes": True}


class DetectLanguageResponse(BaseModel):
    """Response schema for language detection"""
    detected_lang: str = Field(..., description="Detected language code")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence (0-1)")
    
    model_config = {"from_attributes": True}


# Translation log schemas
class TranslationLogBase(BaseModel):
    """Base schema for translation log"""
    article_id: Optional[UUID] = Field(None, description="Article ID")
    field_name: str = Field(..., description="Field name")
    source_text: str = Field(..., description="Source text")
    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Source language")
    target_lang: str = Field(..., description="Target language")
    manually_edited: bool = Field(default=False, description="Whether translation was manually edited")
    edited_at: Optional[datetime] = Field(None, description="When translation was edited")


class TranslationLogCreate(TranslationLogBase):
    """Schema for creating translation log"""
    pass


class TranslationLogResponse(TranslationLogBase):
    """Response schema for translation log"""
    id: UUID = Field(..., description="Log ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = {"from_attributes": True}


class TranslationHistoryResponse(BaseModel):
    """Response schema for translation history"""
    items: List[TranslationLogResponse] = Field(..., description="Translation log items")
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Offset")
    
    model_config = {"from_attributes": True}


# Translation cache schemas (for internal use)
class TranslationCacheBase(BaseModel):
    """Base schema for translation cache"""
    source_text_hash: str = Field(..., description="SHA-256 hash of source text")
    source_text: str = Field(..., description="Source text")
    translated_text: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Source language")
    target_lang: str = Field(..., description="Target language")


class TranslationCacheCreate(TranslationCacheBase):
    """Schema for creating translation cache entry"""
    pass


class TranslationCacheResponse(TranslationCacheBase):
    """Response schema for translation cache"""
    id: UUID = Field(..., description="Cache ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    
    model_config = {"from_attributes": True}

