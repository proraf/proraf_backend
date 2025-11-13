"""add_unique_constraints_cpf_cnpj_telefone

Revision ID: 454a825713d0
Revises: 35b5bda22c39
Create Date: 2025-11-13 15:23:26.074409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '454a825713d0'
down_revision: Union[str, Sequence[str], None] = '35b5bda22c39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Clean up duplicates before adding unique constraints
    # For duplicate CPF, keep the oldest user and set CPF to NULL for duplicates
    connection = op.get_bind()
    
    # Find and handle duplicate CPFs
    result = connection.execute(sa.text("""
        SELECT cpf, COUNT(*) as cnt 
        FROM users 
        WHERE cpf IS NOT NULL 
        GROUP BY cpf 
        HAVING COUNT(*) > 1
    """))
    
    for row in result:
        cpf = row[0]
        # Get all users with this CPF ordered by created_at (keep oldest)
        users = connection.execute(sa.text("""
            SELECT id FROM users 
            WHERE cpf = :cpf 
            ORDER BY created_at ASC
        """), {"cpf": cpf}).fetchall()
        
        # Keep first user, nullify CPF for others
        if len(users) > 1:
            for user_row in users[1:]:
                connection.execute(sa.text("""
                    UPDATE users SET cpf = NULL WHERE id = :user_id
                """), {"user_id": user_row[0]})
    
    # Find and handle duplicate CNPJs
    result = connection.execute(sa.text("""
        SELECT cnpj, COUNT(*) as cnt 
        FROM users 
        WHERE cnpj IS NOT NULL 
        GROUP BY cnpj 
        HAVING COUNT(*) > 1
    """))
    
    for row in result:
        cnpj = row[0]
        users = connection.execute(sa.text("""
            SELECT id FROM users 
            WHERE cnpj = :cnpj 
            ORDER BY created_at ASC
        """), {"cnpj": cnpj}).fetchall()
        
        if len(users) > 1:
            for user_row in users[1:]:
                connection.execute(sa.text("""
                    UPDATE users SET cnpj = NULL WHERE id = :user_id
                """), {"user_id": user_row[0]})
    
    # Find and handle duplicate telefones
    result = connection.execute(sa.text("""
        SELECT telefone, COUNT(*) as cnt 
        FROM users 
        WHERE telefone IS NOT NULL 
        GROUP BY telefone 
        HAVING COUNT(*) > 1
    """))
    
    for row in result:
        telefone = row[0]
        users = connection.execute(sa.text("""
            SELECT id FROM users 
            WHERE telefone = :telefone 
            ORDER BY created_at ASC
        """), {"telefone": telefone}).fetchall()
        
        if len(users) > 1:
            for user_row in users[1:]:
                connection.execute(sa.text("""
                    UPDATE users SET telefone = NULL WHERE id = :user_id
                """), {"user_id": user_row[0]})
    
    # Now add unique constraints for CPF, CNPJ, and telefone in users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_cnpj'), ['cnpj'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_cpf'), ['cpf'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_telefone'), ['telefone'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove unique constraints for CPF, CNPJ, and telefone in users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_telefone'))
        batch_op.drop_index(batch_op.f('ix_users_cpf'))
        batch_op.drop_index(batch_op.f('ix_users_cnpj'))
