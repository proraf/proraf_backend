from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from proraf.config import settings
from proraf.database import engine, Base
from proraf.routers import auth, products, batches, movements, users, admin_dashboard, user_profile, traking, field_data, print_labels, whatsapp, public
import logging

logger = logging.getLogger(__name__)

# Cria tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST para Sistema de Rastreabilidade Agrícola ProRAF",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "ProRAF Team",
        "email": "suporte@proraf.com",
    },
    license_info={
        "name": "Unipampa"
    },
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para logar erros de validação"""
    body = await request.body()
    logger.error(f"Validation error on {request.url.path}")
    logger.error(f"Request body: {body.decode('utf-8', errors='ignore')}")
    logger.error(f"Validation errors: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


# Middleware para preservar HTTPS e /api nos redirects de trailing slash
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Se for um redirect (307, 308, 301, 302)
        if 300 <= response.status_code < 400:
            location = response.headers.get("location")
            if location:
                # Pega o scheme do header X-Forwarded-Proto (setado pelo Nginx)
                scheme = request.headers.get("x-forwarded-proto", "https")
                host = request.headers.get("host", "proraf.cloud")
                
                # Se o location é um path relativo (começa com /)
                if location.startswith("/"):
                    # Reconstrói a URL completa com HTTPS e /api
                    # O Nginx remove /api/ antes de enviar pro backend, então precisamos adicionar de volta
                    new_location = f"{scheme}://{host}/api{location}"
                    response.headers["location"] = new_location
                # Se é uma URL completa mas sem HTTPS ou sem /api
                elif "://" in location:
                    # Se tem http://, substitui por https://
                    if location.startswith("http://"):
                        location = location.replace("http://", "https://", 1)
                    
                    # Se não tem /api/ no path, adiciona
                    if "/api/" not in location and f"{host}/" in location:
                        location = location.replace(f"{host}/", f"{host}/api/", 1)
                    
                    response.headers["location"] = location
        
        return response

app.add_middleware(HTTPSRedirectMiddleware)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique apenas origins confiáveis
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Configurar arquivos estáticos
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Registra routers
app.include_router(traking.router)
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(user_profile.router)
app.include_router(products.router)
app.include_router(batches.router)
app.include_router(movements.router)
app.include_router(users.router)
app.include_router(admin_dashboard.router)
app.include_router(field_data.router)
app.include_router(print_labels.router)
app.include_router(whatsapp.router)
# Router Google OAuth
from proraf.routers import google_auth
app.include_router(google_auth.router)

# Debug router temporário removido após correção


@app.get("/", tags=["Health"], summary="Status da API", description="Verifica se a API está online e funcionando")
async def root():
    """Endpoint de verificação de saúde da API"""
    return {
        "status": "online",
        "app": settings.app_name,
        "version": settings.app_version,
        "message": "ProRAF API está funcionando corretamente"
    }


@app.get("/health", tags=["Health"], summary="Health Check", description="Endpoint de health check para monitoramento")
async def health_check():
    """Verifica saúde da aplicação"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }


def custom_openapi():
    """Customiza documentação OpenAPI/Swagger"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ProRAF - Sistema de Rastreabilidade Agrícola",
        version=settings.app_version,
        description="""
# ProRAF API - Rastreabilidade Agrícola

API REST completa para gerenciamento de rastreabilidade de produtos agrícolas.

## 🔐 Autenticação

Esta API utiliza **duas camadas de segurança**:

1. **API Key**: Todas as requisições devem incluir o header `X-API-Key`
2. **JWT Bearer Token**: Endpoints protegidos requerem autenticação via token JWT

### Como Autenticar no Swagger:

1. **Clique no botão "Authorize" 🔓 no topo da página**
2. Na seção **APIKeyHeader**, cole sua API Key do arquivo `.env`
3. Clique em "Authorize" e depois "Close"
4. Faça login em `/auth/login` para obter o token JWT
5. Clique novamente em "Authorize" 🔓
6. Na seção **BearerAuth**, cole o token JWT
7. Clique em "Authorize" e depois "Close"

