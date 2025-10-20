import pytest
from fastapi import status


def test_track_batch_by_code(client, api_headers, db_session):
    """Testa rastreamento de lote por código (público)"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    from proraf.security import get_password_hash
    from datetime import date
    
    # Cria usuário (produtor)
    user = User(
        nome="João Silva",
        email="joao@farm.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="12345678901"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Cria produto
    product = Product(
        name="Tomate Cereja",
        code="TOM-001",
        comertial_name="Tomate Sweet Cherry",
        description="Tomate orgânico"
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Cria lote
    batch = Batch(
        code="LOTE-TEST-001",
        product_id=product.id,
        user_id=user.id,
        dt_plantio=date(2025, 1, 1),
        dt_colheita=date(2025, 3, 15),
        producao=1500,
        talhao="Talhão A1",
        qrcode="QR-123456"
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # Cria movimentações
    movements = [
        Movement(tipo_movimentacao="plantio", quantidade=2000, batch_id=batch.id, user_id=user.id),
        Movement(tipo_movimentacao="colheita", quantidade=1900, batch_id=batch.id, user_id=user.id),
    ]
    for m in movements:
        db_session.add(m)
    db_session.commit()
    
    # Testa rastreamento (não requer autenticação de usuário)
    response = client.get(f"/tracking/{batch.code}", headers=api_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verifica estrutura da resposta
    assert "batch" in data
    assert "product" in data
    assert "producer" in data
    assert "movements" in data
    assert "stats" in data
    
    # Verifica dados do lote
    assert data["batch"]["code"] == "LOTE-TEST-001"
    assert data["batch"]["producao"] == 1500
    assert data["batch"]["talhao"] == "Talhão A1"
    assert data["batch"]["qrcode"] == "QR-123456"
    
    # Verifica dados do produto
    assert data["product"]["name"] == "Tomate Cereja"
    assert data["product"]["code"] == "TOM-001"
    assert data["product"]["comertial_name"] == "Tomate Sweet Cherry"
    
    # Verifica dados do produtor (sem dados sensíveis)
    assert data["producer"]["nome"] == "João Silva"
    assert data["producer"]["tipo_pessoa"] == "F"
    assert "email" not in data["producer"]
    assert "cpf" not in data["producer"]
    assert "cnpj" not in data["producer"]
    assert "telefone" not in data["producer"]
    
    # Verifica movimentações
    assert len(data["movements"]) == 2
    assert data["movements"][0]["tipo_movimentacao"] == "plantio"
    assert data["movements"][1]["tipo_movimentacao"] == "colheita"
    
    # Verifica estatísticas
    assert data["stats"]["total_movements"] == 2
    assert data["stats"]["total_production"] == 1500
    assert data["stats"]["days_since_planting"] is not None


def test_track_batch_by_qrcode(client, api_headers, db_session):
    """Testa rastreamento de lote por QR Code"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.security import get_password_hash
    
    user = User(
        nome="Maria Santos",
        email="maria@farm.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="J",
        cnpj="12345678000190"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(name="Alface", code="ALF-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(
        code="LOTE-QR-001",
        product_id=product.id,
        user_id=user.id,
        qrcode="QR-UNIQUE-CODE-123"
    )
    db_session.add(batch)
    db_session.commit()
    
    # Rastreia por QR Code
    response = client.get("/tracking/qr/QR-UNIQUE-CODE-123", headers=api_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["batch"]["code"] == "LOTE-QR-001"
    assert data["batch"]["qrcode"] == "QR-UNIQUE-CODE-123"
    assert data["product"]["name"] == "Alface"
    assert data["producer"]["nome"] == "Maria Santos"
    assert data["producer"]["tipo_pessoa"] == "J"


def test_track_nonexistent_batch(client, api_headers):
    """Testa rastreamento de lote inexistente"""
    response = client.get("/tracking/LOTE-INEXISTENTE", headers=api_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "não encontrado" in response.json()["detail"].lower()


def test_track_nonexistent_qrcode(client, api_headers):
    """Testa rastreamento com QR Code inexistente"""
    response = client.get("/tracking/qr/QR-INVALIDO", headers=api_headers)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_track_without_api_key(client):
    """Testa que rastreamento requer API Key"""
    response = client.get("/tracking/LOTE-001")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_track_batch_with_no_movements(client, api_headers, db_session):
    """Testa rastreamento de lote sem movimentações"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.security import get_password_hash
    
    user = User(
        nome="Teste User",
        email="test@farm.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="11111111111"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(name="Product", code="PROD-001")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(
        code="LOTE-NO-MOVEMENTS",
        product_id=product.id,
        user_id=user.id
    )
    db_session.add(batch)
    db_session.commit()
    
    response = client.get("/tracking/LOTE-NO-MOVEMENTS", headers=api_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["movements"] == []
    assert data["stats"]["total_movements"] == 0


def test_track_batch_days_calculation(client, api_headers, db_session):
    """Testa cálculo de dias desde plantio"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.security import get_password_hash
    from datetime import date, timedelta
    
    user = User(
        nome="Teste",
        email="test2@farm.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="22222222222"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(name="Product", code="PROD-002")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Lote plantado há 30 dias
    plant_date = date.today() - timedelta(days=30)
    batch = Batch(
        code="LOTE-DAYS-TEST",
        product_id=product.id,
        user_id=user.id,
        dt_plantio=plant_date
    )
    db_session.add(batch)
    db_session.commit()
    
    response = client.get("/tracking/LOTE-DAYS-TEST", headers=api_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Deve calcular aproximadamente 30 dias
    assert data["stats"]["days_since_planting"] == 30


def test_track_batch_no_planting_date(client, api_headers, db_session):
    """Testa lote sem data de plantio"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.security import get_password_hash
    
    user = User(
        nome="Teste",
        email="test3@farm.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="33333333333"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(name="Product", code="PROD-003")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(
        code="LOTE-NO-DATE",
        product_id=product.id,
        user_id=user.id,
        dt_plantio=None
    )
    db_session.add(batch)
    db_session.commit()
    
    response = client.get("/tracking/LOTE-NO-DATE", headers=api_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["batch"]["dt_plantio"] is None
    assert data["stats"]["days_since_planting"] is None


def test_track_batch_data_privacy(client, api_headers, db_session):
    """Testa que dados sensíveis não são expostos"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.security import get_password_hash
    
    user = User(
        nome="Produtor Teste",
        email="produtor@farm.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="99999999999",
        telefone="51999999999"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(name="Product", code="PROD-PRIV")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(
        code="LOTE-PRIVACY",
        product_id=product.id,
        user_id=user.id
    )
    db_session.add(batch)
    db_session.commit()
    
    response = client.get("/tracking/LOTE-PRIVACY", headers=api_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verifica que dados sensíveis NÃO estão na resposta
    producer = data["producer"]
    assert "email" not in producer
    assert "cpf" not in producer
    assert "cnpj" not in producer
    assert "telefone" not in producer
    assert "senha" not in producer
    
    # Verifica que apenas dados públicos estão presentes
    assert "nome" in producer
    assert "tipo_pessoa" in producer


def test_track_batch_complete_lifecycle(client, api_headers, db_session):
    """Testa rastreamento de lote com ciclo completo"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.models.batch import Batch
    from proraf.models.movement import Movement
    from proraf.security import get_password_hash
    from datetime import date
    
    user = User(
        nome="Agricultor Completo",
        email="completo@farm.com",
        senha=get_password_hash("pass123"),
        tipo_pessoa="F",
        cpf="44444444444"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    product = Product(
        name="Tomate Industrial",
        code="TOM-IND-001",
        comertial_name="Tomate Supreme",
        description="Tomate para processamento industrial"
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    batch = Batch(
        code="LOTE-COMPLETE-001",
        product_id=product.id,
        user_id=user.id,
        dt_plantio=date(2025, 1, 1),
        dt_colheita=date(2025, 3, 15),
        dt_expedition=date(2025, 3, 20),
        producao=5000,
        talhao="Talhão Premium"
    )
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)
    
    # Ciclo completo de movimentações
    movements = [
        Movement(tipo_movimentacao="plantio", quantidade=5500, batch_id=batch.id, user_id=user.id),
        Movement(tipo_movimentacao="tratamento", quantidade=0, batch_id=batch.id, user_id=user.id),
        Movement(tipo_movimentacao="colheita", quantidade=5200, batch_id=batch.id, user_id=user.id),
        Movement(tipo_movimentacao="expedição", quantidade=5000, batch_id=batch.id, user_id=user.id),
    ]
    for m in movements:
        db_session.add(m)
    db_session.commit()
    
    response = client.get("/tracking/LOTE-COMPLETE-001", headers=api_headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verifica todas as datas
    assert data["batch"]["dt_plantio"] is not None
    assert data["batch"]["dt_colheita"] is not None
    assert data["batch"]["dt_expedition"] is not None
    
    # Verifica movimentações em ordem
    assert len(data["movements"]) == 4
    assert data["movements"][0]["tipo_movimentacao"] == "plantio"
    assert data["movements"][-1]["tipo_movimentacao"] == "expedição"
    
    # Verifica estatísticas
    assert data["stats"]["total_movements"] == 4
    assert data["stats"]["total_production"] == 5000