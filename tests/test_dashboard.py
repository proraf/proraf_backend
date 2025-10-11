import pytest
from fastapi import status


@pytest.fixture
def admin_headers(client, api_headers, db_session):
    """Headers com autenticação de administrador"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    admin = User(
        nome="Admin User",
        email="admin@proraf.com",
        senha=get_password_hash("admin123"),
        tipo_pessoa="F",
        cpf="00000000000",
        tipo_perfil="admin"
    )
    db_session.add(admin)
    db_session.commit()
    
    response = client.post(
        "/auth/login",
        data={"username": "admin@proraf.com", "password": "admin123"},
        headers=api_headers
    )
    
    token = response.json()["access_token"]
    return {**api_headers, "Authorization": f"Bearer {token}"}


def test_dashboard_overview(client, admin_headers, db_session):
    """Testa visão geral do dashboard"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    from proraf.security import get_password_hash
    
    # Cria dados de teste
    user = User(nome="User", email="user@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="11111111111")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-001", product_id=product.id, user_id=user.id)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    movement = Movement(tipo_movimentacao="plantio", quantidade=100, batch_id=batch.id, user_id=user.id)
    db_session.add(movement)
    db_session.commit()
    
    response = client.get("/admin/dashboard/overview", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verifica estrutura
    assert "users" in data
    assert "products" in data
    assert "batches" in data
    assert "movements" in data
    
    # Verifica dados de usuários
    assert data["users"]["total"] >= 2
    assert data["users"]["admins"] >= 1
    assert data["users"]["regular"] >= 1
    
    # Verifica dados de produtos
    assert data["products"]["total"] >= 1
    assert data["products"]["active"] >= 1
    
    # Verifica dados de lotes
    assert data["batches"]["total"] >= 1
    assert data["batches"]["active"] >= 1
    
    # Verifica dados de movimentações
    assert data["movements"]["total"] >= 1
    assert "by_type" in data["movements"]


def test_dashboard_recent_activity(client, admin_headers, db_session):
    """Testa atividades recentes"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    from proraf.security import get_password_hash
    
    # Cria dados
    user = User(nome="User", email="user2@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="22222222222")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(name="Product 2", code="PROD-002")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(code="LOTE-002", product_id=product.id, user_id=user.id)
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    movement = Movement(tipo_movimentacao="colheita", quantidade=200, batch_id=batch.id, user_id=user.id)
    db_session.add(movement)
    db_session.commit()
    
    response = client.get("/admin/dashboard/recent-activity", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "recent_movements" in data
    assert "recent_batches" in data
    assert "recent_users" in data
    
    assert len(data["recent_movements"]) > 0
    assert len(data["recent_batches"]) > 0
    assert len(data["recent_users"]) > 0


def test_dashboard_recent_activity_with_limit(client, admin_headers, db_session):
    """Testa limite de atividades recentes"""
    response = client.get("/admin/dashboard/recent-activity?limit=5", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data["recent_movements"]) <= 5
    assert len(data["recent_batches"]) <= 5
    assert len(data["recent_users"]) <= 5


def test_dashboard_production_summary(client, admin_headers, db_session):
    """Testa resumo de produção"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.security import get_password_hash
    
    user = User(nome="Producer", email="producer@test.com", senha=get_password_hash("pass"), tipo_pessoa="F", cpf="33333333333")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Cria produto com múltiplos lotes
    product = Product(name="Tomate", code="TOM-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batches = [
        Batch(code="LOTE-T1", product_id=product.id, user_id=user.id, producao=1000),
        Batch(code="LOTE-T2", product_id=product.id, user_id=user.id, producao=1500),
        Batch(code="LOTE-T3", product_id=product.id, user_id=user.id, producao=2000),
    ]
    for b in batches:
        db_session.add(b)
    db_session.commit()
    
    response = client.get("/admin/dashboard/production-summary", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "production" in data
    assert len(data["production"]) > 0
    
    # Verifica se tomate está na lista
    tomate = next((p for p in data["production"] if p["product_code"] == "TOM-001"), None)
    assert tomate is not None
    assert tomate["total_batches"] == 3
    assert tomate["total_production"] == 4500


def test_regular_user_cannot_access_dashboard(client, auth_headers):
    """Testa que usuário comum não pode acessar dashboard"""
    response = client.get("/admin/dashboard/overview", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    response = client.get("/admin/dashboard/recent-activity", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    response = client.get("/admin/dashboard/production-summary", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_dashboard_with_empty_data(client, admin_headers, db_session):
    """Testa dashboard com dados vazios"""
    # Limpa movimentações para testar estrutura vazia
    from proraf.models.movement import Movement
    db_session.query(Movement).delete()
    db_session.commit()
    
    response = client.get("/admin/dashboard/overview", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["movements"]["total"] == 0
    assert data["movements"]["by_type"] == []