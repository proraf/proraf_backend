from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    comertial_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    variedade_cultivar: Optional[str] = Field(None, max_length=255)
    status: bool = True
    image: Optional[str] = Field(None, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    comertial_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    variedade_cultivar: Optional[str] = Field(None, max_length=255)
    status: Optional[bool] = None
    image: Optional[str] = Field(None, max_length=255)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True