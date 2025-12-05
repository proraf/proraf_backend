"""add_blockchain_fields_to_batch_and_movement

Revision ID: 0d5696186205
Revises: 454a825713d0
Create Date: 2025-12-04 19:26:24.824678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d5696186205'
down_revision: Union[str, Sequence[str], None] = '454a825713d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Adiciona campos blockchain em batch e movement."""
    
    # === BATCH ===
    # Campos editáveis - cópia histórica do produto
    op.add_column('batch', sa.Column('product_name', sa.String(255), nullable=True))
    op.add_column('batch', sa.Column('product_type', sa.String(255), nullable=True))
    
    # Campos blockchain - imutáveis após preenchimento
    op.add_column('batch', sa.Column('blockchain_address_who', sa.String(255), nullable=True))
    op.add_column('batch', sa.Column('blockchain_address_to', sa.String(255), nullable=True))
    op.add_column('batch', sa.Column('blockchain_product_name', sa.String(255), nullable=True))
    op.add_column('batch', sa.Column('blockchain_product_expedition_date', sa.String(100), nullable=True))
    op.add_column('batch', sa.Column('blockchain_product_type', sa.String(255), nullable=True))
    op.add_column('batch', sa.Column('blockchain_batch_id', sa.String(255), nullable=True))
    op.add_column('batch', sa.Column('blockchain_unit_of_measure', sa.String(100), nullable=True))
    op.add_column('batch', sa.Column('blockchain_batch_quantity', sa.Float, nullable=True))
    op.add_column('batch', sa.Column('blockchain_token_id', sa.Integer, nullable=True))
    
    # === MOVEMENT ===
    # Campos editáveis - informações do comprador/destino
    op.add_column('movements', sa.Column('buyer_name', sa.String(255), nullable=True))
    op.add_column('movements', sa.Column('buyer_identification', sa.String(100), nullable=True))
    op.add_column('movements', sa.Column('current_location', sa.String(500), nullable=True))
    
    # Campos blockchain - imutáveis após preenchimento
    op.add_column('movements', sa.Column('blockchain_updater', sa.String(255), nullable=True))
    op.add_column('movements', sa.Column('blockchain_token_id', sa.Integer, nullable=True))
    op.add_column('movements', sa.Column('blockchain_message', sa.Text, nullable=True))
    op.add_column('movements', sa.Column('blockchain_buyer_name', sa.String(255), nullable=True))
    op.add_column('movements', sa.Column('blockchain_buyer_identification', sa.String(100), nullable=True))
    op.add_column('movements', sa.Column('blockchain_current_location', sa.String(500), nullable=True))
    op.add_column('movements', sa.Column('blockchain_update_type', sa.Integer, nullable=True))


def downgrade() -> None:
    """Downgrade schema - Remove campos blockchain de batch e movement."""
    
    # === MOVEMENT ===
    op.drop_column('movements', 'blockchain_update_type')
    op.drop_column('movements', 'blockchain_current_location')
    op.drop_column('movements', 'blockchain_buyer_identification')
    op.drop_column('movements', 'blockchain_buyer_name')
    op.drop_column('movements', 'blockchain_message')
    op.drop_column('movements', 'blockchain_token_id')
    op.drop_column('movements', 'blockchain_updater')
    op.drop_column('movements', 'current_location')
    op.drop_column('movements', 'buyer_identification')
    op.drop_column('movements', 'buyer_name')
    
    # === BATCH ===
    op.drop_column('batch', 'blockchain_token_id')
    op.drop_column('batch', 'blockchain_batch_quantity')
    op.drop_column('batch', 'blockchain_unit_of_measure')
    op.drop_column('batch', 'blockchain_batch_id')
    op.drop_column('batch', 'blockchain_product_type')
    op.drop_column('batch', 'blockchain_product_expedition_date')
    op.drop_column('batch', 'blockchain_product_name')
    op.drop_column('batch', 'blockchain_address_to')
    op.drop_column('batch', 'blockchain_address_who')
    op.drop_column('batch', 'product_type')
    op.drop_column('batch', 'product_name')
