"""
Testes para funcionalidades de blockchain em Lotes e Movimentações.

Testa:
- Novos campos editáveis (product_name, product_type, buyer_name, etc.)
- Campos blockchain imutáveis
- Endpoint PATCH para registro de dados blockchain
- Validação de imutabilidade
"""
import pytest
from fastapi import status
from datetime import date


# =============================================================================
# TESTES DE LOTE COM CAMPOS BLOCKCHAIN
# =============================================================================

class TestBatchBlockchainFields:
    """Testes para campos blockchain em lotes"""
    
    def test_create_batch_with_product_info(self, client, auth_headers, db_session):
        """Testa criação de lote com campos product_name e product_type"""
        from proraf.models.product import Product
        
        product = Product(
            name="Tomate Cereja",
            code="TOM-BC-001",
            user_id=1,
            variedade_cultivar="Sweet Million"
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        response = client.post(
            "/batches/",
            json={
                "code": "LOTE-BC-001",
                "product_id": product.id,
                "product_name": "Tomate Cereja",
                "product_type": "Sweet Million",
                "dt_plantio": "2025-01-15",
                "dt_colheita": "2025-04-20",
                "producao": 500.5,
                "unidadeMedida": "kg"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_name"] == "Tomate Cereja"
        assert data["product_type"] == "Sweet Million"
        # Campos blockchain devem estar vazios
        assert data["blockchain_token_id"] is None
        assert data["blockchain_address_who"] is None
    
    def test_create_batch_blockchain_fields_null_by_default(self, client, auth_headers, db_session):
        """Testa que campos blockchain são null por padrão"""
        from proraf.models.product import Product
        
        product = Product(name="Alface", code="ALF-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        response = client.post(
            "/batches/",
            json={
                "code": "LOTE-NULL-BC",
                "product_id": product.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Todos campos blockchain devem ser null
        assert data["blockchain_address_who"] is None
        assert data["blockchain_address_to"] is None
        assert data["blockchain_product_name"] is None
        assert data["blockchain_product_expedition_date"] is None
        assert data["blockchain_product_type"] is None
        assert data["blockchain_batch_id"] is None
        assert data["blockchain_unit_of_measure"] is None
        assert data["blockchain_batch_quantity"] is None
        assert data["blockchain_token_id"] is None
    
    def test_register_batch_blockchain_data(self, client, auth_headers, db_session):
        """Testa registro de dados blockchain via PATCH"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        
        product = Product(name="Tomate", code="TOM-002", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-PATCH-BC", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        # Registra dados blockchain
        blockchain_data = {
            "blockchain_address_who": "0x1234567890abcdef1234567890abcdef12345678",
            "blockchain_address_to": "0xabcdef1234567890abcdef1234567890abcdef12",
            "blockchain_product_name": "Tomate Orgânico",
            "blockchain_product_expedition_date": "2025-05-20",
            "blockchain_product_type": "Orgânico",
            "blockchain_batch_id": "LOTE-PATCH-BC",
            "blockchain_unit_of_measure": "kg",
            "blockchain_batch_quantity": 500.0,
            "blockchain_token_id": 12345
        }
        
        response = client.patch(
            f"/batches/{batch.id}/blockchain",
            json=blockchain_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["blockchain_token_id"] == 12345
        assert data["blockchain_address_who"] == "0x1234567890abcdef1234567890abcdef12345678"
        assert data["blockchain_product_name"] == "Tomate Orgânico"
        assert data["blockchain_batch_quantity"] == 500.0
    
    def test_batch_blockchain_immutability(self, client, auth_headers, db_session):
        """Testa que dados blockchain são imutáveis após primeiro registro"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        
        product = Product(name="Laranja", code="LAR-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(
            code="LOTE-IMMUTABLE",
            product_id=product.id,
            user_id=1,
            blockchain_token_id=99999  # Já tem token
        )
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        # Tenta modificar dados blockchain
        response = client.patch(
            f"/batches/{batch.id}/blockchain",
            json={"blockchain_token_id": 11111},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "immutable" in response.json()["detail"].lower()
    
    def test_update_batch_editable_fields(self, client, auth_headers, db_session):
        """Testa que product_name e product_type são editáveis via PUT"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        
        product = Product(name="Uva", code="UVA-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(
            code="LOTE-EDIT",
            product_id=product.id,
            user_id=1,
            product_name="Uva Original",
            product_type="Tipo Original"
        )
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        response = client.put(
            f"/batches/{batch.id}",
            json={
                "product_name": "Uva Atualizada",
                "product_type": "Tipo Atualizado"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["product_name"] == "Uva Atualizada"
        assert data["product_type"] == "Tipo Atualizado"
    
    def test_batch_blockchain_partial_update(self, client, auth_headers, db_session):
        """Testa atualização parcial de dados blockchain"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        
        product = Product(name="Morango", code="MOR-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-PARTIAL", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        # Envia apenas alguns campos
        response = client.patch(
            f"/batches/{batch.id}/blockchain",
            json={
                "blockchain_token_id": 54321,
                "blockchain_product_name": "Morango Premium"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["blockchain_token_id"] == 54321
        assert data["blockchain_product_name"] == "Morango Premium"
        # Outros campos podem ser null
    
    def test_batch_blockchain_not_found(self, client, auth_headers):
        """Testa PATCH em lote inexistente"""
        response = client.patch(
            "/batches/99999/blockchain",
            json={"blockchain_token_id": 1},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# TESTES DE MOVIMENTAÇÃO COM CAMPOS BLOCKCHAIN
# =============================================================================

class TestMovementBlockchainFields:
    """Testes para campos blockchain em movimentações"""
    
    def test_create_movement_with_buyer_info(self, client, auth_headers, db_session):
        """Testa criação de movimentação com campos do comprador"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        
        product = Product(name="Tomate", code="TOM-MOV-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-MOV-001", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        response = client.post(
            "/movements/",
            json={
                "tipo_movimentacao": "venda",
                "quantidade": 100.5,
                "batch_id": batch.id,
                "buyer_name": "Supermercado ABC",
                "buyer_identification": "12.345.678/0001-90",
                "current_location": "São Paulo, SP"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["buyer_name"] == "Supermercado ABC"
        assert data["buyer_identification"] == "12.345.678/0001-90"
        assert data["current_location"] == "São Paulo, SP"
        # Blockchain deve ser null
        assert data["blockchain_token_id"] is None
    
    def test_create_movement_blockchain_fields_null_by_default(self, client, auth_headers, db_session):
        """Testa que campos blockchain são null por padrão"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        
        product = Product(name="Alface", code="ALF-MOV-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-MOV-NULL", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        response = client.post(
            "/movements/",
            json={
                "tipo_movimentacao": "expedição",
                "quantidade": 50,
                "batch_id": batch.id
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Todos campos blockchain devem ser null
        assert data["blockchain_updater"] is None
        assert data["blockchain_token_id"] is None
        assert data["blockchain_message"] is None
        assert data["blockchain_buyer_name"] is None
        assert data["blockchain_buyer_identification"] is None
        assert data["blockchain_current_location"] is None
        assert data["blockchain_update_type"] is None
    
    def test_register_movement_blockchain_data(self, client, auth_headers, db_session):
        """Testa registro de dados blockchain via PATCH"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        from proraf.models.movement import Movement
        
        product = Product(name="Uva", code="UVA-MOV-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-MOV-PATCH", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        movement = Movement(
            tipo_movimentacao="venda",
            quantidade=200,
            batch_id=batch.id,
            user_id=1,
            buyer_name="Restaurante XYZ",
            buyer_identification="98.765.432/0001-10"
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        # Registra dados blockchain
        blockchain_data = {
            "blockchain_updater": "0x1234567890abcdef1234567890abcdef12345678",
            "blockchain_token_id": 67890,
            "blockchain_message": "Venda registrada na blockchain",
            "blockchain_buyer_name": "Restaurante XYZ",
            "blockchain_buyer_identification": "98.765.432/0001-10",
            "blockchain_current_location": "Rio de Janeiro, RJ",
            "blockchain_update_type": 1
        }
        
        response = client.patch(
            f"/movements/{movement.id}/blockchain",
            json=blockchain_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["blockchain_token_id"] == 67890
        assert data["blockchain_updater"] == "0x1234567890abcdef1234567890abcdef12345678"
        assert data["blockchain_message"] == "Venda registrada na blockchain"
        assert data["blockchain_update_type"] == 1
    
    def test_movement_blockchain_immutability(self, client, auth_headers, db_session):
        """Testa que dados blockchain são imutáveis após primeiro registro"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        from proraf.models.movement import Movement
        
        product = Product(name="Manga", code="MAN-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-MOV-IMM", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        movement = Movement(
            tipo_movimentacao="expedição",
            quantidade=300,
            batch_id=batch.id,
            user_id=1,
            blockchain_token_id=88888  # Já tem token
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        # Tenta modificar dados blockchain
        response = client.patch(
            f"/movements/{movement.id}/blockchain",
            json={"blockchain_token_id": 11111},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "immutable" in response.json()["detail"].lower()
    
    def test_update_movement_editable_fields(self, client, auth_headers, db_session):
        """Testa que campos do comprador são editáveis via PUT"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        from proraf.models.movement import Movement
        
        product = Product(name="Pera", code="PER-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-MOV-EDIT", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        movement = Movement(
            tipo_movimentacao="venda",
            quantidade=150,
            batch_id=batch.id,
            user_id=1,
            buyer_name="Comprador Original",
            current_location="Local Original"
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        response = client.put(
            f"/movements/{movement.id}",
            json={
                "buyer_name": "Comprador Atualizado",
                "current_location": "Local Atualizado"
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["buyer_name"] == "Comprador Atualizado"
        assert data["current_location"] == "Local Atualizado"
    
    def test_movement_blockchain_partial_update(self, client, auth_headers, db_session):
        """Testa atualização parcial de dados blockchain"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        from proraf.models.movement import Movement
        
        product = Product(name="Abacaxi", code="ABA-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-MOV-PART", product_id=product.id, user_id=1)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        movement = Movement(
            tipo_movimentacao="transferência",
            quantidade=75,
            batch_id=batch.id,
            user_id=1
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        # Envia apenas alguns campos
        response = client.patch(
            f"/movements/{movement.id}/blockchain",
            json={
                "blockchain_token_id": 11111,
                "blockchain_update_type": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["blockchain_token_id"] == 11111
        assert data["blockchain_update_type"] == 2
    
    def test_movement_blockchain_not_found(self, client, auth_headers):
        """Testa PATCH em movimentação inexistente"""
        response = client.patch(
            "/movements/99999/blockchain",
            json={"blockchain_token_id": 1},
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# TESTES DE FLUXO COMPLETO COM BLOCKCHAIN
# =============================================================================

class TestBlockchainFlow:
    """Testes de fluxo completo com blockchain"""
    
    def test_complete_blockchain_flow(self, client, auth_headers, db_session):
        """Testa fluxo completo: produto -> lote -> blockchain -> movimentação -> blockchain"""
        from proraf.models.product import Product
        
        # 1. Cria produto
        product = Product(
            name="Café Arábica",
            code="CAF-001",
            user_id=1,
            variedade_cultivar="Bourbon Amarelo"
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        # 2. Cria lote com informações do produto
        batch_response = client.post(
            "/batches/",
            json={
                "code": "LOTE-CAFE-2025",
                "product_id": product.id,
                "product_name": product.name,
                "product_type": product.variedade_cultivar,
                "dt_plantio": "2024-01-01",
                "dt_colheita": "2025-06-01",
                "dt_expedition": "2025-06-15",
                "producao": 1000.0,
                "unidadeMedida": "kg"
            },
            headers=auth_headers
        )
        assert batch_response.status_code == status.HTTP_201_CREATED
        batch = batch_response.json()
        batch_id = batch["id"]
        
        # 3. Registra lote na blockchain
        blockchain_batch = client.patch(
            f"/batches/{batch_id}/blockchain",
            json={
                "blockchain_address_who": "0xProdutor123",
                "blockchain_address_to": "0xComprador456",
                "blockchain_product_name": "Café Arábica",
                "blockchain_product_expedition_date": "2025-06-15",
                "blockchain_product_type": "Bourbon Amarelo",
                "blockchain_batch_id": "LOTE-CAFE-2025",
                "blockchain_unit_of_measure": "kg",
                "blockchain_batch_quantity": 1000.0,
                "blockchain_token_id": 100001
            },
            headers=auth_headers
        )
        assert blockchain_batch.status_code == status.HTTP_200_OK
        
        # 4. Cria movimentação de venda
        movement_response = client.post(
            "/movements/",
            json={
                "tipo_movimentacao": "venda",
                "quantidade": 500,
                "batch_id": batch_id,
                "buyer_name": "Torrefadora Premium",
                "buyer_identification": "11.222.333/0001-44",
                "current_location": "Minas Gerais"
            },
            headers=auth_headers
        )
        assert movement_response.status_code == status.HTTP_201_CREATED
        movement = movement_response.json()
        movement_id = movement["id"]
        
        # 5. Registra movimentação na blockchain
        blockchain_movement = client.patch(
            f"/movements/{movement_id}/blockchain",
            json={
                "blockchain_updater": "0xProdutor123",
                "blockchain_token_id": 100001,
                "blockchain_message": "Venda de 500kg para Torrefadora Premium",
                "blockchain_buyer_name": "Torrefadora Premium",
                "blockchain_buyer_identification": "11.222.333/0001-44",
                "blockchain_current_location": "Minas Gerais",
                "blockchain_update_type": 1
            },
            headers=auth_headers
        )
        assert blockchain_movement.status_code == status.HTTP_200_OK
        
        # 6. Verifica que lote tem blockchain registrada
        batch_final = client.get(f"/batches/{batch_id}", headers=auth_headers)
        assert batch_final.status_code == status.HTTP_200_OK
        batch_data = batch_final.json()
        assert batch_data["blockchain_token_id"] == 100001
        
        # 7. Verifica que movimentação tem blockchain registrada
        movement_final = client.get(f"/movements/{movement_id}", headers=auth_headers)
        assert movement_final.status_code == status.HTTP_200_OK
        movement_data = movement_final.json()
        assert movement_data["blockchain_token_id"] == 100001
        
        # 8. Tenta modificar blockchain do lote (deve falhar)
        immutable_batch = client.patch(
            f"/batches/{batch_id}/blockchain",
            json={"blockchain_token_id": 999999},
            headers=auth_headers
        )
        assert immutable_batch.status_code == status.HTTP_400_BAD_REQUEST
        
        # 9. Tenta modificar blockchain da movimentação (deve falhar)
        immutable_movement = client.patch(
            f"/movements/{movement_id}/blockchain",
            json={"blockchain_token_id": 999999},
            headers=auth_headers
        )
        assert immutable_movement.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_multiple_movements_same_batch(self, client, auth_headers, db_session):
        """Testa múltiplas movimentações para o mesmo lote"""
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        
        product = Product(name="Soja", code="SOJ-001", user_id=1)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(
            code="LOTE-SOJA-MULTI",
            product_id=product.id,
            user_id=1,
            producao=10000
        )
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        # Registra blockchain do lote
        client.patch(
            f"/batches/{batch.id}/blockchain",
            json={"blockchain_token_id": 200001},
            headers=auth_headers
        )
        
        # Cria várias movimentações
        movimentacoes = [
            {"tipo": "colheita", "qtd": 10000, "buyer": None},
            {"tipo": "venda", "qtd": 3000, "buyer": "Comprador A"},
            {"tipo": "venda", "qtd": 4000, "buyer": "Comprador B"},
            {"tipo": "venda", "qtd": 3000, "buyer": "Comprador C"}
        ]
        
        movement_ids = []
        for idx, mov in enumerate(movimentacoes):
            response = client.post(
                "/movements/",
                json={
                    "tipo_movimentacao": mov["tipo"],
                    "quantidade": mov["qtd"],
                    "batch_id": batch.id,
                    "buyer_name": mov["buyer"]
                },
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_201_CREATED
            movement_ids.append(response.json()["id"])
            
            # Registra blockchain apenas para vendas
            if mov["tipo"] == "venda":
                bc_response = client.patch(
                    f"/movements/{movement_ids[-1]}/blockchain",
                    json={
                        "blockchain_token_id": 200001 + idx,
                        "blockchain_update_type": 1,
                        "blockchain_buyer_name": mov["buyer"]
                    },
                    headers=auth_headers
                )
                assert bc_response.status_code == status.HTTP_200_OK
        
        # Verifica todas movimentações do lote
        response = client.get(f"/movements/batch/{batch.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        movements = response.json()
        assert len(movements) == 4
        
        # Verifica que vendas têm blockchain e colheita não
        colheitas = [m for m in movements if m["tipo_movimentacao"] == "colheita"]
        vendas = [m for m in movements if m["tipo_movimentacao"] == "venda"]
        
        assert len(colheitas) == 1
        assert colheitas[0]["blockchain_token_id"] is None
        
        assert len(vendas) == 3
        assert all(v["blockchain_token_id"] is not None for v in vendas)


# =============================================================================
# TESTES DE VALIDAÇÃO E ERROS
# =============================================================================

class TestBlockchainValidation:
    """Testes de validação de dados blockchain"""
    
    def test_batch_blockchain_unauthorized(self, client, api_headers, db_session):
        """Testa PATCH sem autenticação (retorna 403 pois precisa de token JWT)"""
        from proraf.models.user import User
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        from proraf.security import get_password_hash

        user = User(
            nome="Test User", email="unauth@test.com",
            senha=get_password_hash("testpass123"),
            tipo_pessoa="F", cpf="00000000001", tipo_perfil="user"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        product = Product(name="Test", code="TST-001", user_id=user.id)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-UNAUTH", product_id=product.id, user_id=user.id)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        response = client.patch(
            f"/batches/{batch.id}/blockchain",
            json={"blockchain_token_id": 1},
            headers=api_headers  # Sem token JWT
        )
        
        # API retorna 403 Forbidden quando token JWT não está presente
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_movement_blockchain_unauthorized(self, client, api_headers, db_session):
        """Testa PATCH de movimentação sem autenticação (retorna 403 pois precisa de token JWT)"""
        from proraf.models.user import User
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        from proraf.models.movement import Movement
        from proraf.security import get_password_hash

        user = User(
            nome="Test User", email="unauth2@test.com",
            senha=get_password_hash("testpass123"),
            tipo_pessoa="F", cpf="00000000002", tipo_perfil="user"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        product = Product(name="Test", code="TST-002", user_id=user.id)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-UNAUTH-MOV", product_id=product.id, user_id=user.id)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        movement = Movement(
            tipo_movimentacao="teste",
            quantidade=10,
            batch_id=batch.id,
            user_id=user.id
        )
        db_session.add(movement)
        db_session.commit()
        db_session.refresh(movement)
        
        response = client.patch(
            f"/movements/{movement.id}/blockchain",
            json={"blockchain_token_id": 1},
            headers=api_headers  # Sem token JWT
        )
        
        # API retorna 403 Forbidden quando token JWT não está presente
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_batch_blockchain_wrong_user(self, client, api_headers, db_session):
        """Testa PATCH em lote de outro usuário"""
        from proraf.models.user import User
        from proraf.models.product import Product
        from proraf.models.batch import Batch
        from proraf.security import get_password_hash
        
        # Cria dois usuários
        user1 = User(
            nome="User 1",
            email="user1bc@test.com",
            senha=get_password_hash("pass123"),
            tipo_pessoa="F",
            cpf="11111111111"
        )
        user2 = User(
            nome="User 2",
            email="user2bc@test.com",
            senha=get_password_hash("pass123"),
            tipo_pessoa="F",
            cpf="22222222222"
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        
        # Produto e lote do user2
        product = Product(name="Product", code="PROD-BC", user_id=user2.id)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        batch = Batch(code="LOTE-OTHER", product_id=product.id, user_id=user2.id)
        db_session.add(batch)
        db_session.commit()
        db_session.refresh(batch)
        
        # Login como user1
        login_response = client.post(
            "/auth/login",
            data={"username": "user1bc@test.com", "password": "pass123"},
            headers=api_headers
        )
        token = login_response.json()["access_token"]
        user1_headers = {**api_headers, "Authorization": f"Bearer {token}"}
        
        # Tenta registrar blockchain no lote do user2
        response = client.patch(
            f"/batches/{batch.id}/blockchain",
            json={"blockchain_token_id": 1},
            headers=user1_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
