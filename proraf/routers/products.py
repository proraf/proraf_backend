from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi import status as http_status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from proraf.database import get_db
from proraf.models.product import Product
from proraf.models.user import User
from proraf.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductImageUpload
from proraf.security import get_current_active_user, verify_api_key
from proraf.services.file_service import FileService

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
    status_code=http_status.HTTP_201_CREATED,
    summary="Criar produto",
    description="""
    Cria um novo produto agrícola no sistema.
    
    **Campos obrigatórios:**
    - name: Nome do produto
    - code: Código único do produto
    
    **Campos opcionais:**
    - comertial_name: Nome comercial do produto
    - description: Descrição detalhada
    - variedade_cultivar: Variedade ou cultivar
    - status: Status ativo/inativo (padrão: true)
    - image: URL da imagem do produto (deve começar com http://, https:// ou data:)
    
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
                        "comertial_name": "Tomate Sweet Cherry",
                        "code": "TOM-001",
                        "image": "https://example.com/images/tomate-cereja.jpg",
                        "status": True,
                        "created_at": "2025-01-15T10:00:00"
                    }
                }
            }
        },
        400: {"description": "Código do produto já existe ou dados inválidos"}
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
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists"
        )
    
    # Cria produto com user_id do usuário logado
    product_data = product.model_dump()
    product_data["user_id"] = current_user.id
    
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.post(
    "/with-image",
    response_model=ProductResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Criar produto com imagem",
    description="""
    Cria um novo produto com upload de imagem em uma única requisição.
    
    **Campos obrigatórios:**
    - name: Nome do produto
    - code: Código único do produto
    
    **Campos opcionais:**
    - comertial_name: Nome comercial do produto
    - description: Descrição detalhada
    - variedade_cultivar: Variedade ou cultivar
    - status: Status ativo/inativo (padrão: true)
    - image: Arquivo de imagem (JPG, JPEG, PNG, WEBP, máx 5MB)
    
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
                        "comertial_name": "Tomate Sweet Cherry",
                        "code": "TOM-001",
                        "image": "/static/images/products/550e8400-e29b-41d4-a716-446655440000.jpg",
                        "status": True,
                        "created_at": "2025-01-15T10:00:00"
                    }
                }
            }
        },
        400: {"description": "Código do produto já existe ou dados inválidos"}
    }
)
async def create_product_with_image(
    name: str = Form(..., description="Nome do produto"),
    code: str = Form(..., description="Código único do produto"),
    comertial_name: str = Form(None, description="Nome comercial do produto"),
    description: str = Form(None, description="Descrição detalhada"),
    variedade_cultivar: str = Form(None, description="Variedade ou cultivar"),
    status: bool = Form(True, description="Status ativo/inativo"),
    image: UploadFile = File(None, description="Arquivo de imagem"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Cria novo produto com upload de imagem"""
    
    # Validação básica dos campos obrigatórios
    if not name or len(name.strip()) < 3:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Nome do produto deve ter pelo menos 3 caracteres"
        )
    
    if not code or len(code.strip()) < 1:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Código do produto é obrigatório"
        )
    
    # Limpar e normalizar campos opcionais
    name = name.strip()
    code = code.strip()
    comertial_name = comertial_name.strip() if comertial_name else None
    description = description.strip() if description else None
    variedade_cultivar = variedade_cultivar.strip() if variedade_cultivar else None
    
    # Verifica se código já existe
    db_product = db.query(Product).filter(Product.code == code).first()
    if db_product:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists"
        )
    
    # Upload da imagem se fornecida
    image_path = None
    if image and image.filename:
        image_path = await FileService.save_product_image(image)
        image_path = f"/{image_path}"
    
    # Criar produto com user_id
    product_data = {
        "name": name,
        "code": code,
        "comertial_name": comertial_name,
        "description": description,
        "variedade_cultivar": variedade_cultivar,
        "status": status,
        "image": image_path,
        "user_id": current_user.id
    }
    
    db_product = Product(**product_data)
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
    - my_products_only: Se true, lista apenas produtos do usuário logado
    - user_id: ID do usuário para filtrar produtos (apenas para admins)
    
    **Requer:** API Key + Token JWT
    """
)
async def list_products(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    status_filter: bool = Query(None, description="Filtrar por status (true=ativo, false=inativo)"),
    my_products_only: bool = Query(False, description="Listar apenas meus produtos"),
    user_id: int = Query(None, description="Filtrar produtos por usuário específico (apenas admins)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Lista produtos com paginação e filtros"""
    query = db.query(Product)
    
    # Filtro por status
    if status_filter is not None:
        query = query.filter(Product.status == status_filter)
    
    # Filtro por usuário
    if my_products_only:
        query = query.filter(Product.user_id == current_user.id)
    elif user_id is not None:
        # Apenas admins podem filtrar por outros usuários
        if current_user.tipo_perfil != "admin":
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem filtrar por outros usuários"
            )
        query = query.filter(Product.user_id == user_id)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get(
    "/my-products",
    response_model=List[ProductResponse],
    summary="Listar meus produtos",
    description="""
    Lista todos os produtos criados pelo usuário logado.
    
    **Parâmetros de query:**
    - skip: Quantidade de registros a pular (padrão: 0)
    - limit: Quantidade máxima de registros (padrão: 100, máx: 100)
    - status_filter: Filtrar por status ativo/inativo
    
    **Requer:** API Key + Token JWT
    """
)
async def list_my_products(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    status_filter: bool = Query(None, description="Filtrar por status (true=ativo, false=inativo)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Lista produtos criados pelo usuário logado"""
    query = db.query(Product).filter(Product.user_id == current_user.id)
    
    if status_filter is not None:
        query = query.filter(Product.status == status_filter)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.post(
    "/upload-image",
    response_model=ProductImageUpload,
    status_code=http_status.HTTP_201_CREATED,
    summary="Upload de imagem de produto",
    description="""
    Faz upload de uma imagem para uso em produtos.
    
    **Formatos aceitos:** JPG, JPEG, PNG, WEBP
    **Tamanho máximo:** 5MB
    **Resolução máxima:** 1920x1080 (imagens maiores serão redimensionadas)
    
    **Requer:** API Key + Token JWT
    
    **Retorna:** URL da imagem carregada para usar no campo 'image' do produto
    """,
    responses={
        201: {
            "description": "Imagem carregada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "image_url": "/static/images/products/550e8400-e29b-41d4-a716-446655440000.jpg"
                    }
                }
            }
        },
        400: {"description": "Arquivo inválido ou formato não suportado"},
        413: {"description": "Arquivo muito grande"}
    }
)
async def upload_product_image(
    file: UploadFile = File(..., description="Arquivo de imagem"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Upload de imagem de produto"""
    image_path = await FileService.save_product_image(file)
    return {"image_url": f"/{image_path}"}


@router.get(
    "/images/{filename}",
    response_class=FileResponse,
    summary="Servir imagem de produto",
    description="""
    Serve arquivos de imagem dos produtos.
    
    **Uso interno:** Este endpoint é usado automaticamente quando uma imagem é carregada.
    """
)
async def serve_product_image(filename: str):
    """Serve imagens de produtos"""
    file_path = Path(f"static/images/products/{filename}")
    
    if not file_path.exists():
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return FileResponse(file_path)


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
            status_code=http_status.HTTP_404_NOT_FOUND,
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
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.put(
    "/{product_id}/image",
    response_model=ProductResponse,
    summary="Atualizar imagem do produto",
    description="""
    Atualiza apenas a imagem de um produto existente.
    
    A imagem anterior será substituída (se existir arquivo local).
    
    **Requer:** API Key + Token JWT
    """
)
async def update_product_image(
    product_id: int,
    image: UploadFile = File(..., description="Nova imagem do produto"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Atualiza imagem do produto"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Remover imagem anterior se for um arquivo local
    if db_product.image and db_product.image.startswith('/static/'):
        old_image_path = db_product.image.lstrip('/')
        FileService.delete_image(old_image_path)
    
    # Upload da nova imagem
    image_path = await FileService.save_product_image(image)
    db_product.image = f"/{image_path}"
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.delete(
    "/{product_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Deletar produto",
    description="""
    Desativa um produto (soft delete).
    
    O produto não é removido do banco, apenas marcado como inativo.
    A imagem associada não é removida para preservar histórico.
    
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
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db_product.status = False
    db.commit()
    
    return None


@router.delete(
    "/{product_id}/image",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Remover imagem do produto",
    description="""
    Remove a imagem de um produto específico.
    
    O arquivo de imagem será deletado do servidor se for um arquivo local.
    
    **Requer:** API Key + Token JWT
    """
)
async def delete_product_image(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Remove imagem do produto"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Remover arquivo de imagem se for local
    if db_product.image and db_product.image.startswith('/static/'):
        image_path = db_product.image.lstrip('/')
        FileService.delete_image(image_path)
    
    # Limpar campo de imagem no banco
    db_product.image = None
    db.commit()
    
    return None