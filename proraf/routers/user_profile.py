from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.user import User
from proraf.models.batch import Batch
from proraf.models.movement import Movement
from proraf.models.product import Product
from proraf.schemas.user import UserResponse, UserUpdate
from proraf.security import get_current_active_user, verify_api_key, get_password_hash
from sqlalchemy import func

router = APIRouter(
    prefix="/user",
    tags=["Usuário - Perfil"],
    responses={
        401: {"description": "Não autorizado"},
        404: {"description": "Usuário não encontrado"}
    }
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obter dados do usuário logado",
    description="""
    Retorna os dados do usuário atualmente autenticado.
    
    **Requer:** API Key + Token JWT
    """
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna dados do usuário logado"""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Atualizar dados do usuário logado",
    description="""
    Permite que o usuário atualize seus próprios dados.
    
    **Campos atualizáveis:**
    - nome
    - telefone
    - senha
    
    **Requer:** API Key + Token JWT
    """
)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Atualiza dados do usuário logado"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Se senha foi enviada, fazer hash
    if "senha" in update_data:
        update_data["senha"] = get_password_hash(update_data["senha"])
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get(
    "/me/stats",
    summary="Estatísticas do usuário",
    description="""
    Retorna estatísticas do usuário logado.
    
    **Informações:**
    - Total de lotes
    - Total de movimentações
    - Total de produtos cadastrados
    - Lotes ativos/inativos
    
    **Requer:** API Key + Token JWT
    """
)
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna estatísticas do usuário"""
    
    # Total de lotes
    total_batches = db.query(Batch).filter(Batch.user_id == current_user.id).count()
    active_batches = db.query(Batch).filter(
        Batch.user_id == current_user.id,
        Batch.status == True
    ).count()
    
    # Total de movimentações
    total_movements = db.query(Movement).filter(
        Movement.user_id == current_user.id
    ).count()
    
    # Produção total
    total_production = db.query(func.sum(Batch.producao)).filter(
        Batch.user_id == current_user.id
    ).scalar() or 0
    
    # Movimentações por tipo
    movements_by_type = db.query(
        Movement.tipo_movimentacao,
        func.count(Movement.id).label('count')
    ).filter(
        Movement.user_id == current_user.id
    ).group_by(Movement.tipo_movimentacao).all()
    
    # Produtos únicos (através dos lotes)
    unique_products = db.query(func.count(func.distinct(Batch.product_id))).filter(
        Batch.user_id == current_user.id
    ).scalar() or 0
    
    return {
        "batches": {
            "total": total_batches,
            "active": active_batches,
            "inactive": total_batches - active_batches
        },
        "movements": {
            "total": total_movements,
            "by_type": [
                {"type": tipo, "count": count}
                for tipo, count in movements_by_type
            ]
        },
        "production": {
            "total": float(total_production)
        },
        "products": {
            "unique_products": unique_products
        }
    }


@router.get(
    "/me/batches",
    summary="Lotes do usuário",
    description="""
    Retorna todos os lotes do usuário logado.
    
    **Requer:** API Key + Token JWT
    """
)
async def get_user_batches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna lotes do usuário"""
    batches = db.query(Batch).filter(
        Batch.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return batches


@router.get(
    "/me/movements",
    summary="Movimentações do usuário",
    description="""
    Retorna todas as movimentações do usuário logado.
    
    **Requer:** API Key + Token JWT
    """
)
async def get_user_movements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna movimentações do usuário"""
    movements = db.query(Movement).filter(
        Movement.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return movements


@router.get(
    "/me/recent-activity",
    summary="Atividade recente do usuário",
    description="""
    Retorna as atividades mais recentes do usuário.
    
    **Requer:** API Key + Token JWT
    """
)
async def get_user_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna atividade recente do usuário"""
    
    # Últimas movimentações
    recent_movements = db.query(Movement).filter(
        Movement.user_id == current_user.id
    ).order_by(Movement.created_at.desc()).limit(limit).all()
    
    # Últimos lotes criados
    recent_batches = db.query(Batch).filter(
        Batch.user_id == current_user.id
    ).order_by(Batch.created_at.desc()).limit(limit).all()
    
    return {
        "recent_movements": [
            {
                "id": m.id,
                "type": m.tipo_movimentacao,
                "quantity": float(m.quantidade),
                "batch_id": m.batch_id,
                "created_at": m.created_at.isoformat()
            }
            for m in recent_movements
        ],
        "recent_batches": [
            {
                "id": b.id,
                "code": b.code,
                "product_id": b.product_id,
                "created_at": b.created_at.isoformat()
            }
            for b in recent_batches
        ]
    }


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar própria conta",
    description="""
    Permite que o usuário delete sua própria conta.
    
    **ATENÇÃO:** Esta ação é irreversível!
    
    **Requer:** API Key + Token JWT
    """
)
async def delete_own_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Permite usuário deletar sua própria conta"""
    db.delete(current_user)
    db.commit()
    return None