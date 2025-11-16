"""Initial schema with 5 tables

Revision ID: 3876dc2f9847
Revises:
Create Date: 2025-11-08 01:57:42.875455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '3876dc2f9847'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable required PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    # Skip vector extension - not needed for now
    # op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('title_zh', sa.String(length=200), nullable=False),
        sa.Column('title_en', sa.String(length=200), nullable=False),
        sa.Column('summary_zh', sa.String(length=80), nullable=False),
        sa.Column('summary_en', sa.String(length=80), nullable=False),
        sa.Column('content_zh', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('content_en', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('author', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='published'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("category IN ('headline', 'regulatory', 'analysis', 'business', 'enterprise', 'outlook')", name='valid_category'),
        sa.CheckConstraint("status IN ('draft', 'published', 'archived')", name='valid_status'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_articles_category_published', 'articles', ['category', 'published_at'],
                    postgresql_where=sa.text("status = 'published'"))
    op.create_index(op.f('ix_articles_category'), 'articles', ['category'])
    op.create_index(op.f('ix_articles_created_at'), 'articles', ['created_at'])
    op.create_index(op.f('ix_articles_published_at'), 'articles', ['published_at'])

    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('appointment_date', sa.Date(), nullable=False),
        sa.Column('time_slot', sa.String(length=10), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('confirmation_number', sa.String(length=20), nullable=True),
        sa.Column('notification_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('notification_retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_notification_attempt', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("time_slot ~ '^\\d{2}:\\d{2}$'", name='valid_time_slot_format'),
        sa.CheckConstraint("status IN ('pending', 'confirmed', 'completed', 'cancelled')", name='valid_status'),
        sa.CheckConstraint("notification_status IN ('pending', 'sent', 'failed')", name='valid_notification_status'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('confirmation_number')
    )
    op.create_index('idx_unique_appointment_slot', 'appointments', ['appointment_date', 'time_slot'],
                    unique=True, postgresql_where=sa.text("status != 'cancelled'"))
    op.create_index('idx_appointments_notification_retry', 'appointments', ['notification_status', 'notification_retry_count'],
                    postgresql_where=sa.text("notification_status = 'failed' AND notification_retry_count < 3"))
    op.create_index(op.f('ix_appointments_appointment_date'), 'appointments', ['appointment_date'])
    op.create_index(op.f('ix_appointments_created_at'), 'appointments', ['created_at'])

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='valid_role'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_chat_messages_session_created', 'chat_messages', ['session_id', 'created_at'])
    op.create_index(op.f('ix_chat_messages_created_at'), 'chat_messages', ['created_at'])
    op.create_index(op.f('ix_chat_messages_session_id'), 'chat_messages', ['session_id'])

    # Create faqs table
    op.create_table(
        'faqs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('question_zh', sa.String(length=500), nullable=False),
        sa.Column('question_en', sa.String(length=500), nullable=False),
        sa.Column('answer_zh', sa.Text(), nullable=False),
        sa.Column('answer_en', sa.Text(), nullable=False),
        sa.Column('keywords', postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_faqs_keywords', 'faqs', ['keywords'], postgresql_using='gin')
    op.create_index('idx_faqs_priority_active', 'faqs', ['priority'],
                    postgresql_where=sa.text('is_active = true'),
                    postgresql_ops={'priority': 'DESC'})
    op.create_index(op.f('ix_faqs_created_at'), 'faqs', ['created_at'])

    # Skip article_embeddings table - requires pgvector extension
    # op.create_table(
    #     'article_embeddings',
    #     sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
    #     sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
    #     sa.Column('language', sa.String(length=10), nullable=False),
    #     sa.Column('embedding', Vector(1536), nullable=False),
    #     sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    #     sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    #     sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    #     sa.PrimaryKeyConstraint('id'),
    #     sa.UniqueConstraint('article_id', 'language', name='unique_article_language_embedding')
    # )
    # op.create_index('idx_article_embeddings_vector', 'article_embeddings', ['embedding'],
    #                 postgresql_using='hnsw',
    #                 postgresql_with={'m': 16, 'ef_construction': 64},
    #                 postgresql_ops={'embedding': 'vector_cosine_ops'})
    # op.create_index(op.f('ix_article_embeddings_article_id'), 'article_embeddings', ['article_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # op.drop_table('article_embeddings')  # Skipped - not created
    op.drop_table('faqs')
    op.drop_table('chat_messages')
    op.drop_table('appointments')
    op.drop_table('articles')
    # op.execute('DROP EXTENSION IF EXISTS vector')  # Skipped - not created
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
