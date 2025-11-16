"""
Article API routes
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ArticleListItem,
    RelatedArticlesResponse
)
from app.models.user import User
from app.services.article import article_service
from app.core.deps import require_admin
import math


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=ArticleListResponse, summary="Get articles list")
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (admin only)"),
    search: Optional[str] = Query(None, description="Search in title and summary"),
    db: AsyncSession = Depends(get_db)
) -> ArticleListResponse:
    """
    Get paginated list of articles
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **category**: Filter by category (headline, regulatory, analysis, business, enterprise, outlook)
    - **status**: Filter by status (draft, published, archived) - returns published only for non-admin
    - **search**: Search in title and summary (Chinese and English)
    """
    # For public access, only show published articles
    if status is None:
        status = 'published'
    
    articles, total = await article_service.get_articles(
        db=db,
        page=page,
        page_size=page_size,
        category=category,
        status=status,
        search=search
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return ArticleListResponse(
        items=[ArticleListItem.model_validate(article) for article in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{article_id}", response_model=ArticleResponse, summary="Get article by ID")
async def get_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ArticleResponse:
    """
    Get a single article by ID
    
    - **article_id**: Article UUID
    """
    article = await article_service.get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Only show published articles to public
    if article.status != 'published':
        raise HTTPException(status_code=404, detail="Article not found")
    
    return ArticleResponse.model_validate(article)


@router.get("/{article_id}/related", response_model=RelatedArticlesResponse, summary="Get related articles")
async def get_related_articles(
    article_id: UUID,
    limit: int = Query(6, ge=1, le=20, description="Number of related articles"),
    db: AsyncSession = Depends(get_db)
) -> RelatedArticlesResponse:
    """
    Get related articles from the same category
    
    - **article_id**: Current article UUID
    - **limit**: Number of articles to return (default: 6, max: 20)
    
    Returns articles from the same category, ordered by publication date (newest first).
    Used for "Load More" functionality at article bottom.
    """
    # Check if article exists
    article = await article_service.get_article_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    related_articles, total = await article_service.get_related_articles(
        db=db,
        article_id=article_id,
        limit=limit
    )
    
    return RelatedArticlesResponse(
        articles=[ArticleListItem.model_validate(a) for a in related_articles],
        total=total,
        has_more=total > limit
    )


@router.post("", response_model=ArticleResponse, status_code=201, summary="Create article (Admin)")
async def create_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> ArticleResponse:
    """
    Create a new article (Admin only)

    Requires admin authentication.
    """
    article = await article_service.create_article(db, article_data)
    return ArticleResponse.model_validate(article)


@router.put("/{article_id}", response_model=ArticleResponse, summary="Update article (Admin)")
async def update_article(
    article_id: UUID,
    article_data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> ArticleResponse:
    """
    Update an article (Admin only)

    Requires admin authentication.
    All fields are optional - only provided fields will be updated.
    """
    article = await article_service.update_article(db, article_id, article_data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return ArticleResponse.model_validate(article)


@router.delete("/{article_id}", status_code=204, summary="Delete article (Admin)")
async def delete_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete an article (Admin only)

    Requires admin authentication.
    """
    success = await article_service.delete_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")

    return None

