from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.user import User
from proraf.schemas.user import Token, UserCreate, UserResponse
from proraf.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_api_key
)
from proraf.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
    responses={
        401: {"description": "Não autorizado"},
        403: {"description": "API Key inválida ou ausente"},
    }
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="""
    Registra um novo usuário no sistema.
    
    **Tipos de Pessoa:**
    - **F**: Pessoa Física (requer CPF)
    - **J**: Pessoa Jurídica (requer CNPJ)
    
    **Perfis:**
    - **user**: Usuário padrão (valor padrão)
    - **admin**: Administrador do sistema
    
    **Requer:** API Key no header `X-API-Key`
    """,
    responses={
        201: {
            "description": "Usuário criado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nome": "João Silva",
                        "email": "joao@farm.com",
                        "tipo_pessoa": "F",
                        "cpf": "12345678901",
                        "tipo_perfil": "user",
                        "created_at": "2025-01-15T10:00:00"
                    }
                }
            }
        },
        400: {"description": "Email já cadastrado"}
    }
)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Registra novo usuário"""
    # Verifica se email já existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Cria novo usuário
    hashed_password = get_password_hash(user.senha)
    db_user = User(
        nome=user.nome,
        email=user.email,
        senha=hashed_password,
        tipo_pessoa=user.tipo_pessoa,
        cpf=user.cpf,
        cnpj=user.cnpj,
        telefone=user.telefone,
        tipo_perfil=user.tipo_perfil
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post(
    "/login",
    response_model=Token,
    summary="Fazer login",
    description="""
    Autentica usuário e retorna token JWT.
    
    **Credenciais:**
    - **username**: Email do usuário
    - **password**: Senha do usuário
    
    **Requer:** API Key no header `X-API-Key`
    
    **Retorna:** Token JWT que deve ser usado em requisições subsequentes
    """,
    responses={
        200: {
            "description": "Login realizado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {"description": "Credenciais inválidas"}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Autentica usuário e retorna token JWT"""
    # Busca usuário
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cria token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}