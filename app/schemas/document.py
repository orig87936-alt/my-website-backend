"""
Document upload schemas for request/response validation
"""
from datetime import datetime
from typing import List, Optional, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.article import ContentBlock


# Document upload request schemas
class UploadDocumentRequest(BaseModel):
    """Request schema for document upload (multipart form data)"""
    category: Optional[str] = Field(None, description="Article category")
    auto_translate: bool = Field(default=False, description="Whether to auto-translate after parsing")
    target_lang: str = Field(default="en", pattern="^(zh|en)$", description="Target language for translation")


# Uploaded image info
class UploadedImage(BaseModel):
    """Schema for uploaded image information"""
    original_name: str = Field(..., description="Original image filename")
    uploaded_url: str = Field(..., description="Uploaded image URL")
    size: int = Field(..., description="Image size in bytes")


# Parse metadata
class ParseMetadata(BaseModel):
    """Schema for document parse metadata"""
    word_count: int = Field(..., description="Total word count")
    paragraph_count: int = Field(..., description="Number of paragraphs")
    image_count: int = Field(..., description="Number of images")
    parse_time: float = Field(..., description="Parse time in seconds")
    translation_time: Optional[float] = Field(None, description="Translation time in seconds (if translated)")


# Parse result
class ParseResult(BaseModel):
    """Schema for document parse result"""
    title: str = Field(..., description="Extracted or generated title (Chinese)")
    title_en: Optional[str] = Field(None, description="Translated title (English, if auto_translate=true)")
    summary: str = Field(..., description="Auto-generated summary (50-80 chars, Chinese)")
    summary_en: Optional[str] = Field(None, description="Translated summary (English, if auto_translate=true)")
    category: str = Field(..., description="Suggested or provided category")
    tags: List[str] = Field(default_factory=list, description="Auto-extracted tags")
    content_zh: List[ContentBlock] = Field(..., description="Parsed content in Chinese")
    content_en: Optional[List[ContentBlock]] = Field(None, description="Translated content in English (if auto_translate=true)")
    images_uploaded: List[UploadedImage] = Field(default_factory=list, description="Uploaded images")
    metadata: ParseMetadata = Field(..., description="Parse metadata")


# Document upload response schemas
class UploadDocumentResponse(BaseModel):
    """Response schema for document upload"""
    upload_id: UUID = Field(..., description="Upload ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (md/docx)")
    file_size: int = Field(..., description="File size in bytes")
    parse_result: ParseResult = Field(..., description="Parse result")
    status: str = Field(..., description="Upload status (success/failed)")
    created_at: datetime = Field(..., description="Upload timestamp")
    
    model_config = {"from_attributes": True}


# Document upload history schemas
class DocumentUploadHistoryItem(BaseModel):
    """Schema for document upload history item"""
    id: UUID = Field(..., description="Upload ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (md/docx)")
    file_size: int = Field(..., description="File size in bytes")
    upload_status: str = Field(..., description="Upload status")
    created_at: datetime = Field(..., description="Upload timestamp")
    
    model_config = {"from_attributes": True}


class DocumentUploadHistoryResponse(BaseModel):
    """Response schema for document upload history"""
    items: List[DocumentUploadHistoryItem] = Field(..., description="Upload history items")
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Offset")
    
    model_config = {"from_attributes": True}


# Document upload detail schema
class DocumentUploadDetail(BaseModel):
    """Schema for document upload detail"""
    id: UUID = Field(..., description="Upload ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (md/docx)")
    file_size: int = Field(..., description="File size in bytes")
    upload_status: str = Field(..., description="Upload status")
    parse_result: Optional[ParseResult] = Field(None, description="Parse result (if successful)")
    error_message: Optional[str] = Field(None, description="Error message (if failed)")
    created_at: datetime = Field(..., description="Upload timestamp")
    
    model_config = {"from_attributes": True}


# Internal schemas for document processing
class DocumentParseOptions(BaseModel):
    """Options for document parsing"""
    extract_images: bool = Field(default=True, description="Whether to extract and upload images")
    generate_metadata: bool = Field(default=True, description="Whether to generate metadata (summary, tags)")
    auto_translate: bool = Field(default=False, description="Whether to auto-translate")
    target_lang: str = Field(default="en", description="Target language for translation")
    category: Optional[str] = Field(None, description="Article category")

