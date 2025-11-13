from datetime import datetime, timedelta
from typing import Optional
import hashlib
import hmac
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from proraf.config import settings
from proraf.database import get_db
from proraf.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT de acesso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """Verifica API Key para comunicação com o frontend"""
    if api_key is None or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
    return True


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_api_key)
) -> User:
    """Obtém usuário atual através do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verifica se usuário está ativo"""
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Requer que usuário seja administrador"""
    if current_user.tipo_perfil != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def generate_whatsapp_hash(telefone: str) -> str:
    """
    Gera hash HMAC-SHA256 para autenticação via WhatsApp
    Usa SECRET_KEY como chave compartilhada entre as aplicações
    
    Args:
        telefone: Número de telefone do usuário
        
    Returns:
        Hash hexadecimal para validação
    """
    message = f"{telefone}:{settings.secret_key}"
    hash_object = hmac.new(
        settings.secret_key.encode('utf-8'),
        telefone.encode('utf-8'),
        hashlib.sha256
    )
    return hash_object.hexdigest()


def verify_whatsapp_hash(telefone: str, provided_hash: str) -> bool:
    """
    Verifica se o hash fornecido é válido para o telefone
    
    Args:
        telefone: Número de telefone
        provided_hash: Hash recebido da aplicação WhatsApp
        
    Returns:
        True se o hash é válido, False caso contrário
    """
    expected_hash = generate_whatsapp_hash(telefone)
    return hmac.compare_digest(expected_hash, provided_hash)


async def get_user_by_phone_with_hash(
    telefone: str,
    hash: str,
    db: Session
) -> User:
    """
    Obtém usuário através do telefone e valida o hash compartilhado
    Substitui autenticação tradicional para integração WhatsApp
    
    Args:
        telefone: Número de telefone do usuário
        hash: Hash compartilhado para autenticação
        db: Sessão do banco de dados
        
    Returns:
        Objeto User se autenticação válida
        
    Raises:
        HTTPException: Se telefone não existe ou hash inválido
    """
    # Verifica hash primeiro
    if not verify_whatsapp_hash(telefone, hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication hash"
        )
    
    # Busca usuário pelo telefone
    user = db.query(User).filter(User.telefone == telefone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not registered in the system"
        )
    
    return user