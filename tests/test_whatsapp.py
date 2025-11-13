import pytest
from fastapi import status
from proraf.security import generate_whatsapp_hash


@pytest.fixture
def user_with_phone(db_session):
    """Cria usuário com telefone para testes"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    user = User(
        nome="WhatsApp User",
        email="whatsapp@example.com",
        senha=get_password_hash("testpass123"),
        tipo_pessoa="F",
        cpf="11122233344",
        cnpj=None,
        telefone="55996852212",
        tipo_perfil="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def multiple_users_with_phones(db_session):
    """Cria múltiplos usuários com telefones"""
    from proraf.models.user import User
    from proraf.security import get_password_hash
    
    users = [
        User(
            nome="User 1",
            email="user1@example.com",
            senha=get_password_hash("pass123"),
            tipo_pessoa="F",
            cpf="11111111111",
            telefone="55991111111",
            tipo_perfil="user"
        ),
        User(
            nome="User 2",
            email="user2@example.com",
            senha=get_password_hash("pass123"),
            tipo_pessoa="J",
            cnpj="22222222222222",
            telefone="55992222222",
            tipo_perfil="user"
        ),
        User(
            nome="User 3 No Phone",
            email="user3@example.com",
            senha=get_password_hash("pass123"),
            tipo_pessoa="F",
            cpf="33333333333",
            telefone=None,  # Sem telefone
            tipo_perfil="user"
        )
    ]
    
    for user in users:
        db_session.add(user)
    db_session.commit()
    
    return users


class TestListRegisteredPhones:
    """Testes para GET /whatsapp/phones"""
    
    def test_list_phones_with_valid_hash(self, client, multiple_users_with_phones):
        """Testa listagem de telefones com hash válido"""
        # Gera hash válido para PHONE_LIST
        valid_hash = generate_whatsapp_hash("PHONE_LIST")
        
        response = client.get(
            f"/whatsapp/phones?hash={valid_hash}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Deve retornar apenas telefones não-nulos (2 de 3 usuários)
        assert len(data) == 2
        assert "55991111111" in data
        assert "55992222222" in data
    
    def test_list_phones_with_invalid_hash(self, client, multiple_users_with_phones):
        """Testa listagem com hash inválido"""
        invalid_hash = "invalid_hash_12345"
        
        response = client.get(
            f"/whatsapp/phones?hash={invalid_hash}"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication hash" in response.json()["detail"]
    
    def test_list_phones_without_hash(self, client):
        """Testa listagem sem fornecer hash"""
        response = client.get("/whatsapp/phones")
        
        # FastAPI deve retornar erro de validação
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_phones_empty_database(self, client, db_session):
        """Testa listagem quando não há telefones cadastrados"""
        valid_hash = generate_whatsapp_hash("PHONE_LIST")
        
        response = client.get(
            f"/whatsapp/phones?hash={valid_hash}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []


class TestVerifyPhone:
    """Testes para POST /whatsapp/verify-phone"""
    
    def test_verify_existing_phone(self, client, user_with_phone):
        """Testa verificação de telefone existente"""
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        response = client.post(
            "/whatsapp/verify-phone",
            json={
                "telefone": telefone,
                "hash": valid_hash
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["exists"] is True
        assert data["user_id"] == user_with_phone.id
        assert data["nome"] == user_with_phone.nome
        assert data["email"] == user_with_phone.email
        assert data["tipo_pessoa"] == user_with_phone.tipo_pessoa
    
    def test_verify_nonexistent_phone(self, client):
        """Testa verificação de telefone não cadastrado"""
        telefone = "55999999999"
        valid_hash = generate_whatsapp_hash(telefone)
        
        response = client.post(
            "/whatsapp/verify-phone",
            json={
                "telefone": telefone,
                "hash": valid_hash
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["exists"] is False
        assert data["user_id"] is None
        assert data["nome"] is None
        assert data["email"] is None
        assert data["tipo_pessoa"] is None
    
    def test_verify_phone_with_invalid_hash(self, client, user_with_phone):
        """Testa verificação com hash inválido"""
        telefone = user_with_phone.telefone
        invalid_hash = "invalid_hash_abc123"
        
        response = client.post(
            "/whatsapp/verify-phone",
            json={
                "telefone": telefone,
                "hash": invalid_hash
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication hash" in response.json()["detail"]
    
    def test_verify_phone_with_wrong_hash(self, client, user_with_phone):
        """Testa verificação com hash de outro telefone"""
        telefone = user_with_phone.telefone
        # Gera hash para telefone diferente
        wrong_hash = generate_whatsapp_hash("55988888888")
        
        response = client.post(
            "/whatsapp/verify-phone",
            json={
                "telefone": telefone,
                "hash": wrong_hash
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_verify_phone_missing_fields(self, client):
        """Testa verificação sem campos obrigatórios"""
        # Sem telefone
        response = client.post(
            "/whatsapp/verify-phone",
            json={"hash": "some_hash"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Sem hash
        response = client.post(
            "/whatsapp/verify-phone",
            json={"telefone": "55996852212"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateProductViaWhatsApp:
    """Testes para POST /whatsapp/create-product"""
    
    def test_create_product_successfully(self, client, user_with_phone, db_session):
        """Testa criação de produto com sucesso via WhatsApp"""
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": valid_hash,
                "name": "Laranja",
                "description": "Laranja Lima orgânica",
                "variedade_cultivar": "Lima"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["success"] is True
        assert "created successfully" in data["message"]
        assert data["product_id"] is not None
        assert data["product_name"] == "Laranja"
        assert data["qrcode_url"] is not None
        
        # Verifica no banco de dados
        from proraf.models.product import Product
        product = db_session.query(Product).filter(
            Product.id == data["product_id"]
        ).first()
        
        assert product is not None
        assert product.name == "Laranja"
        assert product.user_id == user_with_phone.id
        assert product.status is True  # Boolean: True = ativo
    
    def test_create_product_duplicate_name(self, client, user_with_phone, db_session):
        """Testa criação de produto com nome duplicado"""
        from proraf.models.product import Product
        import secrets
        
        # Cria produto existente
        code = secrets.token_urlsafe(8)
        existing = Product(
            name="Tomate",
            user_id=user_with_phone.id,
            status=True,  # Boolean: True = ativo
            code=code
        )
        db_session.add(existing)
        db_session.commit()
        
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        # Tenta criar com mesmo nome
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": valid_hash,
                "name": "Tomate"
            }
        )
        
        # Deve retornar sucesso=false mas status 200/201
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        
        assert data["success"] is False
        assert "already exists" in data["message"]
        assert data["product_id"] == existing.id
    
    def test_create_product_with_invalid_hash(self, client, user_with_phone):
        """Testa criação com hash inválido"""
        telefone = user_with_phone.telefone
        invalid_hash = "invalid_hash_xyz"
        
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": invalid_hash,
                "name": "Produto Teste"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid authentication hash" in response.json()["detail"]
    
    def test_create_product_with_unregistered_phone(self, client):
        """Testa criação com telefone não cadastrado"""
        telefone = "55999999999"
        valid_hash = generate_whatsapp_hash(telefone)
        
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": valid_hash,
                "name": "Produto Teste"
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not registered" in response.json()["detail"]
    
    def test_create_product_minimal_data(self, client, user_with_phone, db_session):
        """Testa criação com dados mínimos obrigatórios"""
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": valid_hash,
                "name": "Alface"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["success"] is True
        assert data["product_name"] == "Alface"
        
        # Verifica campos opcionais como None
        from proraf.models.product import Product
        product = db_session.query(Product).filter(
            Product.id == data["product_id"]
        ).first()
        
        assert product.description is None
        assert product.variedade_cultivar is None
    
    def test_create_product_with_all_fields(self, client, user_with_phone, db_session):
        """Testa criação com todos os campos preenchidos"""
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": valid_hash,
                "name": "Morango",
                "description": "Morango orgânico cultivado em estufa",
                "variedade_cultivar": "Camarosa"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        from proraf.models.product import Product
        product = db_session.query(Product).filter(
            Product.id == data["product_id"]
        ).first()
        
        assert product.name == "Morango"
        assert product.description == "Morango orgânico cultivado em estufa"
        assert product.variedade_cultivar == "Camarosa"
        assert product.comertial_name == "Morango"  # Usa mesmo nome
    
    def test_create_product_missing_required_fields(self, client, user_with_phone):
        """Testa criação sem campos obrigatórios"""
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        # Sem nome do produto
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": valid_hash
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Sem telefone
        response = client.post(
            "/whatsapp/create-product",
            json={
                "hash": valid_hash,
                "name": "Produto"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Sem hash
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "name": "Produto"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_product_invalid_name_length(self, client, user_with_phone):
        """Testa criação com nome inválido (muito curto)"""
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": valid_hash,
                "name": "AB"  # Menos de 3 caracteres
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGenerateHashForPhone:
    """Testes para GET /whatsapp/generate-hash/{telefone}"""
    
    def test_generate_hash_for_valid_phone(self, client):
        """Testa geração de hash para telefone"""
        telefone = "55996852212"
        
        response = client.get(f"/whatsapp/generate-hash/{telefone}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["telefone"] == telefone
        assert "hash" in data
        assert len(data["hash"]) == 64  # SHA256 hex = 64 caracteres
        assert data["info"] is not None
        
        # Verifica se o hash gerado é válido
        expected_hash = generate_whatsapp_hash(telefone)
        assert data["hash"] == expected_hash
    
    def test_generate_hash_consistency(self, client):
        """Testa se hash gerado é sempre o mesmo"""
        telefone = "55991234567"
        
        response1 = client.get(f"/whatsapp/generate-hash/{telefone}")
        response2 = client.get(f"/whatsapp/generate-hash/{telefone}")
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        hash1 = response1.json()["hash"]
        hash2 = response2.json()["hash"]
        
        assert hash1 == hash2  # Hash deve ser determinístico
    
    def test_generate_hash_different_phones(self, client):
        """Testa que telefones diferentes geram hashes diferentes"""
        response1 = client.get("/whatsapp/generate-hash/55991111111")
        response2 = client.get("/whatsapp/generate-hash/55992222222")
        
        hash1 = response1.json()["hash"]
        hash2 = response2.json()["hash"]
        
        assert hash1 != hash2


class TestGenerateListHash:
    """Testes para GET /whatsapp/list-hash"""
    
    def test_generate_list_hash(self, client):
        """Testa geração de hash para listagem de telefones"""
        response = client.get("/whatsapp/list-hash")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["identifier"] == "PHONE_LIST"
        assert "hash" in data
        assert len(data["hash"]) == 64
        assert "usage" in data
        
        # Verifica se o hash é válido
        expected_hash = generate_whatsapp_hash("PHONE_LIST")
        assert data["hash"] == expected_hash
    
    def test_list_hash_consistency(self, client):
        """Testa consistência do hash de listagem"""
        response1 = client.get("/whatsapp/list-hash")
        response2 = client.get("/whatsapp/list-hash")
        
        hash1 = response1.json()["hash"]
        hash2 = response2.json()["hash"]
        
        assert hash1 == hash2


class TestWhatsAppIntegrationFlow:
    """Testes de fluxo completo da integração WhatsApp"""
    
    def test_complete_flow_new_user_creates_product(self, client, user_with_phone, db_session):
        """Testa fluxo completo: verificar usuário -> criar produto"""
        telefone = user_with_phone.telefone
        
        # Passo 1: Verificar se usuário existe
        verify_hash = generate_whatsapp_hash(telefone)
        verify_response = client.post(
            "/whatsapp/verify-phone",
            json={
                "telefone": telefone,
                "hash": verify_hash
            }
        )
        
        assert verify_response.status_code == status.HTTP_200_OK
        verify_data = verify_response.json()
        assert verify_data["exists"] is True
        
        # Passo 2: Criar produto para esse usuário
        create_hash = generate_whatsapp_hash(telefone)
        create_response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": create_hash,
                "name": "Abacaxi",
                "description": "Abacaxi pérola"
            }
        )
        
        assert create_response.status_code == status.HTTP_201_CREATED
        create_data = create_response.json()
        assert create_data["success"] is True
        
        # Verifica produto no banco
        from proraf.models.product import Product
        product = db_session.query(Product).filter(
            Product.id == create_data["product_id"]
        ).first()
        
        assert product.user_id == verify_data["user_id"]
    
    def test_flow_unregistered_user_cannot_create_product(self, client):
        """Testa que usuário não cadastrado não pode criar produto"""
        telefone = "55999999999"
        
        # Verifica que não existe
        verify_hash = generate_whatsapp_hash(telefone)
        verify_response = client.post(
            "/whatsapp/verify-phone",
            json={
                "telefone": telefone,
                "hash": verify_hash
            }
        )
        
        assert verify_response.json()["exists"] is False
        
        # Tenta criar produto
        create_hash = generate_whatsapp_hash(telefone)
        create_response = client.post(
            "/whatsapp/create-product",
            json={
                "telefone": telefone,
                "hash": create_hash,
                "name": "Produto Teste"
            }
        )
        
        assert create_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_flow_user_creates_multiple_products(self, client, user_with_phone, db_session):
        """Testa usuário criando múltiplos produtos diferentes"""
        telefone = user_with_phone.telefone
        valid_hash = generate_whatsapp_hash(telefone)
        
        produtos = ["Banana", "Maçã", "Pera", "Uva"]
        
        for produto in produtos:
            response = client.post(
                "/whatsapp/create-product",
                json={
                    "telefone": telefone,
                    "hash": valid_hash,
                    "name": produto
                }
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["success"] is True
        
        # Verifica todos no banco
        from proraf.models.product import Product
        user_products = db_session.query(Product).filter(
            Product.user_id == user_with_phone.id
        ).all()
        
        assert len(user_products) == len(produtos)
        product_names = [p.name for p in user_products]
        for produto in produtos:
            assert produto in product_names
