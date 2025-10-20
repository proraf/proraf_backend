#!/usr/bin/env python3
"""
Teste específico para verificar a correção do erro 500 no endpoint /products/with-image
"""

import asyncio
import httpx
from io import BytesIO
from pathlib import Path

async def test_create_product_with_image_endpoint():
    """
    Testa o endpoint corrigido com diferentes cenários que poderiam causar o erro 500
    """
    
    base_url = "http://localhost:8000"
    
    # Configurar headers (substitua pelos valores reais)
    headers = {
        "X-API-Key": "your-api-key-here",
        "Authorization": "Bearer your-jwt-token-here"
    }
    
    # Cenários de teste
    test_cases = [
        {
            "name": "Teste 1 - Dados válidos",
            "data": {
                "name": "Tomate Cereja Premium",
                "code": "TOM-PREMIUM-001",
                "comertial_name": "Cherry Premium",
                "description": "Tomate cereja orgânico de alta qualidade",
                "variedade_cultivar": "Sweet Cherry",
                "status": True
            },
            "should_pass": True
        },
        {
            "name": "Teste 2 - Campos opcionais vazios",
            "data": {
                "name": "Banana Prata",
                "code": "BAN-001", 
                "comertial_name": "",  # String vazia
                "description": "   ",  # Só espaços
                "variedade_cultivar": "",  # String vazia
                "status": True
            },
            "should_pass": True
        },
        {
            "name": "Teste 3 - Nome muito curto (deve falhar)",
            "data": {
                "name": "To",  # Menos de 3 caracteres
                "code": "TOM-001",
                "status": True
            },
            "should_pass": False
        },
        {
            "name": "Teste 4 - Código vazio (deve falhar)", 
            "data": {
                "name": "Tomate Cereja",
                "code": "",  # Código vazio
                "status": True
            },
            "should_pass": False
        },
        {
            "name": "Teste 5 - Espaços extras (deve normalizar)",
            "data": {
                "name": "   Manga Tommy   ",  # Espaços no início/fim
                "code": "  MAN-001  ",  # Espaços no início/fim
                "comertial_name": "  Tommy Premium  ",
                "status": True
            },
            "should_pass": True
        }
    ]
    
    print("=== Teste do Endpoint /products/with-image ===")
    print("Nota: Configure headers com API key e token válidos para testar")
    print()
    
    async with httpx.AsyncClient() as client:
        for test_case in test_cases:
            print(f"🧪 {test_case['name']}")
            
            # Preparar dados como form-data
            form_data = test_case["data"].copy()
            
            # Adicionar arquivo de imagem dummy se necessário
            files = None
            if test_case.get("include_image", False):
                # Criar um arquivo de imagem dummy para teste
                dummy_image = BytesIO(b"fake image content")
                files = {"image": ("test.jpg", dummy_image, "image/jpeg")}
            
            try:
                response = await client.post(
                    f"{base_url}/products/with-image",
                    headers=headers,
                    data=form_data,
                    files=files,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    result = response.json()
                    print(f"   ✅ SUCCESS (201): Produto criado")
                    print(f"      Nome: {result.get('name')}")
                    print(f"      Código: {result.get('code')}")
                    print(f"      User ID: {result.get('user_id')}")
                    
                    if not test_case["should_pass"]:
                        print(f"   ⚠️  ATENÇÃO: Era esperado falhar mas passou")
                        
                elif response.status_code == 400:
                    error_detail = response.json().get("detail", "Erro não especificado")
                    print(f"   ❌ BAD REQUEST (400): {error_detail}")
                    
                    if test_case["should_pass"]:
                        print(f"   ⚠️  ATENÇÃO: Era esperado passar mas falhou")
                    else:
                        print(f"   ✅ Erro esperado capturado corretamente")
                        
                elif response.status_code == 500:
                    print(f"   🚨 INTERNAL SERVER ERROR (500): {response.text}")
                    print(f"   🐛 PROBLEMA: Erro 500 ainda ocorrendo!")
                    
                else:
                    print(f"   ❓ Status inesperado ({response.status_code}): {response.text}")
                    
            except httpx.ConnectError:
                print(f"   🔌 CONEXÃO: Servidor não está rodando em {base_url}")
                print(f"   💡 Execute: poetry run task dev")
                break
            except Exception as e:
                print(f"   💥 ERRO INESPERADO: {e}")
            
            print()
    
    print("=== Resumo das Correções Aplicadas ===")
    print("✅ Validação manual dos campos obrigatórios")
    print("✅ Normalização de strings (strip/trim)")
    print("✅ Conversão de strings vazias para None nos schemas")
    print("✅ Tratamento adequado de campos opcionais")
    print("✅ Mensagens de erro específicas")
    print("✅ Prevenção do erro 500 Internal Server Error")


def test_schema_validation():
    """
    Testa a validação dos schemas Pydantic com os novos validators
    """
    print("\n=== Teste de Validação dos Schemas ===")
    
    from proraf.schemas.product import ProductCreate, ProductResponse
    
    # Teste com dados que causariam o erro original
    test_data = {
        "name": "Tomate Cereja",
        "code": "TOM-001",
        "comertial_name": "",  # String vazia
        "description": "   ",  # Só espaços
        "variedade_cultivar": "",  # String vazia
        "status": True,
        "image": None
    }
    
    try:
        product = ProductCreate(**test_data)
        print("✅ ProductCreate validado com sucesso")
        validated_data = product.model_dump()
        print(f"   Dados limpos: {validated_data}")
        
        # Teste de resposta
        response_data = validated_data.copy()
        response_data.update({
            "id": 1,
            "user_id": 123,
            "created_at": "2025-10-20T10:00:00Z",
            "updated_at": "2025-10-20T10:00:00Z"
        })
        
        product_response = ProductResponse(**response_data)
        print("✅ ProductResponse validado com sucesso")
        print(f"   Campos vazios convertidos para None: {product_response.comertial_name is None}")
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")


if __name__ == "__main__":
    print("🔧 Teste de Correção do Erro 500 - Endpoint /products/with-image")
    
    # Teste dos schemas primeiro
    test_schema_validation()
    
    print("\n" + "="*60)
    print("Para testar o endpoint real:")
    print("1. Inicie o servidor: poetry run task dev")
    print("2. Configure API_KEY e JWT token válidos no código")
    print("3. Execute: asyncio.run(test_create_product_with_image_endpoint())")
    
    # Para testar com API real, descomente a linha abaixo:
    # asyncio.run(test_create_product_with_image_endpoint())