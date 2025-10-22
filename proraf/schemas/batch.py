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


class BatchResponse(BatchBase):
    id: int
    user_id: int
    qrcode: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True