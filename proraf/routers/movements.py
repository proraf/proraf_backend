from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.movement import Movement
from proraf.models.batch import Batch
from proraf.models.user import User
from proraf.schemas.movement import MovementCreate, MovementUpdate, MovementResponse
from proraf.security import get_current_active_user, verify_api_key

router = APIRouter(
    prefix="/movements",
    tags=["Movimentações"],
    responses={
        401: {"description": "Não autorizado - Token inválido"},
        403: {"description": "Acesso negado"},
        404: {"description": "Movimentação não encontrada"}
    }
)


@router.post(
    "/",
    response_model=MovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimentação",
    description="""
    Registra uma nova movimentação de lote.
    
    **Tipos de movimentação comuns:**
    - plantio
    - colheita
    - expedição
    - venda
    - transferência
    - descarte
    
    **Requer:** API Key + Token JWT
    """,
    responses={
        201: {
            "description": "Movimentação registrada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "tipo_movimentacao": "colheita",
                        "quantidade": 500.5,
                        "batch_id": 1,
                        "user_id": 1,
                        "created_at": "2025-01-15T10:00:00"
                    }
                }
            }
        },
        404: {"description": "Lote não encontrado"}
    }
)
async def create_movement(
    movement: MovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Registra nova movimentação"""
    # Verifica se lote existe
    batch = db.query(Batch).filter(Batch.id == movement.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Verifica permissão (usuário comum só pode movimentar seus próprios lotes)
    if current_user.tipo_perfil != "admin" and batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create movement for this batch"
        )
    
    db_movement = Movement(
        **movement.model_dump(),
        user_id=current_user.id
    )
    
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    
    return db_movement


@router.get(
    "/",
    response_model=List[MovementResponse],
    summary="Listar movimentações",
    description="""
    Lista todas as movimentações com filtros.
    
    **Filtros disponíveis:**
    - batch_id: Filtrar por lote específico
    - tipo_movimentacao: Filtrar por tipo de movimentação
    
    **Requer:** API Key + Token JWT
    """
)
async def list_movements(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    batch_id: int = Query(None, description="Filtrar por ID do lote"),
    tipo_movimentacao: str = Query(None, description="Filtrar por tipo de movimentação"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Lista movimentações com filtros"""
    query = db.query(Movement)
    
    # Usuário comum só vê movimentações de seus lotes
    if current_user.tipo_perfil != "admin":
        # Busca IDs dos lotes do usuário
        user_batch_ids = db.query(Batch.id).filter(Batch.user_id == current_user.id).all()
        user_batch_ids = [batch_id[0] for batch_id in user_batch_ids]
        query = query.filter(Movement.batch_id.in_(user_batch_ids))
    
    if batch_id:
        query = query.filter(Movement.batch_id == batch_id)
    
    if tipo_movimentacao:
        query = query.filter(Movement.tipo_movimentacao == tipo_movimentacao)
    
    movements = query.offset(skip).limit(limit).all()
    return movements


@router.get(
    "/{movement_id}",
    response_model=MovementResponse,
    summary="Buscar movimentação por ID",
    description="""
    Retorna detalhes de uma movimentação específica.
    
    **Requer:** API Key + Token JWT
    """
)
async def get_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Obtém movimentação por ID"""
    movement = db.query(Movement).filter(Movement.id == movement_id).first()
    
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )
    
    # Verifica permissão
    if current_user.tipo_perfil != "admin" and movement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this movement"
        )
    
    return movement


@router.get(
    "/batch/{batch_id}",
    response_model=List[MovementResponse],
    summary="Listar movimentações de um lote",
    description="""
    Retorna todas as movimentações de um lote específico.
    
    Útil para rastreabilidade completa de um lote.
    
    **Requer:** API Key + Token JWT
    """
)
async def list_movements_by_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Lista todas as movimentações de um lote"""
    # Verifica se lote existe
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
            detail="Not authorized to access movements from this batch"
        )
    
    movements = db.query(Movement).filter(Movement.batch_id == batch_id).all()
    return movements


@router.put(
    "/{movement_id}",
    response_model=MovementResponse,
    summary="Atualizar movimentação",
    description="""
    Atualiza dados de uma movimentação existente.
    
    Apenas os campos enviados serão atualizados.
    
    **Requer:** API Key + Token JWT
    """
)
async def update_movement(
    movement_id: int,
    movement_update: MovementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Atualiza movimentação"""
    db_movement = db.query(Movement).filter(Movement.id == movement_id).first()
    
    if not db_movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )
    
    # Verifica permissão
    if current_user.tipo_perfil != "admin" and db_movement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this movement"
        )
    
    update_data = movement_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_movement, field, value)
    
    db.commit()
    db.refresh(db_movement)
    
    return db_movement


@router.delete(
    "/{movement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar movimentação",
    description="""
    Remove uma movimentação do sistema.
    
    **Atenção:** Esta é uma deleção permanente (hard delete).
    
    **Requer:** API Key + Token JWT
    """
)
async def delete_movement(
    movement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Deleta movimentação"""
    db_movement = db.query(Movement).filter(Movement.id == movement_id).first()
    
    if not db_movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movement not found"
        )
    
    # Verifica permissão
    if current_user.tipo_perfil != "admin" and db_movement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this movement"
        )
    
    db.delete(db_movement)
    db.commit()
    
    return None