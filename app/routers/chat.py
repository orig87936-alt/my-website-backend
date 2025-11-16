"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatMessageResponse,
    QuickQuestionsResponse,
    QuickQuestion
)
from app.services.chat import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")  # Max 20 chat messages per minute
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    发送消息并获取 AI 回复
    
    - **message**: 用户消息（必填，1-2000 字符）
    - **session_id**: 会话 ID（可选，用于多轮对话）
    
    返回 AI 回复、会话 ID、参考来源和响应时间
    """
    try:
        ai_response, session_id, sources, response_time = await ChatService.send_message(
            db=db,
            user_message=chat_request.message,
            session_id=chat_request.session_id
        )
        
        return ChatResponse(
            session_id=session_id,
            message=ai_response,
            sources=sources,
            response_time=response_time
        )
    except Exception as e:
        print(f"❌ 聊天服务错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天服务错误: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    获取聊天历史
    
    - **session_id**: 会话 ID
    - **limit**: 返回消息数量限制（默认 50）
    
    返回该会话的所有消息
    """
    try:
        messages = await ChatService.get_chat_history(
            db=db,
            session_id=session_id,
            limit=limit
        )
        
        message_responses = [
            ChatMessageResponse.model_validate(msg)
            for msg in messages
        ]
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=message_responses,
            total=len(message_responses)
        )
    except Exception as e:
        print(f"❌ 获取聊天历史错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取聊天历史错误: {str(e)}"
        )


@router.get("/quick-questions", response_model=QuickQuestionsResponse)
async def get_quick_questions():
    """
    获取快捷问题列表
    
    返回常见问题的快捷选项，用户可一键选择
    """
    questions = await ChatService.get_quick_questions()
    
    return QuickQuestionsResponse(
        questions=[QuickQuestion(**q) for q in questions]
    )

