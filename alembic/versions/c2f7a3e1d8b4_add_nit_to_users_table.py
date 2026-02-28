"""add_nit_to_users_table

Revision ID: c2f7a3e1d8b4
Revises: b7f3e2c1a4d9
Create Date: 2026-02-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2f7a3e1d8b4'
down_revision: Union[str, Sequence[str], None] = 'b7f3e2c1a4d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    columns = {col["name"] for col in inspector.get_columns("users")}
    if "nit" not in columns:
        with op.batch_alter_table("users", schema=None) as batch_op:
            batch_op.add_column(sa.Column("nit", sa.String(length=11), nullable=True))

    indexes = {idx["name"] for idx in inspector.get_indexes("users")}
    if "ix_users_nit" not in indexes:
        op.create_index("ix_users_nit", "users", ["nit"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = {idx["name"] for idx in inspector.get_indexes("users")}

    if "ix_users_nit" in indexes:
        op.drop_index("ix_users_nit", table_name="users")

    columns = {col["name"] for col in inspector.get_columns("users")}
    if "nit" in columns:
        with op.batch_alter_table("users", schema=None) as batch_op:
            batch_op.drop_column("nit")
