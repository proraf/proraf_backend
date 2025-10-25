from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.field_data import FieldData
from proraf.schemas.field_data import FieldDataCreate, FieldDataResponse
from proraf.schemas.pagination import PaginatedResponse
from pydantic import BaseModel

# Schema específico para resposta paginada de field data
class FieldDataPaginatedResponse(BaseModel):
    total: int
    items: List[FieldDataResponse]

router = APIRouter(prefix="/field-data", tags=["Field Data"])
@router.post("/", response_model=FieldDataResponse, summary="Cria um novo dado de campo")
async def create_field_data(
    field_data: FieldDataCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo registro de dado de campo.
    """
    db_field_data = FieldData(**field_data.dict())
    db.add(db_field_data)
    db.commit()
    db.refresh(db_field_data)
    return db_field_data
@router.get("/", response_model=FieldDataPaginatedResponse, summary="Lista dados de campo com paginação")
async def list_field_data(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """
    Lista dados de campo com suporte à paginação.
    """
    total = db.query(FieldData).count()
    field_data_list = db.query(FieldData).offset(skip).limit(limit).all()
    return FieldDataPaginatedResponse(
        total=total,
        items=field_data_list
    )
@router.get("/{field_data_id}", response_model=FieldDataResponse, summary="Obtém um dado de campo por ID")
async def get_field_data(
    field_data_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém um dado de campo específico pelo seu ID.
    """
    db_field_data = db.query(FieldData).filter(FieldData.id == field_data_id).first()
    if not db_field_data:
        raise HTTPException(status_code=404, detail="Dado de campo não encontrado")
    return db_field_data
@router.delete("/{field_data_id}", status_code=204, summary="Deleta um dado de campo por ID")
async def delete_field_data(
    field_data_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta um dado de campo específico pelo seu ID.
    """
    db_field_data = db.query(FieldData).filter(FieldData.id == field_data_id).first()
    if not db_field_data:
        raise HTTPException(status_code=404, detail="Dado de campo não encontrado")
    db.delete(db_field_data)
    db.commit()
    return
@router.put("/{field_data_id}", response_model=FieldDataResponse, summary="Atualiza um dado de campo por ID")
async def update_field_data(
    field_data_id: int,
    field_data_update: FieldDataCreate,
    db: Session = Depends(get_db)
):
    """
    Atualiza um dado de campo específico pelo seu ID.
    """
    db_field_data = db.query(FieldData).filter(FieldData.id == field_data_id).first()
    if not db_field_data:
        raise HTTPException(status_code=404, detail="Dado de campo não encontrado")
    
    for key, value in field_data_update.dict().items():
        setattr(db_field_data, key, value)
    
    db.commit()
    db.refresh(db_field_data)
    return db_field_data
