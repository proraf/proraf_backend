from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class MovementBase(BaseModel):
    tipo_movimentacao: str = Field(..., min_length=1, max_length=50, description="Tipo: plantio, colheita, expedição, etc.")
    quantidade: Decimal = Field(default=0, ge=0, description="Quantidade movimentada")
    batch_id: int = Field(..., description="ID do lote")
    # Campos editáveis - informações do comprador/destino
    buyer_name: Optional[str] = Field(None, max_length=255, description="Nome do comprador")
    buyer_identification: Optional[str] = Field(None, max_length=100, description="CPF/CNPJ/NIT do comprador")
    current_location: Optional[str] = Field(None, max_length=500, description="Localização atual")


class MovementCreate(MovementBase):
    pass


class MovementUpdate(BaseModel):
    tipo_movimentacao: Optional[str] = Field(None, min_length=1, max_length=50)
    quantidade: Optional[Decimal] = Field(None, ge=0)
    # Campos editáveis - informações do comprador/destino
    buyer_name: Optional[str] = Field(None, max_length=255)
    buyer_identification: Optional[str] = Field(None, max_length=100)
    current_location: Optional[str] = Field(None, max_length=500)


class MovementBlockchainUpdate(BaseModel):
    """Schema para atualização de campos blockchain - imutáveis após primeiro preenchimento"""
    blockchain_updater: Optional[str] = Field(None, max_length=255, description="Endereço Ethereum do atualizador")
    blockchain_token_id: Optional[int] = Field(None, description="Token ID NFT")
    blockchain_message: Optional[str] = Field(None, description="Mensagem/observação registrada na blockchain")
    blockchain_buyer_name: Optional[str] = Field(None, max_length=255, description="Nome do comprador (espelho blockchain)")
    blockchain_buyer_identification: Optional[str] = Field(None, max_length=100, description="Identificação do comprador (espelho blockchain)")
    blockchain_current_location: Optional[str] = Field(None, max_length=500, description="Localização (espelho blockchain)")
    blockchain_update_type: Optional[int] = Field(None, description="Tipo de atualização (código numérico)")


class MovementResponse(MovementBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    # Campos blockchain - imutáveis
    blockchain_updater: Optional[str] = None
    blockchain_token_id: Optional[int] = None
    blockchain_message: Optional[str] = None
    blockchain_buyer_name: Optional[str] = None
    blockchain_buyer_identification: Optional[str] = None
    blockchain_current_location: Optional[str] = None
    blockchain_update_type: Optional[int] = None
    
    class Config:
        from_attributes = True