from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class MovementBase(BaseModel):
    tipo_movimentacao: str = Field(..., min_length=1, max_length=50, description="Tipo: plantio, colheita, expedição, etc.")
    quantidade: Decimal = Field(default=0, ge=0, description="Quantidade movimentada")
    batch_id: int = Field(..., description="ID do lote")


class MovementCreate(MovementBase):
    pass


class MovementUpdate(BaseModel):
    tipo_movimentacao: Optional[str] = Field(None, min_length=1, max_length=50)
    quantidade: Optional[Decimal] = Field(None, ge=0)


class MovementResponse(MovementBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True