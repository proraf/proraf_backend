from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class BatchBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=100)
    dt_plantio: Optional[date] = None
    dt_colheita: Optional[date] = None
    dt_expedition: Optional[date] = None
    status: bool = True
    talhao: Optional[str] = Field(None, max_length=100)
    registro_talhao: bool = False
    producao: Decimal = Field(default=0)
    unidadeMedida: Optional[str] = Field(None, max_length=50)
    product_id: int
    # Campos editáveis - cópia histórica do produto
    product_name: Optional[str] = Field(None, max_length=255)
    product_type: Optional[str] = Field(None, max_length=255)


class BatchCreate(BatchBase):
    pass


class BatchUpdate(BaseModel):
    dt_plantio: Optional[date] = None
    dt_colheita: Optional[date] = None
    dt_expedition: Optional[date] = None
    status: Optional[bool] = None
    talhao: Optional[str] = Field(None, max_length=100)
    registro_talhao: Optional[bool] = None
    producao: Optional[Decimal] = None
    unidadeMedida: Optional[str] = Field(None, max_length=50)
    # Campos editáveis - cópia histórica do produto
    product_name: Optional[str] = Field(None, max_length=255)
    product_type: Optional[str] = Field(None, max_length=255)


class BatchBlockchainUpdate(BaseModel):
    """Schema para atualização de campos blockchain - imutáveis após primeiro preenchimento"""
    blockchain_address_who: Optional[str] = Field(None, max_length=255)
    blockchain_address_to: Optional[str] = Field(None, max_length=255)
    blockchain_product_name: Optional[str] = Field(None, max_length=255)
    blockchain_product_expedition_date: Optional[str] = Field(None, max_length=100)
    blockchain_product_type: Optional[str] = Field(None, max_length=255)
    blockchain_batch_id: Optional[str] = Field(None, max_length=255)
    blockchain_unit_of_measure: Optional[str] = Field(None, max_length=100)
    blockchain_batch_quantity: Optional[float] = None
    blockchain_token_id: Optional[int] = None


class BatchResponse(BatchBase):
    id: int
    user_id: int
    qrcode: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Campos blockchain - imutáveis
    blockchain_address_who: Optional[str] = None
    blockchain_address_to: Optional[str] = None
    blockchain_product_name: Optional[str] = None
    blockchain_product_expedition_date: Optional[str] = None
    blockchain_product_type: Optional[str] = None
    blockchain_batch_id: Optional[str] = None
    blockchain_unit_of_measure: Optional[str] = None
    blockchain_batch_quantity: Optional[float] = None
    blockchain_token_id: Optional[int] = None
    
    class Config:
        from_attributes = True