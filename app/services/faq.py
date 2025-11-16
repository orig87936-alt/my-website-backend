"""
FAQ service for CRUD operations and search
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
import uuid

from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate


class FAQService:
    """FAQ 服务"""
    
    @staticmethod
    async def create_faq(db: AsyncSession, faq_data: FAQCreate) -> FAQ:
        """
        创建 FAQ
        
        Args:
            db: 数据库会话
            faq_data: FAQ 创建数据
            
        Returns:
            创建的 FAQ 对象
        """
        # 将关键词列表转换为逗号分隔的字符串（SQLite 兼容）
        keywords_str = ",".join(faq_data.keywords) if faq_data.keywords else ""
        
        faq = FAQ(
            id=str(uuid.uuid4()),
            question=faq_data.question,
            answer=faq_data.answer,
            keywords=keywords_str,
            category=faq_data.category,
            priority=faq_data.priority,
            is_active=faq_data.is_active,
            usage_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(faq)
        await db.commit()
        await db.refresh(faq)
        
        return faq
    
    @staticmethod
    async def get_faq_by_id(db: AsyncSession, faq_id: str) -> Optional[FAQ]:
        """
        根据 ID 获取 FAQ
        
        Args:
            db: 数据库会话
            faq_id: FAQ ID
            
        Returns:
            FAQ 对象或 None
        """
        result = await db.execute(
            select(FAQ).where(FAQ.id == faq_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_faqs(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[FAQ], int]:
        """
        获取 FAQ 列表（分页）
        
        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            category: 分类过滤
            is_active: 状态过滤
            search: 搜索关键词
            
        Returns:
            (FAQ 列表, 总数)
        """
        # 构建查询
        query = select(FAQ)
        
        # 应用过滤
        filters = []
        if category:
            filters.append(FAQ.category == category)
        if is_active is not None:
            filters.append(FAQ.is_active == is_active)
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    FAQ.question.ilike(search_pattern),
                    FAQ.answer.ilike(search_pattern),
                    FAQ.keywords.ilike(search_pattern)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # 排序：优先级降序，更新时间降序
        query = query.order_by(FAQ.priority.desc(), FAQ.updated_at.desc())
        
        # 获取总数
        count_query = select(func.count()).select_from(FAQ)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        faqs = result.scalars().all()
        
        return list(faqs), total
    
    @staticmethod
    async def update_faq(
        db: AsyncSession,
        faq_id: str,
        faq_data: FAQUpdate
    ) -> Optional[FAQ]:
        """
        更新 FAQ
        
        Args:
            db: 数据库会话
            faq_id: FAQ ID
            faq_data: 更新数据
            
        Returns:
            更新后的 FAQ 对象或 None
        """
        faq = await FAQService.get_faq_by_id(db, faq_id)
        if not faq:
            return None
        
        # 更新字段
        update_data = faq_data.model_dump(exclude_unset=True)
        
        # 处理关键词列表
        if "keywords" in update_data and update_data["keywords"] is not None:
            update_data["keywords"] = ",".join(update_data["keywords"])
        
        for field, value in update_data.items():
            setattr(faq, field, value)
        
        faq.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(faq)
        
        return faq
    
    @staticmethod
    async def delete_faq(db: AsyncSession, faq_id: str) -> bool:
        """
        删除 FAQ
        
        Args:
            db: 数据库会话
            faq_id: FAQ ID
            
        Returns:
            是否删除成功
        """
        faq = await FAQService.get_faq_by_id(db, faq_id)
        if not faq:
            return False
        
        await db.delete(faq)
        await db.commit()
        
        return True
    
    @staticmethod
    async def search_faqs(
        db: AsyncSession,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        搜索 FAQ（用于 RAG）
        
        Args:
            db: 数据库会话
            query: 搜索查询
            limit: 返回数量限制
            
        Returns:
            FAQ 搜索结果列表
        """
        # 提取查询中的关键词
        keywords = query.lower().split()
        
        # 构建搜索条件
        search_conditions = []
        for keyword in keywords:
            pattern = f"%{keyword}%"
            search_conditions.append(
                or_(
                    FAQ.question.ilike(pattern),
                    FAQ.answer.ilike(pattern),
                    FAQ.keywords.ilike(pattern)
                )
            )
        
        # 查询活跃的 FAQ
        sql_query = select(FAQ).where(
            and_(
                FAQ.is_active == True,
                or_(*search_conditions) if search_conditions else True
            )
        ).order_by(
            FAQ.priority.desc(),
            FAQ.usage_count.desc()
        ).limit(limit)
        
        result = await db.execute(sql_query)
        faqs = result.scalars().all()
        
        # 转换为字典格式
        results = []
        for faq in faqs:
            # 计算相关性分数（简单实现）
            relevance_score = FAQService._calculate_relevance(query, faq)
            
            results.append({
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "category": faq.category,
                "priority": faq.priority,
                "relevance_score": relevance_score
            })
        
        # 按相关性分数排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results
    
    @staticmethod
    def _calculate_relevance(query: str, faq: FAQ) -> float:
        """
        计算相关性分数
        
        Args:
            query: 搜索查询
            faq: FAQ 对象
            
        Returns:
            相关性分数（0-1）
        """
        query_lower = query.lower()
        question_lower = faq.question.lower()
        answer_lower = faq.answer.lower()
        keywords_lower = faq.keywords.lower()
        
        score = 0.0
        
        # 完全匹配问题（最高分）
        if query_lower == question_lower:
            score += 1.0
        # 问题包含查询
        elif query_lower in question_lower:
            score += 0.8
        # 查询包含在问题中
        elif question_lower in query_lower:
            score += 0.6
        
        # 关键词匹配
        query_words = set(query_lower.split())
        keyword_list = set(keywords_lower.split(","))
        
        if query_words & keyword_list:  # 有交集
            overlap = len(query_words & keyword_list)
            score += 0.3 * (overlap / len(query_words))
        
        # 答案包含查询
        if query_lower in answer_lower:
            score += 0.2
        
        # 优先级加成
        score += (faq.priority / 100) * 0.1
        
        # 使用次数加成
        if faq.usage_count > 0:
            score += min(faq.usage_count / 100, 0.1)
        
        return min(score, 1.0)  # 限制在 0-1 之间
    
    @staticmethod
    async def increment_usage(db: AsyncSession, faq_id: str):
        """
        增加 FAQ 使用次数
        
        Args:
            db: 数据库会话
            faq_id: FAQ ID
        """
        faq = await FAQService.get_faq_by_id(db, faq_id)
        if faq:
            faq.usage_count += 1
            faq.last_used_at = datetime.utcnow()
            await db.commit()