### Exemplo de Headers:

```
X-API-Key: sua-api-key-aqui
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📋 Recursos Disponíveis

- **Autenticação**: Registro e login de usuários
- **Produtos**: Gerenciamento de produtos agrícolas
- **Lotes**: Rastreabilidade de lotes de produção com QR Code
- **Movimentações**: Controle de movimentações de lotes
- **Admin - Usuários**: Gerenciamento completo de usuários (apenas admin)
- **Admin - Dashboard**: Estatísticas e visão geral do sistema (apenas admin)

## 👤 Tipos de Usuário

- **user**: Usuário padrão (acesso aos próprios recursos)
- **admin**: Administrador (acesso completo ao sistema)

## 📱 Tipos de Pessoa

- **F**: Pessoa Física (requer CPF)
- **J**: Pessoa Jurídica (requer CNPJ)

## 🔄 Fluxo de Trabalho

1. Registrar usuário → `/auth/register`
2. Fazer login → `/auth/login`
3. Criar produtos → `/products/`
4. Criar lotes → `/batches/` (QR Code gerado automaticamente)
5. Registrar movimentações → `/movements/`
6. Rastrear via QR Code

## 📞 Suporte

Para suporte técnico, entre em contato: suporte@proraf.com
        """,
        routes=app.routes,
        contact={
            "name": "ProRAF Support Team",
            "url": "https://proraf.com",
            "email": "suporte@proraf.com",
        },
        license_info={
            "name": "Unipampa"
        },
    )
    
    # Adiciona informações de segurança CORRETAS
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "🔑 API Key para autenticação básica. Configure no arquivo .env"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "🎫 Token JWT obtido após login via /auth/login"
        }
    }
    
    # Define segurança global (ambos são necessários)
    openapi_schema["security"] = [
        {
            "APIKeyHeader": [],
            "BearerAuth": []
        }
    ]
    
    # Adiciona exemplos de servidor
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "🔧 Servidor de Desenvolvimento Local"
        },
        {
            "url": "http://127.0.0.1:8000",
            "description": "🔧 Servidor de Desenvolvimento (127.0.0.1)"
        },
        {
            "url": "https://api.proraf.com",
            "description": "🚀 Servidor de Produção"
        }
    ]
    
    # Adiciona tags com descrições detalhadas
    openapi_schema["tags"] = [
        {
            "name": "Health",
            "description": "🏥 Endpoints de verificação de saúde da API. Não requerem autenticação."
        },
        {
            "name": "Autenticação",
            "description": "🔐 Registro, login e gerenciamento de tokens JWT. Requer apenas API Key."
        },
        {
            "name": "Produtos",
            "description": "🌱 CRUD de produtos agrícolas (tomate, alface, etc.). Requer API Key + JWT."
        },
        {
            "name": "Lotes",
            "description": "📦 Gerenciamento de lotes de produção com rastreabilidade e QR Code automático. Requer API Key + JWT."
        },
        {
            "name": "Movimentações",
            "description": "📊 Controle de movimentações de lotes (plantio, colheita, expedição, venda). Requer API Key + JWT."
        },
        {
            "name": "Admin - Usuários",
            "description": "👥 Gerenciamento completo de usuários. **APENAS ADMINISTRADORES**. Requer API Key + JWT + Perfil Admin."
        },
        {
            "name": "Admin - Dashboard",
            "description": "📈 Dashboard com estatísticas e visão geral do sistema. **APENAS ADMINISTRADORES**. Requer API Key + JWT + Perfil Admin."
        },
        {
            "name": "WhatsApp Integration",
            "description": "💬 Integração com API do WhatsApp. Autenticação via telefone + hash compartilhado (sem login tradicional). Permite criar produtos e verificar usuários diretamente via WhatsApp."
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi