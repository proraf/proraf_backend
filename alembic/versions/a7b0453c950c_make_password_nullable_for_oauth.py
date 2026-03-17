"""make_password_nullable_for_oauth

Revision ID: a7b0453c950c
Revises: 36929e0b4754
Create Date: 2025-10-22 17:06:05.232338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b0453c950c'
down_revision: Union[str, Sequence[str], None] = '36929e0b4754'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # PostgreSQL suporta ALTER COLUMN diretamente
    op.alter_column('users', 'senha',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'senha',
                    existing_type=sa.String(255),
                    nullable=False)
