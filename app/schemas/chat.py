"""
Chat schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话 ID（可选，用于多轮对话）")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "如何预约咨询服务？",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    }


class ChatMessageResponse(BaseModel):
    """单条聊天消息响应"""
    id: UUID
    session_id: UUID
    role: str  # 'user' or 'assistant'
    content: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "user",
                "content": "如何预约咨询服务？",
                "created_at": "2025-11-08T10:30:00Z"
            }
        }
    }


class SourceReference(BaseModel):
    """来源引用（FAQ 或文章）"""
    type: str = Field(..., description="来源类型: 'faq' 或 'article'")
    id: UUID = Field(..., description="来源 ID")
    title: str = Field(..., description="标题或问题")
    snippet: Optional[str] = Field(None, description="内容片段")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "faq",
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "如何预约咨询服务？",
                "snippet": "您可以通过预约页面选择时间..."
            }
        }
    }


class ChatResponse(BaseModel):
    """聊天响应模型"""
    session_id: UUID = Field(..., description="会话 ID")
    message: str = Field(..., description="AI 回复内容")
    sources: List[SourceReference] = Field(default_factory=list, description="参考来源")
    response_time: float = Field(..., description="响应时间（秒）")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "您可以通过我们的预约页面选择合适的时间进行咨询服务预约...",
                "sources": [
                    {
                        "type": "faq",
                        "id": "faq-001",
                        "title": "如何预约咨询服务？",
                        "snippet": "您可以通过预约页面选择时间..."
                    }
                ],
                "response_time": 1.23
            }
        }
    }


class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    session_id: UUID
    messages: List[ChatMessageResponse]
    total: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "messages": [],
                "total": 10
            }
        }
    }


class QuickQuestion(BaseModel):
    """快捷问题"""
    id: str  # 快捷问题使用简单的字符串 ID (q1, q2, etc.)
    question: str
    category: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "q1",
                "question": "如何预约咨询服务？",
                "category": "预约"
            }
        }
    }


class QuickQuestionsResponse(BaseModel):
    """快捷问题列表响应"""
    questions: List[QuickQuestion]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "questions": [
                    {"id": "q1", "question": "如何预约咨询服务？", "category": "预约"},
                    {"id": "q2", "question": "预约需要多长时间？", "category": "预约"},
                    {"id": "q3", "question": "如何取消预约？", "category": "预约"}
                ]
            }
        }
    }

