"""update_enum_values_to_uppercase

Revision ID: c5371ac506dc
Revises: e372ab0e6103
Create Date: 2025-11-10 21:20:06.284887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5371ac506dc'
down_revision: Union[str, Sequence[str], None] = 'e372ab0e6103'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade enum values from lowercase to uppercase"""

    # Step 1: Add new enum values (uppercase) to existing enums
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'VISITOR'")
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'USER'")
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ADMIN'")

    op.execute("ALTER TYPE authprovider ADD VALUE IF NOT EXISTS 'EMAIL'")
    op.execute("ALTER TYPE authprovider ADD VALUE IF NOT EXISTS 'GOOGLE'")
    op.execute("ALTER TYPE authprovider ADD VALUE IF NOT EXISTS 'USERNAME'")

    # Step 2: Update existing data to use uppercase values
    op.execute("""
        UPDATE users
        SET role = CASE
            WHEN role::text = 'visitor' THEN 'VISITOR'::userrole
            WHEN role::text = 'user' THEN 'USER'::userrole
            WHEN role::text = 'admin' THEN 'ADMIN'::userrole
            ELSE role
        END
    """)

    op.execute("""
        UPDATE users
        SET auth_provider = CASE
            WHEN auth_provider::text = 'email' THEN 'EMAIL'::authprovider
            WHEN auth_provider::text = 'google' THEN 'GOOGLE'::authprovider
            WHEN auth_provider::text = 'username' THEN 'USERNAME'::authprovider
            ELSE auth_provider
        END
    """)


def downgrade() -> None:
    """Downgrade enum values from uppercase to lowercase"""

    # Update data back to lowercase
    op.execute("""
        UPDATE users
        SET role = CASE
            WHEN role::text = 'VISITOR' THEN 'visitor'::userrole
            WHEN role::text = 'USER' THEN 'user'::userrole
            WHEN role::text = 'ADMIN' THEN 'admin'::userrole
            ELSE role
        END
    """)

    op.execute("""
        UPDATE users
        SET auth_provider = CASE
            WHEN auth_provider::text = 'EMAIL' THEN 'email'::authprovider
            WHEN auth_provider::text = 'GOOGLE' THEN 'google'::authprovider
            WHEN auth_provider::text = 'USERNAME' THEN 'username'::authprovider
            ELSE auth_provider
        END
    """)
