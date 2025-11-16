"""
Translation API routes
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.schemas.translation import (
    TranslateRequest,
    TranslateResponse,
    BatchTranslateRequest,
    BatchTranslateResponse,
    DetectLanguageRequest,
    DetectLanguageResponse,
    TranslationHistoryResponse,
    TranslationLogResponse
)
from app.models.translation import TranslationLog
from app.services.translation import TranslationService
from app.core.deps import require_admin, get_current_user
from app.models.user import User


router = APIRouter(prefix="/translation", tags=["Translation"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/translate",
    response_model=TranslateResponse,
    summary="Translate single field",
    description="T075: Translate a single text field with AI-powered translation and caching"
)
@limiter.limit("30/minute")  # 30 requests per minute
async def translate_text(
    translate_request: TranslateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TranslateResponse:
    """
    Translate a single text field using DeepSeek AI with intelligent caching.

    **Features:**
    - AI-powered translation using DeepSeek API
    - Automatic language detection if source_lang not provided
    - SHA-256 based caching (30-day expiration)
    - Translation logging for quality monitoring

    **Parameters:**
    - **text**: Text to translate (1-5000 characters)
    - **source_lang**: Source language (zh/en) - auto-detect if not provided
    - **target_lang**: Target language (zh/en)

    **Rate Limit:** 30 requests per minute

    **Returns:**
    - **translated_text**: Translated text
    - **source_lang**: Detected/provided source language
    - **target_lang**: Target language
    - **cached**: Whether result was from cache
    """
    try:
        # Create translation service
        translation_service = TranslationService(db)

        # Log translation request
        text_length = len(translate_request.text)
        print(f"🔄 Translation request: {text_length} chars, {translate_request.source_lang} → {translate_request.target_lang}")

        # Translate
        result = await translation_service.translate_text(
            text=translate_request.text,
            source_lang=translate_request.source_lang,
            target_lang=translate_request.target_lang
        )

        # Log translation result
        translated_length = len(result.get('translated_text', ''))
        print(f"✅ Translation complete: {translated_length} chars, cached={result.get('cached', False)}")

        return TranslateResponse(**result)

    except Exception as e:
        print(f"❌ Translation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post(
    "/batch-translate",
    response_model=BatchTranslateResponse,
    summary="Batch translate multiple fields",
    description="T075: Batch translate multiple fields with concurrent processing (T070)"
)
@limiter.limit("10/minute")  # 10 requests per minute (more expensive operation)
async def batch_translate(
    batch_request: BatchTranslateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> BatchTranslateResponse:
    """
    Batch translate multiple fields with concurrent processing for better performance.

    **Features:**
    - Concurrent translation (max 4 fields simultaneously) - T070
    - Automatic language detection
    - SHA-256 based caching
    - Translation logging for each field
    - Performance metrics (translation time, cache hit rate) - T071

    **Parameters:**
    - **fields**: List of fields to translate (1-10 fields)
      - Each field has: field_name (string), text (string)
    - **source_lang**: Source language (zh/en) - auto-detect if not provided
    - **target_lang**: Target language (zh/en)
    - **article_id**: Article ID for logging (optional)

    **Rate Limit:** 10 requests per minute

    **Returns:**
    - **results**: List of translation results for each field
    - **source_lang**: Detected/provided source language
    - **target_lang**: Target language
    - **total_fields**: Total number of fields translated
    - **cached_count**: Number of results from cache
    - **translation_time**: Total translation time in seconds (T071)
    - **cache_hit_rate**: Percentage of cache hits (T071)
    """
    try:
        # Create translation service
        translation_service = TranslationService(db)

        # Prepare fields
        fields = [
            {'field_name': field.field_name, 'text': field.text}
            for field in batch_request.fields
        ]

        # Batch translate
        result = await translation_service.batch_translate(
            fields=fields,
            source_lang=batch_request.source_lang,
            target_lang=batch_request.target_lang,
            article_id=str(batch_request.article_id) if batch_request.article_id else None
        )

        return BatchTranslateResponse(**result)

    except Exception as e:
        print(f"❌ Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")


@router.post("/detect-language", response_model=DetectLanguageResponse, summary="Detect text language")
async def detect_language(
    request: DetectLanguageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> DetectLanguageResponse:
    """
    Detect the language of text
    
    - **text**: Text to detect (1-1000 characters)
    
    Returns detected language code and confidence score.
    """
    try:
        # Create translation service
        translation_service = TranslationService(db)
        
        # Detect language
        detected_lang, confidence = await translation_service.detect_language(request.text)
        
        return DetectLanguageResponse(
            detected_lang=detected_lang,
            confidence=confidence
        )
        
    except Exception as e:
        print(f"❌ Language detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")


@router.get("/history", response_model=TranslationHistoryResponse, summary="Get translation history")
async def get_translation_history(
    article_id: Optional[UUID] = Query(None, description="Filter by article ID"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Offset"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_admin)
) -> TranslationHistoryResponse:
    """
    Get translation history logs
    
    - **article_id**: Filter by article ID (optional)
    - **limit**: Items per page (default: 20, max: 100)
    - **offset**: Offset for pagination (default: 0)
    
    Returns paginated translation history with manual edit tracking.
    """
    try:
        # Build query
        stmt = select(TranslationLog).order_by(desc(TranslationLog.created_at))
        
        # Filter by article_id if provided
        if article_id:
            stmt = stmt.where(TranslationLog.article_id == str(article_id))
        
        # Count total
        count_stmt = select(TranslationLog)
        if article_id:
            count_stmt = count_stmt.where(TranslationLog.article_id == str(article_id))
        
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())
        
        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        # Convert to response
        items = [
            TranslationLogResponse(
                id=log.id,
                article_id=log.article_id,
                field_name=log.field_name,
                source_text=log.source_text,
                translated_text=log.translated_text,
                source_lang=log.source_lang,
                target_lang=log.target_lang,
                manually_edited=log.manually_edited,
                edited_at=log.edited_at,
                created_at=log.created_at
            )
            for log in logs
        ]
        
        return TranslationHistoryResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        print(f"❌ Translation history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get translation history: {str(e)}")

