from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from proraf.config import settings
from proraf.database import engine, Base
from proraf.routers import auth, products, batches, movements

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