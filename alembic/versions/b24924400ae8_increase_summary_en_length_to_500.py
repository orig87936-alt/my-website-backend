"""increase_summary_en_length_to_500

Revision ID: b24924400ae8
Revises: c5371ac506dc
Create Date: 2025-11-15 10:25:56.589220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b24924400ae8'
down_revision: Union[str, Sequence[str], None] = 'c5371ac506dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Increase summary_en column length from 300 to 500
    op.alter_column('articles', 'summary_en',
                    existing_type=sa.String(length=300),
                    type_=sa.String(length=500),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert summary_en column length from 500 to 300
    op.alter_column('articles', 'summary_en',
                    existing_type=sa.String(length=500),
                    type_=sa.String(length=300),
                    existing_nullable=False)
