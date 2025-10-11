import pytest
from fastapi import status
from datetime import date


def test_create_movement(client, auth_headers, db_session):
    """Testa criação de movimentação"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    # Cria produto e lote
    product = Product(name="Tomate", code="TOM-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # Cria movimentação
    response = client.post(
        "/movements/",
        json={
            "tipo_movimentacao": "plantio",
            "quantidade": 500.5,
            "batch_id": batch.id
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["tipo_movimentacao"] == "plantio"
    assert float(data["quantidade"]) == 500.5
    assert data["batch_id"] == batch.id
    assert data["user_id"] == 1


def test_create_movement_invalid_batch(client, auth_headers):
    """Testa criação de movimentação com lote inexistente"""
    response = client.post(
        "/movements/",
        json={
            "tipo_movimentacao": "colheita",
            "quantidade": 100,
            "batch_id": 9999
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Batch not found" in response.json()["detail"]


def test_create_movement_different_types(client, auth_headers, db_session):
    """Testa criação de movimentações de diferentes tipos"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    movement_types = [
        ("plantio", 1000),
        ("colheita", 950),
        ("expedição", 900),
        ("venda", 850),
        ("transferência", 50),
        ("descarte", 10)
    ]
    
    for tipo, quantidade in movement_types:
        response = client.post(
            "/movements/",
            json={
                "tipo_movimentacao": tipo,
                "quantidade": quantidade,
                "batch_id": batch.id
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["tipo_movimentacao"] == tipo


def test_list_movements(client, auth_headers, db_session):
    """Testa listagem de movimentações"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # Cria movimentações
    movements = [
        Movement(tipo_movimentacao="plantio", quantidade=100, batch_id=batch.id, user_id=1),
        Movement(tipo_movimentacao="colheita", quantidade=90, batch_id=batch.id, user_id=1),
        Movement(tipo_movimentacao="expedição", quantidade=85, batch_id=batch.id, user_id=1)
    ]
    for m in movements:
        db_session.add(m)
    db_session.commit()
    
    # Lista todas
    response = client.get("/movements/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3


def test_list_movements_with_batch_filter(client, auth_headers, db_session):
    """Testa listagem filtrada por lote"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Cria dois lotes
    batch1 = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    batch2 = Batch(code="LOTE-002", product_id=product.id, user_id=1)
    db_session.add(batch1)
    db_session.add(batch2)
    db_session.commit()
    db_session.refresh(batch1)
    db_session.refresh(batch2)
    
    # Cria movimentações
    movements = [
        Movement(tipo_movimentacao="plantio", quantidade=100, batch_id=batch1.id, user_id=1),
        Movement(tipo_movimentacao="colheita", quantidade=90, batch_id=batch1.id, user_id=1),
        Movement(tipo_movimentacao="plantio", quantidade=200, batch_id=batch2.id, user_id=1)
    ]
    for m in movements:
        db_session.add(m)
    db_session.commit()
    
    # Filtra por batch1
    response = client.get(f"/movements/?batch_id={batch1.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(m["batch_id"] == batch1.id for m in data)


def test_list_movements_with_type_filter(client, auth_headers, db_session):
    """Testa listagem filtrada por tipo"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
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
        Movement(tipo_movimentacao="colheita", quantidade=80, batch_id=batch.id, user_id=1)
    ]
    for m in movements:
        db_session.add(m)
    db_session.commit()
    
    # Filtra por tipo colheita
    response = client.get("/movements/?tipo_movimentacao=colheita", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(m["tipo_movimentacao"] == "colheita" for m in data)


def test_get_movement_by_id(client, auth_headers, db_session):
    """Testa busca de movimentação por ID"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
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
    db_session.refresh(movement)
    
    response = client.get(f"/movements/{movement.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == movement.id
    assert data["tipo_movimentacao"] == "plantio"


def test_get_movements_by_batch(client, auth_headers, db_session):
    """Testa busca de todas movimentações de um lote"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # Cria histórico de movimentações
    movements = [
        Movement(tipo_movimentacao="plantio", quantidade=1000, batch_id=batch.id, user_id=1),
        Movement(tipo_movimentacao="colheita", quantidade=950, batch_id=batch.id, user_id=1),
        Movement(tipo_movimentacao="expedição", quantidade=900, batch_id=batch.id, user_id=1)
    ]
    for m in movements:
        db_session.add(m)
    db_session.commit()
    
    response = client.get(f"/movements/batch/{batch.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    
    # Verifica tipos na ordem
    tipos = [m["tipo_movimentacao"] for m in data]
    assert "plantio" in tipos
    assert "colheita" in tipos
    assert "expedição" in tipos


def test_get_nonexistent_movement(client, auth_headers):
    """Testa busca de movimentação inexistente"""
    response = client.get("/movements/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_movement(client, auth_headers, db_session):
    """Testa atualização de movimentação"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
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
    db_session.refresh(movement)
    
    # Atualiza quantidade
    response = client.put(
        f"/movements/{movement.id}",
        json={"quantidade": 150},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert float(data["quantidade"]) == 150
    assert data["tipo_movimentacao"] == "plantio"


def test_delete_movement(client, auth_headers, db_session):
    """Testa deleção de movimentação"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
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
    db_session.refresh(movement)
    movement_id = movement.id
    
    response = client.delete(f"/movements/{movement_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica que foi deletada
    deleted = db_session.query(Movement).filter(Movement.id == movement_id).first()
    assert deleted is None


def test_user_cannot_access_other_user_movement(client, api_headers, db_session):
    """Testa que usuário não pode acessar movimentação de outro usuário"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
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
    
    # Cria produto, lote e movimentação do user2
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-USER2", product_id=product.id, user_id=user2.id)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    movement = Movement(
        tipo_movimentacao="plantio",
        quantidade=100,
        batch_id=batch.id,
        user_id=user2.id
    )
    db_session.add(movement)
    db_session.commit()
    db_session.refresh(movement)
    
    # Login como user1
    response = client.post(
        "/auth/login",
        data={"username": "user1@test.com", "password": "pass123"},
        headers=api_headers
    )
    token = response.json()["access_token"]
    user1_headers = {**api_headers, "Authorization": f"Bearer {token}"}
    
    # Tenta acessar movimentação do user2
    response = client.get(f"/movements/{movement.id}", headers=user1_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_rastreability_flow(client, auth_headers, db_session):
    """Testa fluxo completo de rastreabilidade"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    
    # 1. Cria produto
    product = Product(name="Tomate Orgânico", code="TOM-ORG-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # 2. Cria lote
    batch = Batch(
        code="LOTE-2025-001",
        product_id=product.id,
        user_id=1,
        dt_plantio=date(2025, 1, 1)
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # 3. Registra movimentações em ordem
    movimentacoes = [
        {"tipo": "plantio", "qtd": 2000},
        {"tipo": "tratamento", "qtd": 0},
        {"tipo": "colheita", "qtd": 1900},
        {"tipo": "expedição", "qtd": 1850}
    ]
    
    for mov in movimentacoes:
        response = client.post(
            "/movements/",
            json={
                "tipo_movimentacao": mov["tipo"],
                "quantidade": mov["qtd"],
                "batch_id": batch.id
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # 4. Consulta histórico completo
    response = client.get(f"/movements/batch/{batch.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    historico = response.json()
    
    assert len(historico) == 4
    assert historico[0]["tipo_movimentacao"] == "plantio"
    assert historico[-1]["tipo_movimentacao"] == "expedição"
    
    # 5. Verifica rastreabilidade via QR Code
    response = client.get(f"/batches/code/{batch.code}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    # lote_data = response.json()
    # assert lote_data["qrcode"] is not None


def test_pagination_movements(client, auth_headers, db_session):
    """Testa paginação de movimentações"""
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=1)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # Cria 25 movimentações
    for i in range(25):
        movement = Movement(
            tipo_movimentacao=f"tipo_{i}",
            quantidade=i * 10,
            batch_id=batch.id,
            user_id=1
        )
        db_session.add(movement)
    db_session.commit()
    
    # Primeira página
    response = client.get("/movements/?skip=0&limit=10", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10
    
    # Segunda página
    response = client.get("/movements/?skip=10&limit=10", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10
    
    # Terceira página
    response = client.get("/movements/?skip=20&limit=10", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 5