"""
FAQ API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.database import get_db
from app.core.deps import require_admin
from app.models.user import User
from app.schemas.faq import (
    FAQCreate,
    FAQUpdate,
    FAQResponse,
    FAQListResponse,
    FAQListItem,
    FAQSearchResponse,
    FAQSearchResult
)
from app.services.faq import FAQService

router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.post("", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq_data: FAQCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    创建 FAQ（管理员）
    
    - **question**: 问题（必填）
    - **answer**: 答案（必填）
    - **keywords**: 关键词列表（可选）
    - **category**: 分类（可选）
    - **priority**: 优先级 0-100（默认 0）
    - **is_active**: 是否启用（默认 true）
    """
    try:
        faq = await FAQService.create_faq(db, faq_data)

        # 转换 keywords 字符串为列表
        keywords_list = faq.keywords.split(",") if faq.keywords else []

        return FAQResponse(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            keywords=keywords_list,
            category=faq.category,
            priority=faq.priority,
            is_active=faq.is_active,
            usage_count=faq.usage_count,
            last_used_at=faq.last_used_at,
            created_at=faq.created_at,
            updated_at=faq.updated_at
        )
    except Exception as e:
        print(f"❌ 创建 FAQ 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建 FAQ 失败: {str(e)}"
        )


@router.get("", response_model=FAQListResponse)
async def get_faqs(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    获取 FAQ 列表（管理员）
    
    - **page**: 页码（默认 1）
    - **page_size**: 每页数量（默认 20）
    - **category**: 分类过滤（可选）
    - **is_active**: 状态过滤（可选）
    - **search**: 搜索关键词（可选）
    """
    try:
        faqs, total = await FAQService.get_faqs(
            db=db,
            page=page,
            page_size=page_size,
            category=category,
            is_active=is_active,
            search=search
        )
        
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return FAQListResponse(
            items=[FAQListItem.model_validate(faq) for faq in faqs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        print(f"❌ 获取 FAQ 列表错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取 FAQ 列表失败: {str(e)}"
        )


@router.get("/search", response_model=FAQSearchResponse)
async def search_faqs(
    q: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    搜索 FAQ（公开）
    
    - **q**: 搜索查询
    - **limit**: 返回数量限制（默认 10）
    """
    try:
        results = await FAQService.search_faqs(db, q, limit)
        
        return FAQSearchResponse(
            results=[FAQSearchResult(**r) for r in results],
            total=len(results),
            query=q
        )
    except Exception as e:
        print(f"❌ 搜索 FAQ 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索 FAQ 失败: {str(e)}"
        )


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(
    faq_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    获取 FAQ 详情（管理员）
    
    - **faq_id**: FAQ ID
    """
    faq = await FAQService.get_faq_by_id(db, faq_id)

    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ 不存在"
        )

    # 转换 keywords 字符串为列表
    keywords_list = faq.keywords.split(",") if faq.keywords else []

    return FAQResponse(
        id=faq.id,
        question=faq.question,
        answer=faq.answer,
        keywords=keywords_list,
        category=faq.category,
        priority=faq.priority,
        is_active=faq.is_active,
        usage_count=faq.usage_count,
        last_used_at=faq.last_used_at,
        created_at=faq.created_at,
        updated_at=faq.updated_at
    )


@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: str,
    faq_data: FAQUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    更新 FAQ（管理员）
    
    - **faq_id**: FAQ ID
    - 所有字段可选，只更新提供的字段
    """
    try:
        faq = await FAQService.update_faq(db, faq_id, faq_data)
        
        if not faq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FAQ 不存在"
            )
        
        # 转换 keywords 字符串为列表
        keywords_list = faq.keywords.split(",") if faq.keywords else []

        return FAQResponse(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            keywords=keywords_list,
            category=faq.category,
            priority=faq.priority,
            is_active=faq.is_active,
            usage_count=faq.usage_count,
            last_used_at=faq.last_used_at,
            created_at=faq.created_at,
            updated_at=faq.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 更新 FAQ 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新 FAQ 失败: {str(e)}"
        )


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    删除 FAQ（管理员）
    
    - **faq_id**: FAQ ID
    """
    success = await FAQService.delete_faq(db, faq_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ 不存在"
        )
    
    return None

