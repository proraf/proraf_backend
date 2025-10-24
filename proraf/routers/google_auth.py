from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import secrets

from proraf.database import get_db
from proraf.oauth2_config import google_oauth2
from proraf.services.google_oauth_service import google_user_service
from proraf.schemas.user import Token, UserResponse

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

# Store para states temporários (em produção usar Redis)
oauth_states = {}


@router.get("/login")
async def google_login():
    """
    Inicia o fluxo de login do Google OAuth2.
    Retorna a URL para redirecionamento.
    """
    try:
        # Gerar URL de autorização
        authorization_url, state = google_oauth2.get_authorization_url()
        
        # Armazenar state para validação
        oauth_states[state] = True
        
        return {
            "authorization_url": authorization_url,
            "state": state
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao iniciar login Google: {str(e)}"
        )


@router.get("/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code do Google"),
    state: str = Query(..., description="State parameter para validação"),
    db: Session = Depends(get_db)
):
    """
    Processa o callback do Google OAuth2.
    Troca o código por tokens e cria/autentica usuário.
    """
    try:
        # Validar state
        if state not in oauth_states:
            raise HTTPException(
                status_code=400,
                detail="State inválido ou expirado"
            )
        
        # Remover state usado
        del oauth_states[state]
        
        # Trocar código por tokens
        credentials = google_oauth2.exchange_code_for_token(code, state)
        
        if not credentials.token:
            raise HTTPException(
                status_code=400,
                detail="Falha ao obter token de acesso"
            )
        
        # Obter informações do usuário
        user_info = google_user_service.get_user_info_from_token(credentials.token)
        
        # Criar ou obter usuário
        user = google_user_service.create_or_get_user(db, user_info)
        
        # Gerar JWT token
        access_token = google_user_service.generate_jwt_token(user)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no callback Google: {str(e)}"
        )


@router.post("/verify-token")
async def verify_google_token(
    token_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Verifica Google ID token diretamente (para SPAs).
    """
    try:
        id_token_str = token_data.get("id_token")
        
        if not id_token_str:
            raise HTTPException(
                status_code=400,
                detail="ID token é obrigatório"
            )
        
        # Carregar configuração Google
        client_config = google_oauth2.load_client_config()
        client_id = client_config["client_id"]
        
        # Verificar token
        idinfo = google_user_service.verify_google_token(id_token_str, client_id)
        
        # Preparar dados do usuário
        user_data = {
            "id": idinfo.get("sub"),
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture")
        }
        
        # Criar ou obter usuário
        user = google_user_service.create_or_get_user(db, user_data)
        
        # Gerar JWT token
        access_token = google_user_service.generate_jwt_token(user)
        
        # Criar resposta com tratamento de erro
        try:
            user_response = UserResponse.from_orm(user)
        except Exception as validation_error:
            # Se falhar na validação, tentar reparar dados
            raise HTTPException(
                status_code=500,
                detail=f"Erro na validação do usuário: {str(validation_error)}"
            )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na verificação do token: {str(e)}"
        )


@router.get("/user-info")
async def get_google_user_info(access_token: str):
    """
    Endpoint de teste para obter informações do usuário Google.
    """
    try:
        user_info = google_user_service.get_user_info_from_token(access_token)
        return user_info
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao obter informações: {str(e)}"
        )