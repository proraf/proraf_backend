"""
Teste rápido das novas rotas WhatsApp
Execute com: poetry run python test_whatsapp_routes.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_routes():
    print("🧪 Testando rotas WhatsApp...\n")
    
    # 1. Gerar hash para telefone de teste
    print("1️⃣  Gerando hash para telefone 555596852212...")
    response = requests.get(f"{BASE_URL}/whatsapp/generate-hash/555596852212")
    if response.status_code == 200:
        data = response.json()
        hash_value = data["hash"]
        print(f"✅ Hash gerado: {hash_value[:20]}...\n")
    else:
        print(f"❌ Erro ao gerar hash: {response.status_code}\n")
        return
    
    # 2. Criar produto
    print("2️⃣  Criando produto 'Abacaxi'...")
    product_data = {
        "telefone": "555596852212",
        "hash": hash_value,
        "name": "Abacaxi",
        "description": "Abacaxi pérola da melhor qualidade",
        "variedade_cultivar": "Pérola"
    }
    response = requests.post(
        f"{BASE_URL}/whatsapp/create-product",
        json=product_data
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result["success"]:
            product_id = result["product_id"]
            print(f"✅ Produto criado com ID: {product_id}")
            print(f"   Nome: {result['product_name']}")
            print(f"   QR Code: {result.get('qrcode_url', 'N/A')}\n")
        else:
            print(f"⚠️  {result['message']}")
            # Se produto já existe, usa o ID existente
            product_id = result.get("product_id")
            print(f"   Usando produto existente ID: {product_id}\n")
    else:
        print(f"❌ Erro ao criar produto: {response.status_code}")
        print(f"   {response.text}\n")
        return
    
    # 3. Editar produto
    print("3️⃣  Editando produto...")
    update_data = {
        "telefone": "555596852212",
        "hash": hash_value,
        "product_id": product_id,
        "description": "Abacaxi pérola premium - Certificado orgânico",
        "comertial_name": "Abacaxi Premium"
    }
    response = requests.put(
        f"{BASE_URL}/whatsapp/update-product",
        json=update_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Produto atualizado com sucesso!")
        print(f"   {result['message']}\n")
    else:
        print(f"❌ Erro ao editar produto: {response.status_code}")
        print(f"   {response.text}\n")
    
    # 4. Criar lote
    print("4️⃣  Criando lote para o produto...")
    batch_data = {
        "telefone": "555596852212",
        "hash": hash_value,
        "product_id": product_id,
        "talhao": "Talhão C3",
        "dt_plantio": "2025-09-01",
        "dt_colheita": "2025-12-15",
        "producao": 1500,
        "unidadeMedida": "kg"
    }
    response = requests.post(
        f"{BASE_URL}/whatsapp/create-batch",
        json=batch_data
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✅ Lote criado com sucesso!")
        print(f"   {result['message']}")
        print(f"   Código: {result.get('batch_code', 'N/A')}")
        print(f"   Produto: {result.get('product_name', 'N/A')}")
        print(f"   QR Code: {result.get('qrcode_url', 'N/A')}\n")
    else:
        print(f"❌ Erro ao criar lote: {response.status_code}")
        print(f"   {response.text}\n")
    
    print("✨ Testes concluídos!")


if __name__ == "__main__":
    try:
        test_routes()
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
