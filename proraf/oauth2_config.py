import os
import json
from typing import Dict, Any
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

class GoogleOAuth2Config:
    """Configuração para Google OAuth2"""
    
    def __init__(self):
        self.client_secrets_file = "client_secret.json"
        self.scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        self.redirect_uri = "http://localhost:8000/auth/google/callback"
        
    def load_client_config(self) -> Dict[str, Any]:
        """Carrega configuração do cliente Google"""
        try:
            with open(self.client_secrets_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config['web']
        except Exception as e:
            raise Exception(f"Erro ao carregar client_secret.json: {e}")
    
    def create_flow(self) -> Flow:
        """Cria fluxo OAuth2 do Google"""
        client_config = self.load_client_config()
        
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": client_config["client_id"],
                    "client_secret": client_config["client_secret"],
                    "auth_uri": client_config["auth_uri"],
                    "token_uri": client_config["token_uri"],
                    "auth_provider_x509_cert_url": client_config["auth_provider_x509_cert_url"],
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        
        flow.redirect_uri = self.redirect_uri
        return flow
    
    def get_authorization_url(self) -> tuple[str, str]:
        """Gera URL de autorização e state"""
        flow = self.create_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state
    
    def exchange_code_for_token(self, authorization_code: str, state: str) -> Credentials:
        """Troca código de autorização por tokens"""
        flow = self.create_flow()
        flow.fetch_token(code=authorization_code)
        return flow.credentials

# Instância global
google_oauth2 = GoogleOAuth2Config()