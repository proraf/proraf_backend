import pytest
from fastapi import status


def test_get_current_user(client, auth_headers, db_session):
    """Testa obtenção de dados do usuário logado"""
    response = client.get("/user/me", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["nome"] == "Test User"
    assert "senha" not in data


def test_update_current_user(client, auth_headers):
    """Testa atualização de dados do usuário logado"""
    response = client.put(
        "/user/me",
        json={
            "nome": "Nome Atualizado",
            "telefone": "51999999999"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nome"] == "Nome Atualizado"
    assert data["telefone"] == "51999999999"
    
def test_update_user_tipo(client, auth_headers):
    """Testa atualização do tipo de pessoa do usuário"""
    response = client.put(
        "/user/me",
        json={
            "tipo_perfil": "Blockchain"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["tipo_perfil"] == "Blockchain"
    
    
def test_update_user_cpf(client, auth_headers):
    """Testa atualização do CPF do usuário"""
    response = client.put(
        "/user/me/cpfouCnpj",
        json={
            "cpfouCnpj": "12345678901",
            "tipoPessoa": "F"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cpf"] == "12345678901"


def test_update_user_password(client, auth_headers, api_headers, db_session):
    """Testa atualização de senha"""
    # Atualiza senha
    response = client.put(
        "/user/me",
        json={"senha": "novasenha123"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    # Testa login com nova senha
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "novasenha123"},
        headers=api_headers
    )
    
    assert response.status_code == status.HTTP_200_OK


def test_get_user_stats(client, auth_headers, db_session):
    """Testa estatísticas do usuário"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    # Cria dados de teste
    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1, producao=1000)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    movement = Movement(
        tipo_movimentacao="plantio",
        quantidade=500,
        batch_id=batch.id,
        user_id=1
    )
    db_session.add(movement)
    db_session.commit()
    
    response = client.get("/user/me/stats", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "batches" in data
    assert "movements" in data
    assert "production" in data
    assert "products" in data
    
    assert data["batches"]["total"] >= 1
    assert data["movements"]["total"] >= 1
    assert data["production"]["total"] >= 1000


def test_get_user_batches(client, auth_headers, db_session):
    """Testa listagem de lotes do usuário"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch

    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batches = [
        Batch(code="LOTE-1", product_id=product.id, user_id=1),
        Batch(code="LOTE-2", product_id=product.id, user_id=1),
    ]
    for b in batches:
        db_session.add(b)
    db_session.commit()
    
    response = client.get("/user/me/batches", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


def test_get_user_movements(client, auth_headers, db_session):
    """Testa listagem de movimentações do usuário"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement

    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    movements = [
        Movement(tipo_movimentacao="plantio", quantidade=100, batch_id=batch.id, user_id=1),
        Movement(tipo_movimentacao="colheita", quantidade=90, batch_id=batch.id, user_id=1),
    ]
    for m in movements:
        db_session.add(m)
    db_session.commit()
    
    response = client.get("/user/me/movements", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2


def test_get_user_recent_activity(client, auth_headers, db_session):
    """Testa atividade recente do usuário"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement

    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    movement = Movement(
        tipo_movimentacao="plantio",
        quantidade=100,
        batch_id=batch.id,
        user_id=1
    )
    db_session.add(movement)
    db_session.commit()
    
    response = client.get("/user/me/recent-activity?limit=5", headers=auth_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "recent_movements" in data
    assert "recent_batches" in data
    assert len(data["recent_movements"]) <= 5
    assert len(data["recent_batches"]) <= 5


def test_delete_own_account(client, auth_headers, db_session):
    """Testa deleção da própria conta"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    # Cria usuário temporário
    temp_user = User(
        nome="Temp User",
        email="temp@test.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="99999999999"
    )
    db_session.add(temp_user)
    db_session.commit()
    db_session.refresh(temp_user)
    
    # Faz login como usuário temporário
    from proraf.security import create_access_token
    token = create_access_token(data={"sub": temp_user.email})
    temp_headers = {
        "X-API-Key": auth_headers["X-API-Key"],
        "Authorization": f"Bearer {token}"
    }
    
    # Deleta conta
    response = client.delete("/user/me", headers=temp_headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica que foi deletado
    deleted_user = db_session.query(User).filter(User.email == "temp@test.com").first()
    assert deleted_user is None


def test_user_cannot_access_without_auth(client, api_headers):
    """Testa que rotas requerem autenticação"""
    response = client.get("/user/me", headers=api_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_pagination_user_batches(client, auth_headers, db_session):
    """Testa paginação de lotes do usuário"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch

    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Cria 15 lotes
    for i in range(15):
        batch = Batch(code=f"LOTE-{i:03d}", product_id=product.id, user_id=1)
        db_session.add(batch)
    db_session.commit()
    
    # Primeira página
    response = client.get("/user/me/batches?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10
    
    # Segunda página
    response = client.get("/user/me/batches?skip=10&limit=10", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5