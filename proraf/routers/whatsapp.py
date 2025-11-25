from typing import List
import secrets
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.user import User
from proraf.models.product import Product
from proraf.models.batch import Batch
from proraf.schemas.whatsapp import (
    WhatsAppAuth,
    PhoneVerification,
    PhoneResponse,
    WhatsAppProductCreate,
    WhatsAppProductResponse,
    WhatsAppProductUpdate,
    WhatsAppBatchCreate,
    WhatsAppBatchResponse,
    ProductListItem,
    WhatsAppProductListResponse
)
from proraf.security import (
    verify_whatsapp_hash,
    get_user_by_phone_with_hash,
    generate_whatsapp_hash
)
from proraf.services.qrcode_service import generate_qrcode

router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp Integration"],
    responses={
        401: {"description": "Invalid authentication hash"},
        404: {"description": "Phone number not found"}
    }
)


@router.get(
    "/phones",
    response_model=List[str],
    summary="[WhatsApp] Listar telefones cadastrados",
    description="""
    Retorna lista de todos os números de telefone cadastrados no sistema.
    
    **Uso:** API do WhatsApp pode verificar se um usuário já possui conta
    antes de iniciar interações.
    
    **Autenticação:** Requer hash válido gerado com SECRET_KEY compartilhada.
    
    **Segurança:** Apenas números de telefone são retornados, sem dados sensíveis.
    """
)
async def list_registered_phones(
    hash: str,
    db: Session = Depends(get_db)
):
    """
    Lista todos os números de telefone cadastrados no sistema.
    Usado pela API do WhatsApp para verificar usuários existentes.
    """
    # Valida hash usando um valor fixo conhecido pelas duas aplicações
    # Para esta rota específica, usamos "PHONE_LIST" como identificador
    if not verify_whatsapp_hash("PHONE_LIST", hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication hash for phone list access"
        )
    
    # Retorna apenas telefones não-nulos
    users = db.query(User.telefone).filter(User.telefone.isnot(None)).all()
    phone_list = [user[0] for user in users]
    
    return phone_list


@router.post(
    "/verify-phone",
    response_model=PhoneResponse,
    summary="[WhatsApp] Verificar se telefone existe",
    description="""
    Verifica se um número de telefone está cadastrado no sistema.
    
    **Retorna:**
    - exists: true/false
    - Se existe: dados básicos do usuário (id, nome, email, tipo_pessoa)
    
    **Autenticação:** Hash HMAC-SHA256(telefone, SECRET_KEY)
    """
)
async def verify_phone(
    verification: PhoneVerification,
    db: Session = Depends(get_db)
):
    """
    Verifica se telefone existe e retorna dados básicos do usuário
    """
    # Valida hash
    if not verify_whatsapp_hash(verification.telefone, verification.hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication hash"
        )
    
    # Busca usuário
    user = db.query(User).filter(User.telefone == verification.telefone).first()
    
    if not user:
        return PhoneResponse(exists=False)
    
    return PhoneResponse(
        exists=True,
        user_id=user.id,
        nome=user.nome,
        email=user.email,
        tipo_pessoa=user.tipo_pessoa
    )


@router.post(
    "/list-products",
    response_model=WhatsAppProductListResponse,
    summary="[WhatsApp] Listar produtos do usuário",
    description="""
    Retorna lista completa de todos os produtos cadastrados pelo usuário.
    
    **Autenticação:** Número de telefone + hash compartilhado
    
    **Retorna:**
    - Total de produtos cadastrados
    - Quantidade de produtos ativos e inativos
    - Lista detalhada com todos os produtos
    - Quantidade de lotes por produto
    
    **Exemplo de uso:**
    Usuário com telefone "55996852212" envia mensagem:
    "Meus produtos" ou "Listar produtos"
    
    A API do WhatsApp processa e chama este endpoint.
    Bot retorna lista formatada com todos os produtos do usuário.
    
    **Casos de uso:**
    - Consultar produtos antes de criar lote
    - Verificar status dos produtos
    - Obter ID do produto para outras operações
    - Visualizar variedades cadastradas
    """
)
async def list_user_products(
    auth: WhatsAppAuth,
    db: Session = Depends(get_db)
):
    """
    Lista todos os produtos do usuário autenticado via telefone e hash
    """
    # Autentica usuário via telefone + hash
    user = await get_user_by_phone_with_hash(
        auth.telefone,
        auth.hash,
        db
    )
    
    # Busca todos os produtos do usuário
    products = db.query(Product).filter(Product.user_id == user.id).all()
    
    if not products:
        return WhatsAppProductListResponse(
            success=True,
            message="Você ainda não possui produtos cadastrados",
            total_products=0,
            active_products=0,
            inactive_products=0,
            products=[]
        )
    
    # Prepara lista de produtos com contagem de lotes
    product_list = []
    active_count = 0
    inactive_count = 0
    
    for product in products:
        # Conta lotes do produto
        batches_count = db.query(Batch).filter(Batch.product_id == product.id).count()
        
        # Conta produtos ativos/inativos
        if product.status:
            active_count += 1
        else:
            inactive_count += 1
        
        product_list.append(ProductListItem(
            id=product.id,
            name=product.name,
            comertial_name=product.comertial_name,
            description=product.description,
            variedade_cultivar=product.variedade_cultivar,
            status=product.status,
            code=product.code,
            batches_count=batches_count
        ))
    
    # Ordena produtos por nome
    product_list.sort(key=lambda x: x.name.lower())
    
    return WhatsAppProductListResponse(
        success=True,
        message=f"Você possui {len(products)} produto(s) cadastrado(s)",
        total_products=len(products),
        active_products=active_count,
        inactive_products=inactive_count,
        products=product_list
    )


