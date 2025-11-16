"""Add translation and document upload tables

Revision ID: add_translation_tables
Revises: 3876dc2f9847
Create Date: 2025-11-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_translation_tables'
down_revision: Union[str, Sequence[str], None] = '3876dc2f9847'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add translation and document upload tables."""
    
    # Create translation_cache table
    op.create_table(
        'translation_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('source_text_hash', sa.String(length=64), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('translated_text', sa.Text(), nullable=False),
        sa.Column('source_lang', sa.String(length=10), nullable=False),
        sa.Column('target_lang', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW() + INTERVAL '30 days'")),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_text_hash', 'source_lang', 'target_lang', name='unique_translation')
    )
    
    # Create indexes for translation_cache
    op.create_index('idx_translation_cache_hash', 'translation_cache', ['source_text_hash', 'source_lang', 'target_lang'])
    op.create_index('idx_translation_cache_expires', 'translation_cache', ['expires_at'])
    
    # Create translation_logs table
    op.create_table(
        'translation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('field_name', sa.String(length=50), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('translated_text', sa.Text(), nullable=False),
        sa.Column('source_lang', sa.String(length=10), nullable=False),
        sa.Column('target_lang', sa.String(length=10), nullable=False),
        sa.Column('manually_edited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for translation_logs
    op.create_index('idx_translation_logs_article', 'translation_logs', ['article_id'])
    op.create_index('idx_translation_logs_created', 'translation_logs', ['created_at'])
    
    # Create document_uploads table
    op.create_table(
        'document_uploads',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('upload_status', sa.String(length=20), nullable=False),
        sa.Column('parse_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("upload_status IN ('success', 'failed', 'processing')", name='valid_upload_status'),
        sa.CheckConstraint("file_type IN ('md', 'docx')", name='valid_file_type'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for document_uploads
    op.create_index('idx_document_uploads_status', 'document_uploads', ['upload_status'])
    op.create_index('idx_document_uploads_created', 'document_uploads', ['created_at'])


def downgrade() -> None:
    """Downgrade schema - remove translation and document upload tables."""
    
    # Drop document_uploads table and indexes
    op.drop_index('idx_document_uploads_created', table_name='document_uploads')
    op.drop_index('idx_document_uploads_status', table_name='document_uploads')
    op.drop_table('document_uploads')
    
    # Drop translation_logs table and indexes
    op.drop_index('idx_translation_logs_created', table_name='translation_logs')
    op.drop_index('idx_translation_logs_article', table_name='translation_logs')
    op.drop_table('translation_logs')
    
    # Drop translation_cache table and indexes
    op.drop_index('idx_translation_cache_expires', table_name='translation_cache')
    op.drop_index('idx_translation_cache_hash', table_name='translation_cache')
    op.drop_table('translation_cache')

