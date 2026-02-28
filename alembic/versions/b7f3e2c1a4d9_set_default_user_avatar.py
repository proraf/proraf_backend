"""set_default_user_avatar

Revision ID: b7f3e2c1a4d9
Revises: 0d5696186205
Create Date: 2026-02-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f3e2c1a4d9'
down_revision: Union[str, Sequence[str], None] = '0d5696186205'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_AVATAR = "static/images/users/icone.png"


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        f"UPDATE users SET avatar_url = '{DEFAULT_AVATAR}' WHERE avatar_url IS NULL OR avatar_url = ''"
    )

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'avatar_url',
            existing_type=sa.String(length=500),
            nullable=False,
            server_default=DEFAULT_AVATAR,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'avatar_url',
            existing_type=sa.String(length=500),
            nullable=True,
            server_default=None,
        )
