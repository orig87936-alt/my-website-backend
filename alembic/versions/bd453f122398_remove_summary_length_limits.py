"""remove_summary_length_limits

Revision ID: bd453f122398
Revises: b24924400ae8
Create Date: 2025-11-15 10:30:48.281546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd453f122398'
down_revision: Union[str, Sequence[str], None] = 'b24924400ae8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove length limits from summary columns by changing to TEXT type
    op.alter_column('articles', 'summary_zh',
                    existing_type=sa.String(length=150),
                    type_=sa.Text(),
                    existing_nullable=False)

    op.alter_column('articles', 'summary_en',
                    existing_type=sa.String(length=500),
                    type_=sa.Text(),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert to limited length VARCHAR columns
    op.alter_column('articles', 'summary_zh',
                    existing_type=sa.Text(),
                    type_=sa.String(length=150),
                    existing_nullable=False)

    op.alter_column('articles', 'summary_en',
                    existing_type=sa.Text(),
                    type_=sa.String(length=500),
                    existing_nullable=False)
