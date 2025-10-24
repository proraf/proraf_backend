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
    # SQLite não suporta ALTER COLUMN diretamente, então vamos usar um workaround
    # Criar tabela temporária com senha nullable
    op.execute("""
    CREATE TABLE users_temp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        senha VARCHAR(255),  -- REMOVIDA RESTRIÇÃO NOT NULL
        tipo_pessoa VARCHAR(10) NOT NULL,
        cpf VARCHAR(14),
        cnpj VARCHAR(18),
        telefone VARCHAR(20),
        tipo_perfil VARCHAR(20) DEFAULT 'user',
        google_id VARCHAR(255),
        avatar_url VARCHAR(500),
        provider VARCHAR(20) DEFAULT 'local',
        created_at DATETIME,
        updated_at DATETIME,
        CONSTRAINT check_tipo_pessoa CHECK (tipo_pessoa IN ('F', 'J'))
    )
    """)
    
    # Copiar dados da tabela original
    op.execute("""
    INSERT INTO users_temp (id, nome, email, senha, tipo_pessoa, cpf, cnpj, telefone, tipo_perfil, google_id, avatar_url, provider, created_at, updated_at)
    SELECT id, nome, email, senha, tipo_pessoa, cpf, cnpj, telefone, tipo_perfil, google_id, avatar_url, provider, created_at, updated_at
    FROM users
    """)
    
    # Remover tabela original
    op.execute("DROP TABLE users")
    
    # Renomear tabela temporária
    op.execute("ALTER TABLE users_temp RENAME TO users")
    
    # Recriar índices
    op.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")
    op.execute("CREATE UNIQUE INDEX ix_users_google_id ON users (google_id)")


def downgrade() -> None:
    """Downgrade schema."""
    # Para fazer rollback, recriar com senha NOT NULL
    # (Isso vai falhar se existirem usuários OAuth com senha NULL)
    op.execute("""
    CREATE TABLE users_temp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        senha VARCHAR(255) NOT NULL,  -- VOLTA NOT NULL
        tipo_pessoa VARCHAR(10) NOT NULL,
        cpf VARCHAR(14),
        cnpj VARCHAR(18),
        telefone VARCHAR(20),
        tipo_perfil VARCHAR(20) DEFAULT 'user',
        google_id VARCHAR(255),
        avatar_url VARCHAR(500),
        provider VARCHAR(20) DEFAULT 'local',
        created_at DATETIME,
        updated_at DATETIME,
        CONSTRAINT check_tipo_pessoa CHECK (tipo_pessoa IN ('F', 'J'))
    )
    """)
    
    # Copiar apenas usuários com senha (excluir OAuth)
    op.execute("""
    INSERT INTO users_temp (id, nome, email, senha, tipo_pessoa, cpf, cnpj, telefone, tipo_perfil, google_id, avatar_url, provider, created_at, updated_at)
    SELECT id, nome, email, senha, tipo_pessoa, cpf, cnpj, telefone, tipo_perfil, google_id, avatar_url, provider, created_at, updated_at
    FROM users
    WHERE senha IS NOT NULL
    """)
    
    op.execute("DROP TABLE users")
    op.execute("ALTER TABLE users_temp RENAME TO users")
    
    # Recriar índices
    op.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")
    op.execute("CREATE UNIQUE INDEX ix_users_google_id ON users (google_id)")
