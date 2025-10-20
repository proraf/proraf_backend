"""
Exemplo de uso do sistema de upload de imagens para produtos

Este script demonstra como usar as novas funcionalidades de upload de imagem
"""

import requests
import json
from pathlib import Path

# Configurações da API
BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key-change-in-production"  # Substitua pela sua API key
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def login_and_get_token():
    """Faz login e retorna o token JWT"""
    login_data = {
        "username": "admin@example.com",  # Substitua pelos seus dados
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data,
        headers={"X-API-Key": API_KEY}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return token
    else:
        print(f"Erro no login: {response.text}")
        return None

def upload_image_example():
    """Exemplo de upload de imagem separado"""
    token = login_and_get_token()
    if not token:
        return
    
    headers_with_auth = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}"
    }
    
    # Exemplo com arquivo de imagem (substitua pelo caminho real)
    image_path = "example_image.jpg"
    
    if Path(image_path).exists():
        with open(image_path, "rb") as f:
            files = {"file": ("example_image.jpg", f, "image/jpeg")}
            
            response = requests.post(
                f"{BASE_URL}/products/upload-image",
                files=files,
                headers={"X-API-Key": API_KEY, "Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Imagem carregada com sucesso: {result['image_url']}")
                return result["image_url"]
            else:
                print(f"❌ Erro no upload: {response.text}")
                return None
    else:
        print(f"❌ Arquivo {image_path} não encontrado")
        return None

def create_product_with_url():
    """Exemplo de criação de produto com URL da imagem"""
    token = login_and_get_token()
    if not token:
        return
    
    headers_with_auth = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    product_data = {
        "name": "Tomate Cereja Orgânico",
        "code": "TOM-ORG-001",
        "comertial_name": "Tomate Sweet Cherry Premium",
        "description": "Tomate cereja orgânico cultivado sem agrotóxicos",
        "variedade_cultivar": "Cherry Premium",
        "status": True,
        "image": "https://example.com/images/tomate-cereja.jpg"  # URL externa
    }
    
    response = requests.post(
        f"{BASE_URL}/products/",
        json=product_data,
        headers=headers_with_auth
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Produto criado com sucesso: {result['name']} (ID: {result['id']})")
        return result["id"]
    else:
        print(f"❌ Erro na criação: {response.text}")
        return None

def create_product_with_file_upload():
    """Exemplo de criação de produto com upload de arquivo"""
    token = login_and_get_token()
    if not token:
        return
    
    headers_with_auth = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}"
    }
    
    # Dados do produto
    product_data = {
        "name": "Alface Americana",
        "code": "ALF-AME-001",
        "comertial_name": "Alface Premium",
        "description": "Alface americana fresca e crocante",
        "variedade_cultivar": "Americana Premium",
        "status": "true"
    }
    
    # Exemplo com arquivo de imagem
    image_path = "example_lettuce.jpg"
    
    if Path(image_path).exists():
        with open(image_path, "rb") as f:
            files = {
                "image": ("example_lettuce.jpg", f, "image/jpeg")
            }
            
            response = requests.post(
                f"{BASE_URL}/products/with-image",
                data=product_data,
                files=files,
                headers=headers_with_auth
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Produto com imagem criado: {result['name']} (ID: {result['id']})")
                print(f"📷 Imagem salva em: {result['image']}")
                return result["id"]
            else:
                print(f"❌ Erro na criação: {response.text}")
                return None
    else:
        print(f"📝 Criando produto sem imagem (arquivo {image_path} não encontrado)")
        
        response = requests.post(
            f"{BASE_URL}/products/with-image",
            data=product_data,
            headers=headers_with_auth
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Produto criado sem imagem: {result['name']} (ID: {result['id']})")
            return result["id"]
        else:
            print(f"❌ Erro na criação: {response.text}")
            return None

def update_product_image(product_id):
    """Exemplo de atualização de imagem do produto"""
    token = login_and_get_token()
    if not token:
        return
    
    headers_with_auth = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {token}"
    }
    
    image_path = "new_product_image.jpg"
    
    if Path(image_path).exists():
        with open(image_path, "rb") as f:
            files = {"image": ("new_product_image.jpg", f, "image/jpeg")}
            
            response = requests.put(
                f"{BASE_URL}/products/{product_id}/image",
                files=files,
                headers=headers_with_auth
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Imagem do produto {product_id} atualizada: {result['image']}")
                return True
            else:
                print(f"❌ Erro na atualização: {response.text}")
                return False
    else:
        print(f"❌ Arquivo {image_path} não encontrado")
        return False

def main():
    """Função principal de exemplo"""
    print("🚀 Testando sistema de upload de imagens do ProRAF")
    print("-" * 50)
    
    # 1. Upload de imagem separado
    print("📤 1. Testando upload de imagem separado...")
    image_url = upload_image_example()
    
    # 2. Criar produto com URL
    print("\n📦 2. Criando produto com URL de imagem...")
    product_id_1 = create_product_with_url()
    
    # 3. Criar produto com upload de arquivo
    print("\n📦 3. Criando produto com upload de arquivo...")
    product_id_2 = create_product_with_file_upload()
    
    # 4. Atualizar imagem de produto existente
    if product_id_2:
        print(f"\n🔄 4. Atualizando imagem do produto {product_id_2}...")
        update_product_image(product_id_2)
    
    print("\n✨ Teste concluído!")
    print("\n📚 Documentação completa disponível em: http://localhost:8000/docs")

if __name__ == "__main__":
    main()