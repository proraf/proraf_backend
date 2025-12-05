from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.batch import Batch
from proraf.models.product import Product
from proraf.models.user import User
from proraf.schemas.batch import BatchCreate, BatchUpdate, BatchResponse, BatchBlockchainUpdate
from proraf.security import get_current_active_user, verify_api_key
from proraf.services.qrcode_service import generate_qrcode

router = APIRouter(prefix="/batches", tags=["Lotes"])

# Lista de campos blockchain que são imutáveis
BLOCKCHAIN_FIELDS = [
    "blockchain_address_who",
    "blockchain_address_to", 
    "blockchain_product_name",
    "blockchain_product_expedition_date",
    "blockchain_product_type",
    "blockchain_batch_id",
    "blockchain_unit_of_measure",
    "blockchain_batch_quantity",
    "blockchain_token_id"
]


@router.post("/", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def create_batch(
    batch: BatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Cria novo lote"""
    # Verifica se código já existe
    db_batch = db.query(Batch).filter(Batch.code == batch.code).first()
    if db_batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch code already exists"
        )
    
    # Verifica se produto existe
    product = db.query(Product).filter(Product.id == batch.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Cria lote
    db_batch = Batch(**batch.model_dump(), user_id=current_user.id)
    
    # Gera QR Code
    qrcode_data = f"PRORAF-{batch.code}-{product.code}"
    db_batch.qrcode = generate_qrcode(qrcode_data)
    
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    
    return db_batch


@router.get("/", response_model=List[BatchResponse])
async def list_batches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    product_id: int = Query(None),
    status_filter: bool = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Lista lotes com filtros"""
    query = db.query(Batch)
    
    if product_id:
        query = query.filter(Batch.product_id == product_id)
    
    if status_filter is not None:
        query = query.filter(Batch.status == status_filter)
    
    # Usuário comum só vê seus próprios lotes
    if current_user.tipo_perfil != "admin":
        query = query.filter(Batch.user_id == current_user.id)
    
    batches = query.offset(skip).limit(limit).all()
    return batches


@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Obtém lote por ID"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verifica permissão
    if current_user.tipo_perfil != "admin" and batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this batch"
        )
    
    return batch


@router.get("/code/{batch_code}", response_model=BatchResponse)
async def get_batch_by_code(
    batch_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Obtém lote por código"""
    batch = db.query(Batch).filter(Batch.code == batch_code).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    return batch


@router.put("/{batch_id}", response_model=BatchResponse)
async def update_batch(
    batch_id: int,
    batch_update: BatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Atualiza lote"""
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not db_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verifica permissão
    if current_user.tipo_perfil != "admin" and db_batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this batch"
        )
    
    update_data = batch_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_batch, field, value)
    
    db.commit()
    db.refresh(db_batch)
    
    return db_batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Deleta lote (soft delete)"""
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not db_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verifica permissão
    if current_user.tipo_perfil != "admin" and db_batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this batch"
        )
    
    db_batch.status = False
    db.commit()
    
    return None


@router.patch("/{batch_id}/blockchain", response_model=BatchResponse)
async def update_batch_blockchain(
    batch_id: int,
    blockchain_data: BatchBlockchainUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Atualiza campos blockchain do lote.
    ATENÇÃO: Campos blockchain são IMUTÁVEIS após o primeiro preenchimento.
    """
    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not db_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verifica permissão
    if current_user.tipo_perfil != "admin" and db_batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this batch"
        )
    
    # Verifica se dados blockchain já foram preenchidos (imutabilidade)
    if db_batch.blockchain_token_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blockchain data already registered and cannot be modified. Blockchain records are immutable."
        )
    
    # Atualiza campos blockchain
    update_data = blockchain_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_batch, field, value)
    
    db.commit()
    db.refresh(db_batch)
    
    return db_batch