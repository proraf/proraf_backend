from fastapi import status


def test_public_list_products(client, db_session):
    """Rota pública: lista todos os produtos com nome do produtor"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.security import get_password_hash

    producer = User(
        nome="Produtor A",
        email="produtor.a@test.com",
        senha=get_password_hash("123456"),
        tipo_pessoa="F",
        cpf="11111111111",
    )
    db_session.add(producer)
    db_session.commit()
    db_session.refresh(producer)

    product = Product(
        name="Abacaxi",
        description="Fruta tropical",
        image="https://img.test/abacaxi.png",
        code="ABX-001",
        user_id=producer.id,
    )
    db_session.add(product)
    db_session.commit()

    response = client.get("/public/products")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["nome"] == "Abacaxi"
    assert data[0]["produtor_nome"] == "Produtor A"


def test_public_list_producers(client, db_session):
    """Rota pública: lista produtores com imagem"""
    from proraf.models.user import User
    from proraf.security import get_password_hash

    producer = User(
        nome="Produtora B",
        email="produtora.b@test.com",
        senha=get_password_hash("123456"),
        tipo_pessoa="F",
        cpf="22222222222",
    )
    db_session.add(producer)
    db_session.commit()

    response = client.get("/public/producers")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["nome"] == "Produtora B"
    assert data[0]["imagem"] == "static/images/users/icone.png"


def test_public_search_products_and_producers(client, db_session):
    """Rota pública: busca textual em produtos e produtores"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.security import get_password_hash

    producer = User(
        nome="Abadia Produtor",
        email="abadia@test.com",
        senha=get_password_hash("123456"),
        tipo_pessoa="F",
        cpf="33333333333",
    )
    db_session.add(producer)
    db_session.commit()
    db_session.refresh(producer)

    product = Product(
        name="Abacaxi",
        description="Fruta tropical",
        image="https://img.test/abacaxi.png",
        code="ABX-002",
        user_id=producer.id,
    )
    db_session.add(product)
    db_session.commit()

    response = client.get("/public/search?q=aba")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "produtos" in data
    assert "produtores" in data
    assert any(item["nome"] == "Abacaxi" for item in data["produtos"])
    assert any(item["nome"] == "Abadia Produtor" for item in data["produtores"])


def test_public_list_products_by_producer(client, db_session):
    """Rota pública: lista produtos de um produtor pelo ID"""
    from proraf.models.user import User
    from proraf.models.product import Product
    from proraf.security import get_password_hash

    producer = User(
        nome="Produtor C",
        email="produtor.c@test.com",
        senha=get_password_hash("123456"),
        tipo_pessoa="F",
        cpf="44444444444",
    )
    other_producer = User(
        nome="Produtor D",
        email="produtor.d@test.com",
        senha=get_password_hash("123456"),
        tipo_pessoa="F",
        cpf="55555555555",
    )
    db_session.add(producer)
    db_session.add(other_producer)
    db_session.commit()
    db_session.refresh(producer)
    db_session.refresh(other_producer)

    db_session.add(
        Product(
            name="Banana",
            description="Fruta amarela",
            code="BAN-001",
            user_id=producer.id,
        )
    )
    db_session.add(
        Product(
            name="Maçã",
            description="Fruta vermelha",
            code="MAC-001",
            user_id=other_producer.id,
        )
    )
    db_session.commit()

    response = client.get(f"/public/producers/{producer.id}/products")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["nome"] == "Banana"
