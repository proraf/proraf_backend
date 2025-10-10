from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.product import Product
from proraf.models.user import User
from proraf.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from proraf.security import get_current_active_user, verify_api_key

router = APIRouter(
    prefix="/products",
    tags=["Produtos"],
    responses={
        401: {"description": "Não autorizado - Token inválido"},
        403: {"description": "Acesso negado"},
        404: {"description": "Produto não encontrado"}
    }
)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
    description="""
    Cria um novo produto agrícola no sistema.
    
    **Campos obrigatórios:**
    - name: Nome do produto
    - code: Código único do produto
    
    **Requer:** API Key + Token JWT
    """,
    responses={
        201: {
            "description": "Produto criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Tomate Cereja",
                        "code": "TOM-001",
                        "status": True,
                        "created_at": "2025-01-15T10:00:00"
                    }
                }
            }
        },
        400: {"description": "Código do produto já existe"}
    }
)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Cria novo produto"""
    # Verifica se código já existe
    db_product = db.query(Product).filter(Product.code == product.code).first()
    if db_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists"
        )
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.get(
    "/",
    response_model=List[ProductResponse],
    summary="Listar produtos",
    description="""
    Lista todos os produtos com paginação e filtros.
    
    **Parâmetros de query:**
    - skip: Quantidade de registros a pular (padrão: 0)
    - limit: Quantidade máxima de registros (padrão: 100, máx: 100)
    - status_filter: Filtrar por status ativo/inativo
    
    **Requer:** API Key + Token JWT
    """
)
async def list_products(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    status_filter: bool = Query(None, description="Filtrar por status (true=ativo, false=inativo)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Lista produtos com paginação"""
    query = db.query(Product)
    
    if status_filter is not None:
        query = query.filter(Product.status == status_filter)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Buscar produto por ID",
    description="""
    Retorna detalhes de um produto específico.
    
    **Requer:** API Key + Token JWT
    """
)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Obtém produto por ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Atualizar produto",
    description="""
    Atualiza dados de um produto existente.
    
    Apenas os campos enviados serão atualizados.
    
    **Requer:** API Key + Token JWT
    """
)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Atualiza produto"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar produto",
    description="""
    Desativa um produto (soft delete).
    
    O produto não é removido do banco, apenas marcado como inativo.
    
    **Requer:** API Key + Token JWT
    """
)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Deleta produto (soft delete)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db_product.status = False
    db.commit()
    
    return None