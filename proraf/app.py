from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from proraf.config import settings
from proraf.database import engine, Base
from proraf.routers import auth, products, batches, movements, users, admin_dashboard

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
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(batches.router)
app.include_router(movements.router)
app.include_router(users.router)
app.include_router(admin_dashboard.router)


@app.get("/", tags=["Health"])
async def root():
    """Endpoint de verificação de saúde da API"""
    return {
        "status": "online",
        "app": settings.app_name,
        "version": settings.app_version
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica saúde da aplicação"""
    return {
        "status": "healthy",
        "database": "connected"
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

### Como Autenticar:

1. **Obter API Key**: Configure a variável `API_KEY` no arquivo `.env`
2. **Registrar/Login**: Use os endpoints `/auth/register` ou `/auth/login`
3. **Usar Token**: Inclua o token no header `Authorization: Bearer {token}`

### Exemplo de Headers:

```
X-API-Key: sua-api-key-aqui
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📋 Recursos Disponíveis

- **Autenticação**: Registro e login de usuários
- **Produtos**: Gerenciamento de produtos agrícolas
- **Lotes**: Rastreabilidade de lotes de produção
- **Movimentações**: Controle de movimentações de lotes
- **Dados de Campo**: Informações geográficas e de campo

## 👤 Tipos de Usuário

- **user**: Usuário padrão (acesso aos próprios recursos)
- **admin**: Administrador (acesso completo)

## 📱 Tipos de Pessoa

- **F**: Pessoa Física (requer CPF)
- **J**: Pessoa Jurídica (requer CNPJ)

## 🔄 Fluxo de Trabalho

1. Registrar usuário → `/auth/register`
2. Fazer login → `/auth/login`
3. Criar produtos → `/products/`
4. Criar lotes → `/batches/`
5. Registrar movimentações → `/movements/`
6. Rastrear via QR Code gerado automaticamente

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
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    
    # Adiciona informações de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key para autenticação básica. Obtenha sua chave nas configurações."
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtido após login. Use: `Authorization: Bearer {token}`"
        }
    }
    
    # Adiciona exemplos de servidor
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Servidor de Desenvolvimento"
        },
        {
            "url": "https://api.proraf.com",
            "description": "Servidor de Produção"
        }
    ]
    
    # Adiciona tags com descrições
    openapi_schema["tags"] = [
        {
            "name": "Health",
            "description": "Endpoints de verificação de saúde da API"
        },
        {
            "name": "Autenticação",
            "description": "Registro, login e gerenciamento de tokens JWT"
        },
        {
            "name": "Produtos",
            "description": "CRUD de produtos agrícolas (tomate, alface, etc.)"
        },
        {
            "name": "Lotes",
            "description": "Gerenciamento de lotes de produção com rastreabilidade e QR Code"
        },
        {
            "name": "Movimentações",
            "description": "Controle de movimentações de lotes (plantio, colheita, expedição)"
        },
        {
            "name": "Dados de Campo",
            "description": "Informações geográficas, mapas e imagens de campo"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi