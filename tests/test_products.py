import pytest
from fastapi import status


def test_create_product(client, auth_headers):
    """Testa criação de produto"""
    response = client.post(
        "/products/",
        json={
            "name": "Tomate Cereja",
            "comertial_name": "Tomate Cherry Premium",
            "description": "Tomate cereja orgânico",
            "variedade_cultivar": "Sweet 100",
            "image": "https://example.com/images/tomate-cereja.jpg",
            "code": "TOM-001",
            "status": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Tomate Cereja"
    assert data["code"] == "TOM-001"
    assert "id" in data


def test_create_product_duplicate_code(client, auth_headers, db_session):
    """Testa criação de produto com código duplicado"""
    from proraf.models.product import Product
    
    # Tenta criar com mesmo código
    response = client.post(
        "/products/",
        json={
            "name": "New Product",
            "code": "EXIST-001"
        },
        headers=auth_headers
    )
    response = client.post(
        "/products/",
        json={
            "name": "New Product",
            "code": "EXIST-001"
        },
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_products(client, auth_headers, db_session):
    """Testa listagem de produtos"""
    from proraf.models.product import Product
    
    # Cria produtos
    products = [
        Product(name="Product 1", code="PROD-001", user_id=1),
        Product(name="Product 2", code="PROD-002", user_id=1),
        Product(name="Product 3", code="PROD-003", status=False, user_id=1)
    ]
    for p in products:
        db_session.add(p)
    db_session.commit()
    
    # Lista todos
    response = client.get("/products/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3


def test_list_products_with_status_filter(client, auth_headers, db_session):
    """Testa listagem com filtro de status"""
    from proraf.models.product import Product
    
    products = [
        Product(name="Active 1", code="ACT-001", status=True, user_id=1),
        Product(name="Active 2", code="ACT-002", status=True, user_id=1),
        Product(name="Inactive", code="INACT-001", status=False, user_id=1)
    ]
    for p in products:
        db_session.add(p)
    db_session.commit()
    
    # Lista apenas ativos
    response = client.get(
        "/products/?status_filter=true",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(p["status"] for p in data)


def test_get_product_by_id(client, auth_headers, db_session):
    """Testa busca de produto por ID"""
    from proraf.models.product import Product

    product = Product(name="Test Product", code="TEST-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    response = client.get(f"/products/{product.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == product.id
    assert data["name"] == "Test Product"


def test_get_nonexistent_product(client, auth_headers):
    """Testa busca de produto inexistente"""
    response = client.get("/products/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_product(client, auth_headers, db_session):
    """Testa atualização de produto"""
    from proraf.models.product import Product

    product = Product(name="Old Name", code="PROD-001", user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    response = client.put(
        f"/products/{product.id}",
        json={"name": "New Name", "description": "Updated description"},
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Name"
    assert data["description"] == "Updated description"


def test_delete_product(client, auth_headers, db_session):
    """Testa deleção (soft delete) de produto"""
    from proraf.models.product import Product

    product = Product(name="To Delete", code="DEL-001", status=True, user_id=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    response = client.delete(f"/products/{product.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica se foi soft delete
    deleted_product = db_session.query(Product).get(product.id)
    assert deleted_product.status is False


def test_access_without_authentication(client, api_headers):
    """Testa acesso sem autenticação"""
    response = client.get("/products/", headers=api_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN