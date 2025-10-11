from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from proraf.database import get_db
from proraf.models.user import User
from proraf.models.product import Product
from proraf.models.batch import Batch
from proraf.models.movement import Movement
from proraf.security import require_admin, verify_api_key

router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin - Dashboard"],
    responses={
        401: {"description": "Não autorizado"},
        403: {"description": "Acesso negado - Requer admin"}
    }
)


@router.get(
    "/overview",
    summary="[ADMIN] Visão geral do sistema",
    description="""
    Retorna estatísticas gerais do sistema ProRAF.
    
    **Informações:**
    - Total de usuários, produtos, lotes
    - Movimentações registradas
    - Lotes ativos/inativos
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna visão geral do dashboard"""
    
    # Estatísticas de usuários
    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.tipo_perfil == "admin").count()
    
    # Estatísticas de produtos
    total_products = db.query(Product).count()
    active_products = db.query(Product).filter(Product.status == True).count()
    
    # Estatísticas de lotes
    total_batches = db.query(Batch).count()
    active_batches = db.query(Batch).filter(Batch.status == True).count()
    
    # Estatísticas de movimentações
    total_movements = db.query(Movement).count()
    
    # Movimentações por tipo (top 5)
    movements_by_type = db.query(
        Movement.tipo_movimentacao,
        func.count(Movement.id).label('count')
    ).group_by(Movement.tipo_movimentacao).order_by(func.count(Movement.id).desc()).limit(5).all()
    
    return {
        "users": {
            "total": total_users,
            "admins": total_admins,
            "regular": total_users - total_admins
        },
        "products": {
            "total": total_products,
            "active": active_products,
            "inactive": total_products - active_products
        },
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
        }
    }


@router.get(
    "/recent-activity",
    summary="[ADMIN] Atividades recentes",
    description="""
    Lista as atividades mais recentes do sistema.
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna atividades recentes"""
    
    # Últimas movimentações
    recent_movements = db.query(Movement).order_by(
        Movement.created_at.desc()
    ).limit(limit).all()
    
    # Últimos lotes criados
    recent_batches = db.query(Batch).order_by(
        Batch.created_at.desc()
    ).limit(limit).all()
    
    # Últimos usuários registrados
    recent_users = db.query(User).order_by(
        User.created_at.desc()
    ).limit(limit).all()
    
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
        ],
        "recent_users": [
            {
                "id": u.id,
                "nome": u.nome,
                "email": u.email,
                "tipo_perfil": u.tipo_perfil,
                "created_at": u.created_at.isoformat()
            }
            for u in recent_users
        ]
    }


@router.get(
    "/production-summary",
    summary="[ADMIN] Resumo de produção",
    description="""
    Retorna resumo da produção por produto.
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def get_production_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna resumo de produção"""
    
    # Produção total por produto
    production_by_product = db.query(
        Product.name,
        Product.code,
        func.count(Batch.id).label('total_batches'),
        func.sum(Batch.producao).label('total_production')
    ).join(Batch, Product.id == Batch.product_id).group_by(
        Product.id, Product.name, Product.code
    ).all()
    
    return {
        "production": [
            {
                "product_name": name,
                "product_code": code,
                "total_batches": total_batches,
                "total_production": float(total_production) if total_production else 0
            }
            for name, code, total_batches, total_production in production_by_product
        ]
    }