from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.batch import Batch
from proraf.models.product import Product
from proraf.models.user import User
from proraf.models.movement import Movement
from proraf.security import verify_api_key
from sqlalchemy import func

router = APIRouter(
    prefix="/tracking",
    tags=["Rastreamento Público"],
    responses={
        404: {"description": "Lote não encontrado"}
    }
)


@router.get(
    "/{batch_code}",
    summary="Rastrear lote por código",
    description="""
    Rota pública para rastreamento de lotes.
    
    **Não requer autenticação de usuário**, apenas API Key.
    
    Retorna informações completas sobre:
    - Dados do lote
    - Dados do produto
    - Dados do produtor (usuário dono do lote)
    - Histórico de movimentações
    - QR Code
    
    **Uso:** Ideal para consumidores finais rastrearem produtos via QR Code
    
    **Requer:** Apenas API Key
    """,
    responses={
        200: {
            "description": "Informações de rastreamento",
            "content": {
                "application/json": {
                    "example": {
                        "batch": {
                            "id": 1,
                            "code": "LOTE-2025-001",
                            "dt_plantio": "2025-01-01",
                            "dt_colheita": "2025-03-15",
                            "dt_expedition": "2025-03-20",
                            "producao": 1500.5,
                            "talhao": "Talhão A1",
                            "qrcode": "QR-abc123...",
                            "status": True
                        },
                        "product": {
                            "id": 1,
                            "name": "Tomate Cereja",
                            "comertial_name": "Tomate Sweet Cherry",
                            "description": "Tomate orgânico cultivado sem agrotóxicos",
                            "variedade_cultivar": "Sweet 100",
                            "image": "/static/images/products/...",
                            "code": "TOM-001"
                        },
                        "producer": {
                            "nome": "João Silva",
                            "tipo_pessoa": "F",
                            "cidade": "Alegrete",
                            "estado": "RS"
                        },
                        "movements": [
                            {
                                "tipo_movimentacao": "plantio",
                                "quantidade": 2000,
                                "created_at": "2025-01-01T10:00:00"
                            },
                            {
                                "tipo_movimentacao": "colheita",
                                "quantidade": 1900,
                                "created_at": "2025-03-15T08:00:00"
                            }
                        ],
                        "stats": {
                            "total_movements": 3,
                            "days_since_planting": 74
                        }
                    }
                }
            }
        }
    }
)
async def track_batch(
    batch_code: str,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Rastreia um lote pelo código (público)
    Não requer autenticação de usuário
    """
    # Busca lote pelo código
    batch = db.query(Batch).filter(Batch.code == batch_code).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    
    # Busca produto relacionado
    product = db.query(Product).filter(Product.id == batch.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Busca produtor (usuário dono do lote)
    producer = db.query(User).filter(User.id == batch.user_id).first()
    
    if not producer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produtor não encontrado"
        )
    
    # Busca movimentações do lote (ordenadas por data)
    movements = db.query(Movement).filter(
        Movement.batch_id == batch.id
    ).order_by(Movement.created_at).all()
    
    # Calcula dias desde plantio
    days_since_planting = None
    if batch.dt_plantio:
        from datetime import datetime, date
        if isinstance(batch.dt_plantio, str):
            plant_date = datetime.fromisoformat(batch.dt_plantio).date()
        else:
            plant_date = batch.dt_plantio
        
        today = date.today()
        days_since_planting = (today - plant_date).days
    
    # Monta resposta com informações públicas
    return {
        "batch": {
            "id": batch.id,
            "code": batch.code,
            "dt_plantio": batch.dt_plantio.isoformat() if batch.dt_plantio else None,
            "dt_colheita": batch.dt_colheita.isoformat() if batch.dt_colheita else None,
            "dt_expedition": batch.dt_expedition.isoformat() if batch.dt_expedition else None,
            "producao": float(batch.producao),
            "talhao": batch.talhao,
            "qrcode": batch.qrcode,
            "status": batch.status,
            "created_at": batch.created_at.isoformat()
        },
        "product": {
            "id": product.id,
            "name": product.name,
            "comertial_name": product.comertial_name,
            "description": product.description,
            "variedade_cultivar": product.variedade_cultivar,
            "image": product.image,
            "code": product.code
        },
        "producer": {
            "nome": producer.nome,
            "tipo_pessoa": producer.tipo_pessoa,
            # Não expõe dados sensíveis (email, cpf, cnpj, telefone)
            "tipo_perfil": producer.tipo_perfil
        },
        "movements": [
            {
                "id": m.id,
                "tipo_movimentacao": m.tipo_movimentacao,
                "quantidade": float(m.quantidade),
                "created_at": m.created_at.isoformat()
            }
            for m in movements
        ],
        "stats": {
            "total_movements": len(movements),
            "days_since_planting": days_since_planting,
            "total_production": float(batch.producao)
        }
    }


@router.get(
    "/qr/{qrcode}",
    summary="Rastrear lote por QR Code",
    description="""
    Rastreia um lote pelo QR Code gerado automaticamente.
    
    **Não requer autenticação de usuário**, apenas API Key.
    
    **Requer:** Apenas API Key
    """
)
async def track_batch_by_qrcode(
    qrcode: str,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """
    Rastreia um lote pelo QR Code (público)
    """
    # Busca lote pelo QR Code
    batch = db.query(Batch).filter(Batch.qrcode == qrcode).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado para este QR Code"
        )
    
    # Redireciona para a função principal usando o código do lote
    return await track_batch(batch.code, db, api_key_valid)