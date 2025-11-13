from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class FieldDataBase(BaseModel):
    latitude: Optional[str] = Field(None, example="-29.123456")
    longitude: Optional[str] = Field(None, example="-53.123456")
    mapa: Optional[str] = Field(None, example="url_do_mapa.jpg")
    imagem_aerea: Optional[str] = Field(None, example="url_imagem_aerea.jpg")
    imagem_perfil: Optional[str] = Field(None, example="url_imagem_perfil.jpg")
    imagem_fundo: Optional[str] = Field(None, example="url_imagem_fundo.jpg")
    observacoes: Optional[str] = Field(None, example="Observações sobre o campo")

class FieldDataCreate(FieldDataBase):
    pass

class FieldDataUpdate(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    mapa: Optional[str] = None
    imagem_aerea: Optional[str] = None
    imagem_perfil: Optional[str] = None
    imagem_fundo: Optional[str] = None
    observacoes: Optional[str] = None

class FieldDataResponse(FieldDataBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True