"""
Article embedding model for vector search
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

# 尝试导入 pgvector，如果不可用则跳过
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    # 如果 pgvector 不可用，使用 Text 类型作为占位符
    Vector = lambda dim: Text


class ArticleEmbedding(Base):
    """Article embedding model for semantic search using pgvector"""
    
    __tablename__ = "article_embeddings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    
    # Foreign key to articles
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    # Vector embedding (1536 dimensions for OpenAI text-embedding-3-small)
    # 如果 pgvector 不可用，使用 Text 类型存储 JSON 格式的向量
    embedding = Column(Vector(1536) if PGVECTOR_AVAILABLE else Text, nullable=False)
    
    # Content used for embedding
    content_text = Column(Text, nullable=True)
    
    # Language
    language = Column(String(10), nullable=False)  # 'zh' or 'en'
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=text("NOW()"))
    
    # Constraints
    __table_args__ = (
        # One embedding per article per language
        UniqueConstraint("article_id", "language", name="unique_article_language_embedding"),
        # HNSW index for fast vector similarity search using cosine distance
        # 注意: 需要 pgvector 扩展，如果未安装则跳过索引
        # Index(
        #     "idx_article_embeddings_vector",
        #     "embedding",
        #     postgresql_using="hnsw",
        #     postgresql_with={"m": 16, "ef_construction": 64},
        #     postgresql_ops={"embedding": "vector_cosine_ops"}
        # ),
    )
    
    def __repr__(self):
        return f"<ArticleEmbedding(id={self.id}, article_id={self.article_id}, language='{self.language}')>"

