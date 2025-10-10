import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from proraf.app import app
from proraf.database import Base, get_db
from proraf.config import settings

# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Cria sessão de banco de dados para testes"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Cliente de teste com banco de dados mockado"""
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def api_headers():
    """Headers com API Key para testes"""
    return {
        "X-API-Key": settings.api_key
    }


@pytest.fixture
def auth_headers(client, api_headers, db_session):
    """Headers com autenticação para testes"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    # Cria usuário de teste
    user = User(
        nome="Test User",
        email="test@example.com",
        senha=get_password_hash("testpass123"),
        tipo_pessoa="F",
        cpf="12345678901",
        tipo_perfil="user"
    )
    db_session.add(user)
    db_session.commit()
    
    # Faz login
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        },
        headers=api_headers
    )
    
    token = response.json()["access_token"]
    
    return {
        **api_headers,
        "Authorization": f"Bearer {token}"
    }