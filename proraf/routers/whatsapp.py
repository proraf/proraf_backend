from typing import List
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.user import User
from proraf.models.product import Product
from proraf.schemas.whatsapp import (
    WhatsAppAuth,
    PhoneVerification,
    PhoneResponse,
    WhatsAppProductCreate,
    WhatsAppProductResponse
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
