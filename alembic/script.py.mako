"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer))

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_column("user_id")
