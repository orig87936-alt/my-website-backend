"""
Article service for business logic
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from uuid import UUID
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


class ArticleService:
    """Service for article business logic"""
    
    @staticmethod
    async def create_article(db: AsyncSession, article_data: ArticleCreate) -> Article:
        """Create a new article"""
        # Convert Pydantic models to dict for JSONB storage
        content_zh_dict = [block.model_dump() for block in article_data.content_zh]
        content_en_dict = [block.model_dump() for block in article_data.content_en]
        
        article = Article(
            category=article_data.category,
            status=article_data.status,
            title_zh=article_data.title_zh,
            title_en=article_data.title_en,
            summary_zh=article_data.summary_zh,
            summary_en=article_data.summary_en,
            lead_zh=article_data.lead_zh,
            lead_en=article_data.lead_en,
            content_zh=content_zh_dict,
            content_en=content_en_dict,
            image_url=article_data.image_url,
            image_caption_zh=article_data.image_caption_zh,
            image_caption_en=article_data.image_caption_en,
            author=article_data.author,
            published_at=article_data.published_at or datetime.utcnow()
        )
        
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article
    
    @staticmethod
    async def get_article_by_id(db: AsyncSession, article_id: UUID) -> Optional[Article]:
        """Get article by ID"""
        # Convert UUID to string for SQLite compatibility
        article_id_str = str(article_id) if isinstance(article_id, UUID) else article_id
        result = await db.execute(
            select(Article).where(Article.id == article_id_str)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_articles(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Article], int]:
        """
        Get paginated list of articles with optional filtering
        
        Args:
            db: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            category: Filter by category
            status: Filter by status
            search: Search in title and summary (Chinese and English)
        
        Returns:
            Tuple of (articles list, total count)
        """
        # Build query
        query = select(Article)
        count_query = select(func.count()).select_from(Article)
        
        # Apply filters
        filters = []
        if category:
            filters.append(Article.category == category)
        if status:
            filters.append(Article.status == status)
        if search:
            search_filter = or_(
                Article.title_zh.ilike(f"%{search}%"),
                Article.title_en.ilike(f"%{search}%"),
                Article.summary_zh.ilike(f"%{search}%"),
                Article.summary_en.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Article.published_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()
        
        return list(articles), total
    
    @staticmethod
    async def get_related_articles(
        db: AsyncSession,
        article_id: UUID,
        limit: int = 6
    ) -> Tuple[List[Article], int]:
        """
        Get related articles from the same category
        
        Args:
            db: Database session
            article_id: Current article ID
            limit: Number of articles to return
        
        Returns:
            Tuple of (related articles list, total count in category)
        """
        # First, get the current article to find its category
        current_article = await ArticleService.get_article_by_id(db, article_id)
        if not current_article:
            return [], 0
        
        # Convert UUID to string for SQLite compatibility
        article_id_str = str(article_id) if isinstance(article_id, UUID) else article_id

        # Query for articles in the same category, excluding current article
        query = select(Article).where(
            and_(
                Article.category == current_article.category,
                Article.id != article_id_str,
                Article.status == 'published'
            )
        ).order_by(Article.published_at.desc())

        # Get total count
        count_query = select(func.count()).select_from(Article).where(
            and_(
                Article.category == current_article.category,
                Article.id != article_id_str,
                Article.status == 'published'
            )
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()
        
        return list(articles), total
    
    @staticmethod
    async def update_article(
        db: AsyncSession,
        article_id: UUID,
        article_data: ArticleUpdate
    ) -> Optional[Article]:
        """Update an article"""
        article = await ArticleService.get_article_by_id(db, article_id)
        if not article:
            return None
        
        # Update fields
        update_data = article_data.model_dump(exclude_unset=True)
        
        # Convert content blocks to dict if present
        if 'content_zh' in update_data and update_data['content_zh'] is not None:
            update_data['content_zh'] = [block.model_dump() for block in article_data.content_zh]
        if 'content_en' in update_data and update_data['content_en'] is not None:
            update_data['content_en'] = [block.model_dump() for block in article_data.content_en]
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        article.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(article)
        return article
    
    @staticmethod
    async def delete_article(db: AsyncSession, article_id: UUID) -> bool:
        """Delete an article"""
        article = await ArticleService.get_article_by_id(db, article_id)
        if not article:
            return False
        
        await db.delete(article)
        await db.commit()
        return True
    
    @staticmethod
    async def get_published_articles(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None
    ) -> Tuple[List[Article], int]:
        """Get published articles only (for public API)"""
        return await ArticleService.get_articles(
            db=db,
            page=page,
            page_size=page_size,
            category=category,
            status='published'
        )

    @staticmethod
    async def search_articles(
        db: AsyncSession,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        搜索文章（用于 RAG）

        Args:
            db: 数据库会话
            query: 搜索查询
            limit: 返回数量限制

        Returns:
            文章搜索结果列表
        """
        # 提取查询中的关键词
        keywords = query.lower().split()

        # 构建搜索条件（搜索中英文标题和摘要）
        search_conditions = []
        for keyword in keywords:
            pattern = f"%{keyword}%"
            search_conditions.append(
                or_(
                    Article.title_zh.ilike(pattern),
                    Article.title_en.ilike(pattern),
                    Article.summary_zh.ilike(pattern),
                    Article.summary_en.ilike(pattern)
                )
            )

        # 查询已发布的文章
        sql_query = select(Article).where(
            and_(
                Article.status == 'published',
                or_(*search_conditions) if search_conditions else True
            )
        ).order_by(
            Article.published_at.desc()
        ).limit(limit)

        result = await db.execute(sql_query)
        articles = result.scalars().all()

        # 转换为字典格式
        results = []
        for article in articles:
            # 提取文本内容（从 content_zh 和 content_en）
            text_content_zh = ArticleService._extract_text_from_blocks(article.content_zh)
            text_content_en = ArticleService._extract_text_from_blocks(article.content_en)
            text_content = f"{text_content_zh} {text_content_en}"

            # 计算相关性分数
            relevance_score = ArticleService._calculate_article_relevance(query, article, text_content)

            results.append({
                "id": article.id,
                "title": article.title_zh,  # 使用中文标题
                "summary": article.summary_zh,  # 使用中文摘要
                "category": article.category,
                "content_snippet": text_content[:200] + "..." if len(text_content) > 200 else text_content,
                "relevance_score": relevance_score
            })

        # 按相关性分数排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return results

    @staticmethod
    def _extract_text_from_blocks(content_blocks) -> str:
        """
        从内容块中提取文本

        Args:
            content_blocks: 内容块（JSON 或字符串）

        Returns:
            提取的文本内容
        """
        if not content_blocks:
            return ""

        # 如果是字符串，解析为 JSON
        if isinstance(content_blocks, str):
            try:
                blocks = json.loads(content_blocks)
            except:
                return content_blocks
        else:
            blocks = content_blocks

        # 提取所有文本内容
        text_parts = []
        if isinstance(blocks, list):
            for block in blocks:
                if isinstance(block, dict) and "content" in block:
                    text_parts.append(block["content"])

        return " ".join(text_parts)

    @staticmethod
    def _calculate_article_relevance(query: str, article: Article, text_content: str) -> float:
        """
        计算文章相关性分数

        Args:
            query: 搜索查询
            article: 文章对象
            text_content: 文章文本内容

        Returns:
            相关性分数（0-1）
        """
        query_lower = query.lower()
        # 合并中英文标题和摘要
        title_lower = f"{article.title_zh} {article.title_en}".lower()
        summary_lower = f"{article.summary_zh} {article.summary_en}".lower()
        content_lower = text_content.lower()

        score = 0.0

        # 标题匹配（最高权重）
        if query_lower in title_lower:
            score += 0.5

        # 摘要匹配
        if query_lower in summary_lower:
            score += 0.3

        # 内容匹配
        if query_lower in content_lower:
            score += 0.2

        # 关键词匹配
        query_words = set(query_lower.split())
        title_words = set(title_lower.split())

        if query_words & title_words:  # 有交集
            overlap = len(query_words & title_words)
            score += 0.2 * (overlap / len(query_words))

        return min(score, 1.0)  # 限制在 0-1 之间


# Singleton instance
article_service = ArticleService()

