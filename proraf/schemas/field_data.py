from typing import Optional
from pydantic import BaseModel, Field

class FieldDataBase(BaseModel):
    name: str = Field(..., example="Nome do Campo")
    type: str = Field(..., example="Tipo do Campo")
    required: bool = Field(..., example=True)

class FieldDataCreate(FieldDataBase):
    pass

class FieldDataResponse(FieldDataBase):
    id: int
    created_at: str
    updated_at: str
    class Config:
        from_attributes = True