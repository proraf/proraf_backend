from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from proraf.database import get_db
from proraf.models.user import User
from proraf.schemas.user import UserCreate, UserUpdate, UserResponse
from proraf.security import (
    get_current_active_user,
    require_admin,
    verify_api_key,
    get_password_hash
)

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Usuários"],
    responses={
        401: {"description": "Não autorizado - Token inválido"},
        403: {"description": "Acesso negado - Requer permissão de administrador"},
        404: {"description": "Usuário não encontrado"}
    }
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[ADMIN] Criar usuário",
    description="""
    Cria um novo usuário no sistema (apenas administradores).
    
    **Diferente do registro público:**
    - Permite definir tipo_perfil como 'admin'
    - Permite criar usuários para outros
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Cria novo usuário (apenas admin)"""
    # Verifica se email já existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Cria usuário
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


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="[ADMIN] Listar todos usuários",
    description="""
    Lista todos os usuários cadastrados no sistema.
    
    **Filtros disponíveis:**
    - tipo_perfil: Filtrar por perfil (user, admin)
    - tipo_pessoa: Filtrar por tipo (F, J)
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def list_users(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros"),
    tipo_perfil: str = Query(None, description="Filtrar por perfil (user/admin)"),
    tipo_pessoa: str = Query(None, description="Filtrar por tipo (F/J)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Lista todos usuários (apenas admin)"""
    query = db.query(User)
    
    if tipo_perfil:
        query = query.filter(User.tipo_perfil == tipo_perfil)
    
    if tipo_pessoa:
        query = query.filter(User.tipo_pessoa == tipo_pessoa)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="[ADMIN] Buscar usuário por ID",
    description="""
    Retorna detalhes de um usuário específico.
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Obtém usuário por ID (apenas admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get(
    "/email/{email}",
    response_model=UserResponse,
    summary="[ADMIN] Buscar usuário por email",
    description="""
    Retorna detalhes de um usuário pelo email.
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Obtém usuário por email (apenas admin)"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="[ADMIN] Atualizar usuário",
    description="""
    Atualiza dados de um usuário.
    
    **Permite atualizar:**
    - Nome, telefone, senha
    - Tipo de perfil (promover/rebaixar admin)
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Atualiza usuário (apenas admin)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Se senha foi enviada, fazer hash
    if "senha" in update_data:
        update_data["senha"] = get_password_hash(update_data["senha"])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[ADMIN] Deletar usuário",
    description="""
    Remove um usuário do sistema permanentemente.
    
    **ATENÇÃO:** Esta é uma operação irreversível!
    
    **Não é possível:**
    - Deletar o próprio usuário administrador
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Deleta usuário (apenas admin)"""
    # Impede admin deletar a si mesmo
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(db_user)
    db.commit()
    
    return None


@router.patch(
    "/{user_id}/promote",
    response_model=UserResponse,
    summary="[ADMIN] Promover usuário a admin",
    description="""
    Promove um usuário comum a administrador.
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def promote_to_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Promove usuário a administrador"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if db_user.tipo_perfil == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an admin"
        )
    
    db_user.tipo_perfil = "admin"
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.patch(
    "/{user_id}/demote",
    response_model=UserResponse,
    summary="[ADMIN] Rebaixar admin a usuário",
    description="""
    Rebaixa um administrador a usuário comum.
    
    **Não é possível:**
    - Rebaixar o próprio usuário
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def demote_from_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Rebaixa administrador a usuário comum"""
    # Impede admin rebaixar a si mesmo
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if db_user.tipo_perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )
    
    db_user.tipo_perfil = "user"
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get(
    "/stats/overview",
    summary="[ADMIN] Estatísticas de usuários",
    description="""
    Retorna estatísticas gerais sobre usuários do sistema.
    
    **Informações incluídas:**
    - Total de usuários
    - Total de administradores
    - Total por tipo de pessoa (F/J)
    
    **Requer:** API Key + Token JWT + Perfil Admin
    """
)
async def get_users_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    api_key_valid: bool = Depends(verify_api_key)
):
    """Retorna estatísticas de usuários"""
    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.tipo_perfil == "admin").count()
    total_regular = db.query(User).filter(User.tipo_perfil == "user").count()
    total_pf = db.query(User).filter(User.tipo_pessoa == "F").count()
    total_pj = db.query(User).filter(User.tipo_pessoa == "J").count()
    
    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_regular_users": total_regular,
        "total_pessoa_fisica": total_pf,
        "total_pessoa_juridica": total_pj
    }