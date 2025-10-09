import pytest
from fastapi import status


def test_register_user(client, api_headers):
    """Testa registro de novo usuário"""
    response = client.post(
        "/auth/register",
        json={
            "nome": "João Silva",
            "email": "joao@example.com",
            "senha": "senha123",
            "tipo_pessoa": "F",
            "cpf": "12345678901",
            "telefone": "51999999999"
        },
        headers=api_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "joao@example.com"
    assert data["nome"] == "João Silva"
    assert "senha" not in data


def test_register_duplicate_email(client, api_headers, db_session):
    """Testa registro com email duplicado"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    # Cria usuário existente
    user = User(
        nome="Existing User",
        email="existing@example.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="98765432100"
    )
    db_session.add(user)
    db_session.commit()
    
    # Tenta registrar com mesmo email
    response = client.post(
        "/auth/register",
        json={
            "nome": "New User",
            "email": "existing@example.com",
            "senha": "newpass123",
            "tipo_pessoa": "J",
            "cnpj": "12345678000190"
        },
        headers=api_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"]


def test_login_success(client, api_headers, db_session):
    """Testa login com credenciais válidas"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    # Cria usuário
    user = User(
        nome="Test User",
        email="test@example.com",
        senha=get_password_hash("testpass123"),
        tipo_pessoa="F",
        cpf="12345678901"
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
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, api_headers):
    """Testa login com credenciais inválidas"""
    response = client.post(
        "/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpass"
        },
        headers=api_headers
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_without_api_key(client):
    """Testa registro sem API Key"""
    response = client.post(
        "/auth/register",
        json={
            "nome": "Test User",
            "email": "test@example.com",
            "senha": "pass123",
            "tipo_pessoa": "F",
            "cpf": "12345678901"
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN