"""
Chat message model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, CheckConstraint, Index, text
from app.models.base import Base
from app.models.types import UUID, JSONB


class ChatMessage(Base):
    """Chat message model for conversation history"""
    
    __tablename__ = "chat_messages"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Session grouping
    session_id = Column(UUID, nullable=False, index=True)
    
    # Message details
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)

    # Message metadata (sources, tokens, response time, etc.)
    # Note: renamed from 'metadata' to 'message_metadata' to avoid SQLAlchemy reserved word
    message_metadata = Column(JSONB, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="valid_role"
        ),
        # Composite index for session history retrieval
        Index("idx_chat_messages_session_created", "session_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role='{self.role}', content='{self.content[:50]}...')>"

