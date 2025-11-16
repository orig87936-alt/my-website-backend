"""Update article summary column lengths

Revision ID: update_summary_length
Revises: add_translation_tables
Create Date: 2025-11-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'update_summary_length'
down_revision: Union[str, Sequence[str], None] = 'add_translation_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - increase summary column lengths."""
    # Increase summary_zh from 80 to 150 characters
    op.alter_column('articles', 'summary_zh',
                    existing_type=sa.String(length=80),
                    type_=sa.String(length=150),
                    existing_nullable=False)
    
    # Increase summary_en from 80 to 300 characters
    op.alter_column('articles', 'summary_en',
                    existing_type=sa.String(length=80),
                    type_=sa.String(length=300),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema - revert summary column lengths."""
    # Revert summary_en from 300 to 80 characters
    op.alter_column('articles', 'summary_en',
                    existing_type=sa.String(length=300),
                    type_=sa.String(length=80),
                    existing_nullable=False)
    
    # Revert summary_zh from 150 to 80 characters
    op.alter_column('articles', 'summary_zh',
                    existing_type=sa.String(length=150),
                    type_=sa.String(length=80),
                    existing_nullable=False)

