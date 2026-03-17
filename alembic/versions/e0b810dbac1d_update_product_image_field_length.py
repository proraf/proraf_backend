"""Update product image field length

Revision ID: e0b810dbac1d
Revises: abc249a965c3
Create Date: 2025-10-15 11:05:17.267356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0b810dbac1d'
down_revision: Union[str, Sequence[str], None] = 'abc249a965c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # PostgreSQL suporta ALTER COLUMN - aumenta o tamanho do campo image
    op.alter_column('products', 'image',
                    existing_type=sa.String(255),
                    type_=sa.String(500),
                    existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('products', 'image',
                    existing_type=sa.String(500),
                    type_=sa.String(255),
                    existing_nullable=True)
