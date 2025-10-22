"""add_unidade_medida_to_batch

Revision ID: 8d22053b54ff
Revises: a77dc48ea19d
Create Date: 2025-10-21 16:21:09.580112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d22053b54ff'
down_revision: Union[str, Sequence[str], None] = 'a77dc48ea19d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
