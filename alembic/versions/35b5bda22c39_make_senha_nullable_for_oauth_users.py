"""make_senha_nullable_for_oauth_users

Revision ID: 35b5bda22c39
Revises: a7b0453c950c
Create Date: 2025-10-24 12:51:01.048799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35b5bda22c39'
down_revision: Union[str, Sequence[str], None] = 'a7b0453c950c'
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
    # Volta senha para NOT NULL (vai falhar se existirem registros com senha NULL)
    op.alter_column('users', 'senha',
                    existing_type=sa.String(255),
                    nullable=False)
