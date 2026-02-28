"""restore_missing_revision_link

Revision ID: 5a9bb9d46b99
Revises: 454a825713d0
Create Date: 2026-02-28 00:00:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '5a9bb9d46b99'
down_revision: Union[str, Sequence[str], None] = '454a825713d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op migration to restore missing revision in history chain."""
    pass


def downgrade() -> None:
    """No-op downgrade."""
    pass
