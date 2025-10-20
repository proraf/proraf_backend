import pytest
from fastapi import status
from datetime import date


def test_create_batch(client, auth_headers, db_session):
    """Testa criação de lote"""
    from proraf.models.product import Product
    
    # Cria produto primeiro
    product = Product(name="Tomate", code="TOM-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    response = client.post(
        "/batches/",
        json={
            "code": "LOTE-001",
            "dt_plantio": "2025-01-01",
            "dt_colheita": "2025-03-15",
            "talhao": "Talhão A1",
            "producao": 1500.50,
            "product_id": product.id,
            "status": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["code"] == "LOTE-001"
    assert data["talhao"] == "Talhão A1"
    assert data["qrcode"] is not None  # QR Code gerado automaticamente
    assert "QR-" in data["qrcode"]


def test_create_batch_duplicate_code(client, auth_headers, db_session):
    """Testa criação de lote com código duplicado"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Cria lote existente
    batch = Batch(
        code="LOTE-EXIST",
        product_id=product.id,
        user_id=1
    )
    db_session.add(batch)
    db_session.commit()
    
    # Tenta criar com mesmo código
    response = client.post(
        "/batches/",
        json={
            "code": "LOTE-EXIST",
            "product_id": product.id
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_create_batch_invalid_product(client, auth_headers):
    """Testa criação de lote com produto inexistente"""
    response = client.post(
        "/batches/",
        json={
            "code": "LOTE-002",
            "product_id": 9999  # Produto não existe
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Product not found" in response.json()["detail"]


def test_list_batches(client, auth_headers, db_session):
    """Testa listagem de lotes"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    # Cria produto
    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Cria lotes
    batches = [
        Batch(code="LOTE-1", product_id=product.id, user_id=1),
        Batch(code="LOTE-2", product_id=product.id, user_id=1),
        Batch(code="LOTE-3", product_id=product.id, user_id=1, status=False)
    ]
    for b in batches:
        db_session.add(b)
    db_session.commit()
    
    # Lista todos
    response = client.get("/batches/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3


def test_list_batches_with_filters(client, auth_headers, db_session):
    """Testa listagem com filtros"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    # Cria produtos
    product1 = Product(name="Product 1", code="PROD-001", user_id=1)
    product2 = Product(name="Product 2", code="PROD-002", user_id=1)
    db_session.add(product1)
    db_session.add(product2)
    db_session.commit()
    db_session.refresh(product1)
    db_session.refresh(product2)
    
    # Cria lotes
    batches = [
        Batch(code="LOTE-P1-1", product_id=product1.id, user_id=1, status=True),
        Batch(code="LOTE-P1-2", product_id=product1.id, user_id=1, status=True),
        Batch(code="LOTE-P2-1", product_id=product2.id, user_id=1, status=True),
        Batch(code="LOTE-INACT", product_id=product1.id, user_id=1, status=False)
    ]
    for b in batches:
        db_session.add(b)
    db_session.commit()
    
    # Filtrar por produto
    response = client.get(
        f"/batches/?product_id={product1.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3  # 2 ativos + 1 inativo do produto 1
    
    # Filtrar por status
    response = client.get(
        "/batches/?status_filter=true",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all(b["status"] for b in data)


def test_get_batch_by_id(client, auth_headers, db_session):
    """Testa busca de lote por ID"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-TEST", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    response = client.get(f"/batches/{batch.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == batch.id
    assert data["code"] == "LOTE-TEST"


def test_get_batch_by_code(client, auth_headers, db_session):
    """Testa busca de lote por código"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-CODE-TEST", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    
    response = client.get("/batches/code/LOTE-CODE-TEST", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["code"] == "LOTE-CODE-TEST"


def test_get_nonexistent_batch(client, auth_headers):
    """Testa busca de lote inexistente"""
    response = client.get("/batches/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_batch(client, auth_headers, db_session):
    """Testa atualização de lote"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(
        code="LOTE-UPD",
        product_id=product.id,
        user_id=1,
        producao=1000
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    response = client.put(
        f"/batches/{batch.id}",
        json={
            "producao": 2000,
            "talhao": "Talhão B2"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert float(data["producao"]) == 2000
    assert data["talhao"] == "Talhão B2"


def test_delete_batch(client, auth_headers, db_session):
    """Testa deleção (soft delete) de lote"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    product = Product(name="Product", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(
        code="LOTE-DEL",
        product_id=product.id,
        user_id=1,
        status=True
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    response = client.delete(f"/batches/{batch.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica soft delete
    db_session.refresh(batch)
    assert batch.status is False


def test_user_cannot_access_other_user_batch(client, api_headers, db_session):
    """Testa que usuário não pode acessar lote de outro usuário"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.security import get_password_hash
    
    # Cria dois usuários
    user1 = User(
        nome="User 1",
        email="user1@test.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="11111111111"
    )
    user2 = User(
        nome="User 2",
        email="user2@test.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="22222222222"
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    
    # Cria produto e lote do user2
    product = Product(name="Product", code="PROD-001", user_id=user2.id)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-USER2", product_id=product.id, user_id=user2.id)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # Login como user1
    response = client.post(
        "/auth/login",
        data={"username": "user1@test.com", "password": "pass123"},
        headers=api_headers
    )
    token = response.json()["access_token"]
    user1_headers = {**api_headers, "Authorization": f"Bearer {token}"}
    
    # Tenta acessar lote do user2
    response = client.get(f"/batches/{batch.id}", headers=user1_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_qrcode_generation(client, auth_headers, db_session):
    """Testa geração automática de QR Code"""
    from proraf.models.product import Product
    
    product = Product(name="Tomate", code="TOM-QR", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    response = client.post(
        "/batches/",
        json={
            "code": "LOTE-QR-TEST",
            "product_id": product.id
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Verifica formato do QR Code
    assert data["qrcode"] is not None
    assert data["qrcode"].startswith("QR-")
    assert len(data["qrcode"]) > 10  # QR Code com tamanho razoável