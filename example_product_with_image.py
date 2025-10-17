#!/usr/bin/env python3
"""
Exemplo de como criar produtos com imagem usando a API ProRAF

Este arquivo demonstra como usar o endpoint de criação de produtos 
incluindo o campo de imagem que foi implementado.
"""

import asyncio
import httpx
import json

# Dados de exemplo para criar produto com imagem
product_examples = [
    {
        "name": "Tomate Cereja",
        "comertial_name": "Sweet Cherry Premium",
        "description": "Tomate cereja orgânico de alta qualidade, ideal para saladas",
        "variedade_cultivar": "Sweet Cherry",
        "code": "TOM-001",
        "image": "https://example.com/images/tomate-cereja.jpg",
        "status": True
    },
    {
        "name": "Alface Crespa",
        "comertial_name": "Alface Premium",
        "description": "Alface crespa hidropônica",
        "variedade_cultivar": "Crespa Verde",
        "code": "ALF-001", 
        "image": "data:image/jpeg;base64,/9j4AAQSkZJRgABAQEAYABgAAD...",  # Exemplo de base64
        "status": True
    },
    {
        "name": "Cenoura",
        "code": "CEN-001",
        # Sem imagem - campo é opcional
        "status": True
    }
]

async def create_product_with_image():
    """
    Exemplo de como fazer uma requisição POST para criar produto com imagem
    """
    
    # Configuração da API
    base_url = "http://localhost:8000"
    api_key = "your-api-key"
    token = "your-jwt-token"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        for i, product_data in enumerate(product_examples, 1):
            try:
                print(f"\n=== Exemplo {i}: Criando '{product_data['name']}' ===")
                
                response = await client.post(
                    f"{base_url}/products/",
                    headers=headers,
                    json=product_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    print("✅ Produto criado com sucesso!")
                    print(f"   ID: {result.get('id')}")
                    print(f"   Nome: {result.get('name')}")
                    print(f"   Código: {result.get('code')}")
                    print(f"   Imagem: {result.get('image', 'Não informado')}")
                else:
                    print(f"❌ Erro ao criar produto: {response.status_code}")
                    print(f"   Resposta: {response.text}")
                    
            except Exception as e:
                print(f"❌ Erro na requisição: {e}")


def validate_product_data():
    """
    Exemplo de como validar dados de produto localmente antes de enviar
    """
    print("\n=== Validação Local dos Dados ===")
    
    from proraf.schemas.product import ProductCreate
    
    for i, product_data in enumerate(product_examples, 1):
        try:
            product_schema = ProductCreate(**product_data)
            print(f"✅ Exemplo {i} válido: {product_data['name']}")
            
            # Mostrar dados validados
            validated_data = product_schema.model_dump()
            if validated_data.get('image'):
                image_preview = validated_data['image'][:50] + "..." if len(validated_data['image']) > 50 else validated_data['image']
                print(f"   Imagem: {image_preview}")
            else:
                print("   Imagem: Não informada")
                
        except Exception as e:
            print(f"❌ Exemplo {i} inválido: {e}")


if __name__ == "__main__":
    print("=== Exemplo de Uso - Produtos com Imagem ===")
    
    # Validar dados localmente
    validate_product_data()
    
    print("\n" + "="*50)
    print("Para testar a API real, descomente e configure:")
    print("1. Inicie o servidor: poetry run task dev")
    print("2. Configure API_KEY e JWT token válidos")
    print("3. Execute: asyncio.run(create_product_with_image())")
    
    # Para testar com API real, descomente a linha abaixo:
    # asyncio.run(create_product_with_image())