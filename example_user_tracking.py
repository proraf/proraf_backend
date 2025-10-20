#!/usr/bin/env python3
"""
Exemplo de como usar a funcionalidade de rastreamento de usuário em produtos

Este arquivo demonstra como os produtos agora incluem o ID do usuário que os criou,
permitindo rastrear quem adicionou cada produto no sistema.
"""

import asyncio
import httpx
import json

# Exemplo de criação de produto (agora com rastreamento de usuário)
product_example = {
    "name": "Tomate Cereja Orgânico",
    "comertial_name": "Cherry Organic Premium",
    "description": "Tomate cereja orgânico cultivado sem agrotóxicos",
    "variedade_cultivar": "Sweet Cherry",
    "code": "TOM-ORG-001",
    "image": "https://example.com/images/tomate-cereja-organico.jpg",
    "status": True
    # Nota: user_id NÃO é enviado - é capturado automaticamente do usuário logado
}

async def example_create_product_with_user_tracking():
    """
    Exemplo de como criar produto com rastreamento de usuário
    """
    
    base_url = "http://localhost:8000"
    api_key = "your-api-key"
    token = "your-jwt-token"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("=== Criando Produto com Rastreamento de Usuário ===")
            
            response = await client.post(
                f"{base_url}/products/",
                headers=headers,
                json=product_example
            )
            
            if response.status_code == 201:
                result = response.json()
                print("✅ Produto criado com sucesso!")
                print(f"   ID: {result.get('id')}")
                print(f"   Nome: {result.get('name')}")
                print(f"   Código: {result.get('code')}")
                print(f"   Criado por usuário: {result.get('user_id')}")
                print(f"   Data de criação: {result.get('created_at')}")
                
                product_id = result.get('id')
                user_id = result.get('user_id')
                
                print("\n=== Listando Produtos do Usuário ===")
                
                # Listar apenas produtos do usuário logado
                my_products_response = await client.get(
                    f"{base_url}/products/my-products",
                    headers=headers
                )
                
                if my_products_response.status_code == 200:
                    my_products = my_products_response.json()
                    print(f"📦 Você tem {len(my_products)} produto(s):")
                    for product in my_products:
                        print(f"   - {product['name']} (ID: {product['id']})")
                
                # Listar todos os produtos com filtro
                print("\n=== Filtros Disponíveis ===")
                
                # Filtro 1: Apenas meus produtos
                response = await client.get(
                    f"{base_url}/products/?my_products_only=true",
                    headers=headers
                )
                print(f"🔍 Filtro 'meus produtos': {len(response.json()) if response.status_code == 200 else 'erro'} resultado(s)")
                
                # Filtro 2: Por status
                response = await client.get(
                    f"{base_url}/products/?status_filter=true&my_products_only=true", 
                    headers=headers
                )
                print(f"🔍 Filtro 'meus produtos ativos': {len(response.json()) if response.status_code == 200 else 'erro'} resultado(s)")
                
            else:
                print(f"❌ Erro ao criar produto: {response.status_code}")
                print(f"   Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")


def demonstrate_schema_validation():
    """
    Demonstra como os schemas funcionam com o campo user_id
    """
    print("\n=== Validação de Schemas ===")
    
    from proraf.schemas.product import ProductCreate, ProductResponse
    
    # 1. Schema de entrada (NÃO inclui user_id)
    try:
        product_create = ProductCreate(**product_example)
        print("✅ ProductCreate validado com sucesso")
        print(f"   Campos de entrada: {list(product_create.model_dump().keys())}")
        print(f"   user_id incluído na entrada? {'user_id' in product_create.model_dump()}")
    except Exception as e:
        print(f"❌ Erro no ProductCreate: {e}")
    
    # 2. Schema de resposta (INCLUI user_id)
    try:
        response_data = {
            "id": 1,
            "name": product_example["name"],
            "code": product_example["code"], 
            "comertial_name": product_example["comertial_name"],
            "description": product_example["description"],
            "variedade_cultivar": product_example["variedade_cultivar"],
            "status": product_example["status"],
            "image": product_example["image"],
            "user_id": 1,  # Adicionado automaticamente pelo sistema
            "created_at": "2025-10-20T10:00:00Z",
            "updated_at": "2025-10-20T10:00:00Z"
        }
        
        product_response = ProductResponse(**response_data)
        print("✅ ProductResponse validado com sucesso")
        print(f"   Campos de saída: {list(product_response.model_dump().keys())}")
        print(f"   user_id incluído na saída? {'user_id' in product_response.model_dump()}")
        print(f"   Valor do user_id: {product_response.user_id}")
        
    except Exception as e:
        print(f"❌ Erro no ProductResponse: {e}")


if __name__ == "__main__":
    print("=== Sistema de Rastreamento de Usuário em Produtos ===")
    print("🎯 Funcionalidades implementadas:")
    print("   • Campo user_id adicionado ao modelo Product")
    print("   • Captura automática do usuário logado na criação")
    print("   • Filtros para listar produtos por usuário")
    print("   • Endpoint /my-products para produtos próprios")
    print("   • Relacionamento Product -> User no banco")
    
    # Demonstrar validação
    demonstrate_schema_validation()
    
    print("\n" + "="*50)
    print("Para testar a API real:")
    print("1. Inicie o servidor: poetry run task dev")
    print("2. Configure API_KEY e JWT token válidos")
    print("3. Execute: asyncio.run(example_create_product_with_user_tracking())")
    
    # Para testar com API real, descomente a linha abaixo:
    # asyncio.run(example_create_product_with_user_tracking())