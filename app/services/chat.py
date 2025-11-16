"""
Chat service for AI-powered conversations with RAG
"""
import time
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.chat import ChatMessage
from app.services.deepseek import DeepSeekService
from app.services.faq import FAQService
from app.services.article import ArticleService
from app.schemas.chat import SourceReference


class ChatService:
    """聊天服务"""
    
    @staticmethod
    async def send_message(
        db: AsyncSession,
        user_message: str,
        session_id: Optional[str] = None
    ) -> Tuple[str, str, List[SourceReference], float]:
        """
        发送消息并获取 AI 回复
        
        Args:
            db: 数据库会话
            user_message: 用户消息
            session_id: 会话 ID（可选）
            
        Returns:
            (AI 回复, 会话 ID, 来源列表, 响应时间)
        """
        start_time = time.time()
        
        # 生成或使用现有会话 ID
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 保存用户消息
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=user_message,
            created_at=datetime.utcnow()
        )
        db.add(user_msg)
        await db.commit()
        
        # RAG: 检索相关 FAQ 和文章
        faq_results = await FAQService.search_faqs(db, user_message, limit=3)
        article_results = await ArticleService.search_articles(db, user_message, limit=2)
        
        # 构建来源引用
        sources = []
        
        for faq in faq_results:
            sources.append(SourceReference(
                type="faq",
                id=faq["id"],
                title=faq["question"],
                snippet=faq["answer"][:100] + "..." if len(faq["answer"]) > 100 else faq["answer"]
            ))
        
        for article in article_results:
            sources.append(SourceReference(
                type="article",
                id=article["id"],
                title=article["title"],
                snippet=article.get("content_snippet", article.get("summary", ""))
            ))
        
        # 构建 RAG 提示
        messages = DeepSeekService.build_rag_prompt(
            user_question=user_message,
            faq_results=faq_results,
            article_results=article_results
        )
        
        # 调用 DeepSeek API
        try:
            ai_response = await DeepSeekService.chat_completion(messages)
        except Exception as e:
            print(f"❌ DeepSeek API 调用失败: {str(e)}")
            # 降级方案：使用模拟回复
            ai_response = DeepSeekService._mock_response(messages)
        
        # 保存 AI 回复
        ai_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=ai_response,
            created_at=datetime.utcnow()
        )
        db.add(ai_msg)
        await db.commit()
        
        # 更新 FAQ 使用次数
        for faq in faq_results:
            await FAQService.increment_usage(db, faq["id"])
        
        # 计算响应时间
        response_time = time.time() - start_time
        
        return ai_response, session_id, sources, response_time
    
    @staticmethod
    async def get_chat_history(
        db: AsyncSession,
        session_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        获取聊天历史
        
        Args:
            db: 数据库会话
            session_id: 会话 ID
            limit: 返回数量限制
            
        Returns:
            聊天消息列表
        """
        query = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(
            ChatMessage.created_at.asc()
        ).limit(limit)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return list(messages)
    
    @staticmethod
    async def get_quick_questions() -> List[dict]:
        """
        获取快捷问题列表
        
        Returns:
            快捷问题列表
        """
        return [
            {
                "id": "q1",
                "question": "如何预约咨询服务？",
                "category": "预约"
            },
            {
                "id": "q2",
                "question": "预约需要多长时间？",
                "category": "预约"
            },
            {
                "id": "q3",
                "question": "如何取消预约？",
                "category": "预约"
            },
            {
                "id": "q4",
                "question": "你们提供哪些服务？",
                "category": "服务"
            },
            {
                "id": "q5",
                "question": "营业时间是什么时候？",
                "category": "服务"
            },
            {
                "id": "q6",
                "question": "如何联系客服？",
                "category": "其他"
            }
        ]