@router.post(
    "/create-product",
    response_model=WhatsAppProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[WhatsApp] Criar produto via telefone",
    description="""
    Permite criar um novo produto diretamente via WhatsApp.
    
    **Autenticação:** Número de telefone + hash compartilhado (sem login tradicional)
    
    **Exemplo de uso:**
    Usuário com telefone "55996852212" envia mensagem no WhatsApp:
    "Registrar produto: laranja"
    
    A API do WhatsApp processa e chama este endpoint com:
    - telefone: "55996852212"
    - hash: HMAC-SHA256("55996852212", SECRET_KEY)
    - name: "laranja"
    
    **Retorna:** Dados do produto criado incluindo QR Code
    """
)
async def create_product_via_whatsapp(
    product_data: WhatsAppProductCreate,
    db: Session = Depends(get_db)
):
    """
    Cria produto para usuário autenticado via telefone e hash compartilhado
    """
    # Autentica usuário via telefone + hash
    user = await get_user_by_phone_with_hash(
        product_data.telefone,
        product_data.hash,
        db
    )
    
    # Verifica se produto com mesmo nome já existe para este usuário
    existing_product = db.query(Product).filter(
        Product.user_id == user.id,
        Product.name == product_data.name
    ).first()
    
    if existing_product:
        return WhatsAppProductResponse(
            success=False,
            message=f"Product '{product_data.name}' already exists in your account",
            product_id=existing_product.id,
            product_name=existing_product.name
        )
    
    # Gera código único para o produto
    code = secrets.token_urlsafe(8)
    while db.query(Product).filter(Product.code == code).first():
        code = secrets.token_urlsafe(8)
    
    # Cria novo produto
    new_product = Product(
        name=product_data.name,
        comertial_name=product_data.name,  # Usa o mesmo nome como comercial
        description=product_data.description,
        variedade_cultivar=product_data.variedade_cultivar,
        status=True,  # Boolean: True = ativo, False = inativo
        code=code,
        user_id=user.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Gera QR Code para o produto
    qrcode_data = f"product:{new_product.id}"
    qrcode_id = generate_qrcode(qrcode_data)
    qrcode_url = f"/qrcode/{qrcode_id}"
    
    return WhatsAppProductResponse(
        success=True,
        message=f"Product '{new_product.name}' created successfully via WhatsApp",
        product_id=new_product.id,
        product_name=new_product.name,
        qrcode_url=qrcode_url
    )


@router.get(
    "/generate-hash/{telefone}",
    summary="[DEV] Gerar hash para telefone",
    description="""
    **ROTA DE DESENVOLVIMENTO**
    
    Gera o hash de autenticação para um telefone específico.
    Útil para testar a integração e gerar hashes válidos.
    
    **Em produção:** Esta rota deve ser removida ou protegida!
    """
)
async def generate_hash_for_phone(telefone: str):
    """
    Gera hash de autenticação para um telefone
    ATENÇÃO: Esta é uma rota auxiliar para desenvolvimento
    """
    hash_value = generate_whatsapp_hash(telefone)
    return {
        "telefone": telefone,
        "hash": hash_value,
        "info": "Use este hash nas requisições WhatsApp para autenticação"
    }


@router.get(
    "/list-hash",
    summary="[DEV] Gerar hash para listar telefones",
    description="""
    **ROTA DE DESENVOLVIMENTO**
    
    Gera o hash necessário para acessar a lista de telefones cadastrados.
    """
)
async def generate_list_hash():
    """
    Gera hash para acessar lista de telefones
    """
    hash_value = generate_whatsapp_hash("PHONE_LIST")
    return {
        "identifier": "PHONE_LIST",
        "hash": hash_value,
        "usage": "Use este hash no parâmetro ?hash= da rota GET /whatsapp/phones"
    }


@router.put(
    "/update-product",
    response_model=WhatsAppProductResponse,
    summary="[WhatsApp] Editar produto via telefone",
    description="""
    Permite editar um produto existente diretamente via WhatsApp.
    
    **Autenticação:** Número de telefone + hash compartilhado
    
    **Validações:**
    - Verifica se o produto existe
    - Verifica se o produto pertence ao usuário autenticado
    - Atualiza apenas os campos fornecidos (partial update)
    
    **Exemplo de uso:**
    Usuário com telefone "55996852212" envia mensagem:
    "Editar produto 5: descrição 'laranjas orgânicas', variedade 'Pera Rio'"
    
    A API do WhatsApp processa e chama este endpoint com os dados fornecidos.
    """
)
async def update_product_via_whatsapp(
    product_data: WhatsAppProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Edita produto para usuário autenticado via telefone e hash compartilhado
    """
    # Autentica usuário via telefone + hash
    user = await get_user_by_phone_with_hash(
        product_data.telefone,
        product_data.hash,
        db
    )
    
    # Busca o produto
    product = db.query(Product).filter(Product.id == product_data.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_data.product_id} not found"
        )
    
    # Verifica se o produto pertence ao usuário
    if product.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this product"
        )
    
    # Atualiza apenas os campos fornecidos
    update_data = product_data.model_dump(exclude_unset=True, exclude={"telefone", "hash", "product_id"})
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return WhatsAppProductResponse(
        success=True,
        message=f"Product '{product.name}' updated successfully via WhatsApp",
        product_id=product.id,
        product_name=product.name
    )


@router.post(
    "/create-batch",
    response_model=WhatsAppBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[WhatsApp] Criar lote via telefone",
    description="""
    Permite criar um novo lote para um produto via WhatsApp.
    
    **Autenticação:** Número de telefone + hash compartilhado
    
    **Validações:**
    - Verifica se o produto existe
    - Verifica se o produto pertence ao usuário autenticado
    - Gera código único automaticamente
    - Gera QR Code para rastreabilidade
    
    **Exemplo de uso:**
    Usuário com telefone "55996852212" envia mensagem:
    "Criar lote para produto 5: talhão A1, plantio 2025-01-15, colheita 2025-04-20, produção 500 kg"
    
    A API do WhatsApp processa e chama este endpoint com:
    - telefone: "55996852212"
    - hash: HMAC-SHA256("55996852212", SECRET_KEY)
    - product_id: 5
    - talhao: "A1"
    - dt_plantio: "2025-01-15"
    - dt_colheita: "2025-04-20"
    - producao: 500
    - unidadeMedida: "kg"
    
    **Retorna:** Dados do lote criado incluindo código e QR Code
    """
)
async def create_batch_via_whatsapp(
    batch_data: WhatsAppBatchCreate,
    db: Session = Depends(get_db)
):
    """
    Cria lote para usuário autenticado via telefone e hash compartilhado
    """
    # Autentica usuário via telefone + hash
    user = await get_user_by_phone_with_hash(
        batch_data.telefone,
        batch_data.hash,
        db
    )
    
    # Busca o produto
    product = db.query(Product).filter(Product.id == batch_data.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {batch_data.product_id} not found"
        )
    
    # Verifica se o produto pertence ao usuário
    if product.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create batches for this product"
        )
    
    # Gera código único para o lote (formato: LOTE-PRODUTO-RANDOM)
    code_prefix = f"LOTE-{product.code}-"
    code = code_prefix + secrets.token_urlsafe(6)
    
    # Garante que o código é único
    while db.query(Batch).filter(Batch.code == code).first():
        code = code_prefix + secrets.token_urlsafe(6)
    
    # Converte strings de data para objetos date, se fornecidas
    dt_plantio = None
    dt_colheita = None
    
    if batch_data.dt_plantio:
        try:
            dt_plantio = datetime.strptime(batch_data.dt_plantio, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid dt_plantio format. Use YYYY-MM-DD"
            )
    
    if batch_data.dt_colheita:
        try:
            dt_colheita = datetime.strptime(batch_data.dt_colheita, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid dt_colheita format. Use YYYY-MM-DD"
            )
    
    # Cria novo lote
    new_batch = Batch(
        code=code,
        talhao=batch_data.talhao,
        dt_plantio=dt_plantio,
        dt_colheita=dt_colheita,
        producao=batch_data.producao or 0,
        unidadeMedida=batch_data.unidadeMedida,
        status=True,
        product_id=product.id,
        user_id=user.id
    )
    
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    
    # Gera QR Code para o lote
    qrcode_data = f"batch:{new_batch.id}"
    qrcode_id = generate_qrcode(qrcode_data)
    qrcode_url = f"/qrcode/{qrcode_id}"
    
    # Salva o QR Code no lote
    new_batch.qrcode = qrcode_url
    db.commit()
    
    return WhatsAppBatchResponse(
        success=True,
        message=f"Batch '{new_batch.code}' created successfully for product '{product.name}'",
        batch_id=new_batch.id,
        batch_code=new_batch.code,
        product_name=product.name,
        qrcode_url=qrcode_url
    )
