"""
Document upload model for tracking document processing
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, CheckConstraint, Index
from app.models.base import Base
from app.models.types import UUID, JSONB


class DocumentUpload(Base):
    """Document upload model for tracking uploaded documents"""
    
    __tablename__ = "document_uploads"
    
    # Primary key
    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # File information
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(50), nullable=False)  # 'md' or 'docx'
    
    # Upload status
    upload_status = Column(String(20), nullable=False, index=True)  # 'success', 'failed', 'processing'
    
    # Parse result (JSONB containing parsed content)
    parse_result = Column(JSONB, nullable=True)
    
    # Error message (if upload failed)
    error_message = Column(Text, nullable=True)
    
    # User who uploaded (optional)
    created_by = Column(String(100), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("upload_status IN ('success', 'failed', 'processing')", name='valid_upload_status'),
        CheckConstraint("file_type IN ('md', 'docx')", name='valid_file_type'),
        Index('idx_document_uploads_status', 'upload_status'),
        Index('idx_document_uploads_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<DocumentUpload {self.filename} status={self.upload_status}>"

