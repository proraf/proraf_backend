import requests
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from proraf.models.user import User
from proraf.schemas.user import GoogleUserCreate
from proraf.security import create_access_token


class GoogleUserService:
    """Serviço para gerenciar usuários OAuth do Google"""
    
    @staticmethod
    def get_user_info_from_token(access_token: str) -> Dict[str, Any]:
        """Obtém informações do usuário do Google usando access token"""
        try:
            # Fazer request para Google People API
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erro ao obter dados do usuário: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Falha ao acessar Google API: {e}")
    
    @staticmethod
    def verify_google_token(id_token_str: str, client_id: str) -> Dict[str, Any]:
        """Verifica e decodifica Google ID token"""
        try:
            # Verificar o ID token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                client_id
            )
            
            # Verificar se é do nosso app
            if idinfo.get('aud') != client_id:
                raise ValueError('Token inválido')
                
            return idinfo
            
        except ValueError as e:
            raise Exception(f"Token inválido: {e}")
    
    @staticmethod
    def create_or_get_user(db: Session, google_user_data: Dict[str, Any]) -> User:
        """Cria ou obtém usuário baseado nos dados do Google"""
        
        google_id = google_user_data.get("id")
        email = google_user_data.get("email")
        name = google_user_data.get("name", "")
        picture = google_user_data.get("picture")
        
        if not google_id or not email:
            raise Exception("Dados insuficientes do Google")
        
        # Tentar encontrar usuário por google_id
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if user:
            # Usuário já existe, atualizar dados se necessário
            if user.avatar_url != picture:
                user.avatar_url = picture
                db.commit()
            return user
        
        # Verificar se usuário já existe com mesmo email (conta local)
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Linkar conta Google à conta existente
            existing_user.google_id = google_id
            existing_user.avatar_url = picture
            existing_user.provider = "google"
            db.commit()
            return existing_user
        
        # Criar novo usuário Google com dados válidos
        new_user = User(
            nome=name or "Usuário Google",  # Nome padrão se vazio
            email=email,
            senha=None,  # NULL - agora permitido após migração
            tipo_pessoa="F",  # Default pessoa física
            cpf=None,  # NULL - validação flexível para OAuth
            cnpj=None,
            telefone=None,
            google_id=google_id,
            avatar_url=picture,
            provider="google",
            tipo_perfil="user"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def generate_jwt_token(user: User) -> str:
        """Gera JWT token para usuário autenticado"""
        return create_access_token(data={"sub": user.email})


# Instância do serviço
google_user_service = GoogleUserService()