# 📷 Sistema de Upload de Imagens - ProRAF

Este documento descreve as novas funcionalidades de upload e gerenciamento de imagens de produtos implementadas na API ProRAF.

## 🆕 Funcionalidades Adicionadas

### 1. **Upload de Imagens**
- Upload de arquivos de imagem (JPG, JPEG, PNG, WEBP)
- Processamento automático (redimensionamento, otimização)
- Validação de formato e tamanho
- Geração de nomes únicos para evitar conflitos

### 2. **Novos Endpoints**

#### `POST /products/upload-image`
Faz upload de uma imagem para uso posterior em produtos.
- **Entrada**: Arquivo de imagem (multipart/form-data)
- **Saída**: URL da imagem carregada
- **Tamanho máximo**: 5MB
- **Formatos aceitos**: JPG, JPEG, PNG, WEBP

#### `POST /products/with-image`
Cria um produto com upload de imagem em uma única requisição.
- **Entrada**: Dados do produto + arquivo de imagem (multipart/form-data)
- **Saída**: Produto criado com URL da imagem

#### `PUT /products/{id}/image`
Atualiza apenas a imagem de um produto existente.
- **Entrada**: Arquivo de imagem
- **Saída**: Produto atualizado
- **Comportamento**: Remove a imagem anterior se for arquivo local

#### `DELETE /products/{id}/image`
Remove a imagem de um produto específico.
- **Comportamento**: Remove o arquivo do servidor se for local
- **Saída**: Status 204 (No Content)

#### `GET /products/images/{filename}`
Serve arquivos de imagem dos produtos.
- **Uso**: Interno, chamado automaticamente pelas URLs geradas

## 🔧 Configurações

### Variáveis de Ambiente (config.py)
```python
# Upload de arquivos
upload_dir: str = "static/images/products"
max_file_size: int = 5 * 1024 * 1024  # 5MB
allowed_image_types: list[str] = [".jpg", ".jpeg", ".png", ".webp"]
max_image_width: int = 1920
max_image_height: int = 1080
```

### Estrutura de Diretórios
```
proraf-backend/
├── static/
│   └── images/
│       └── products/          # Imagens dos produtos
│           ├── uuid1.jpg
│           ├── uuid2.png
│           └── ...
├── proraf/
│   └── services/
│       └── file_service.py    # Serviço de gerenciamento de arquivos
└── ...
```

## 📋 Exemplos de Uso

### 1. Upload de Imagem Separado

```python
import requests

# Headers de autenticação
headers = {
    "X-API-Key": "sua-api-key",
    "Authorization": "Bearer seu-jwt-token"
}

# Upload da imagem
with open("produto.jpg", "rb") as f:
    files = {"file": ("produto.jpg", f, "image/jpeg")}
    
    response = requests.post(
        "http://localhost:8000/products/upload-image",
        files=files,
        headers=headers
    )
    
    if response.status_code == 201:
        image_url = response.json()["image_url"]
        print(f"Imagem carregada: {image_url}")
```

### 2. Criar Produto com Imagem (método tradicional)

```python
# Usar a URL da imagem no produto
product_data = {
    "name": "Tomate Cereja",
    "code": "TOM-001",
    "image": image_url  # URL obtida do upload
}

response = requests.post(
    "http://localhost:8000/products/",
    json=product_data,
    headers=headers
)
```

### 3. Criar Produto com Upload Direto

```python
# Dados do produto
data = {
    "name": "Tomate Cereja",
    "code": "TOM-001",
    "description": "Tomate cereja orgânico"
}

# Upload direto com criação
with open("produto.jpg", "rb") as f:
    files = {"image": ("produto.jpg", f, "image/jpeg")}
    
    response = requests.post(
        "http://localhost:8000/products/with-image",
        data=data,
        files=files,
        headers=headers
    )
```

### 4. Atualizar Apenas a Imagem

```python
product_id = 1

with open("nova_imagem.jpg", "rb") as f:
    files = {"image": ("nova_imagem.jpg", f, "image/jpeg")}
    
    response = requests.put(
        f"http://localhost:8000/products/{product_id}/image",
        files=files,
        headers=headers
    )
```

## 🔒 Validações Implementadas

### 1. **Validação de Arquivo**
- Tamanho máximo: 5MB
- Formatos aceitos: `.jpg`, `.jpeg`, `.png`, `.webp`
- Validação de conteúdo (não apenas extensão)

### 2. **Processamento de Imagem**
- Redimensionamento automático se > 1920x1080
- Otimização de qualidade (85% para JPEG)
- Conversão de RGBA/LA para RGB quando necessário
- Preservação de proporção (thumbnail)

### 3. **Segurança**
- Nomes únicos (UUID) para evitar conflitos
- Validação de tipo MIME
- Sanitização de nomes de arquivo

## 🗂️ Gerenciamento de Arquivos

### Serviço FileService
O `FileService` centraliza todas as operações com arquivos:

```python
from proraf.services.file_service import FileService

# Upload de imagem
image_path = await FileService.save_product_image(upload_file)

# Remoção de imagem
FileService.delete_image(image_path)

# URL completa
full_url = FileService.get_image_url(image_path, base_url)
```

### Comportamentos Especiais

1. **URLs Externas**: URLs que começam com `http://`, `https://` ou `data:` são tratadas como externas e não são processadas
2. **Soft Delete**: Ao desativar um produto, a imagem não é removida automaticamente
3. **Substituição**: Ao atualizar imagem, a anterior é removida se for arquivo local
4. **Fallback**: Se upload falhar, o arquivo temporário é automaticamente removido

## 🚦 Códigos de Resposta

| Código | Descrição |
|--------|-----------|
| 201 | Imagem/produto criado com sucesso |
| 200 | Imagem/produto atualizado com sucesso |
| 204 | Imagem removida com sucesso |
| 400 | Formato inválido ou dados incorretos |
| 404 | Produto ou imagem não encontrada |
| 413 | Arquivo muito grande (>5MB) |
| 500 | Erro interno no processamento |

## 📊 Compatibilidade

### Formatos Suportados
- **JPEG/JPG**: Recomendado para fotos
- **PNG**: Recomendado para imagens com transparência
- **WEBP**: Formato moderno, menor tamanho

### Browsers
- Todos os browsers modernos suportam os formatos aceitos
- URLs geradas são compatíveis com HTML `<img>` tags
- Suporte a diferentes resoluções (responsivo)

## 🔄 Migração de Dados Existentes

Para produtos com URLs externas existentes:
1. As URLs continuam funcionando normalmente
2. Use `PUT /products/{id}/image` para migrar para arquivo local
3. O campo `image` aceita tanto URLs quanto caminhos locais

## 🛠️ Troubleshooting

### Problemas Comuns

1. **"Import could not be resolved"**
   - Execute: `poetry install` para instalar dependências

2. **"File too large"**
   - Verifique se o arquivo é < 5MB
   - Configure `max_file_size` se necessário

3. **"Invalid image file"**
   - Certifique-se que é um arquivo de imagem válido
   - Tente converter para JPEG/PNG

4. **"Image not found" no navegador**
   - Verifique se o serviço de arquivos estáticos está configurado
   - Confirme que o arquivo existe em `static/images/products/`

### Logs Úteis
```bash
# Iniciar servidor com logs detalhados
poetry run task dev

# Verificar arquivos estáticos
ls -la static/images/products/

# Testar endpoint de imagem
curl -I http://localhost:8000/static/images/products/exemplo.jpg
```

## 📚 Próximos Passos

1. **Implementar thumbnails automáticos** para diferentes tamanhos
2. **Adicionar watermark** nas imagens
3. **Integração com CDN** para melhor performance
4. **Compressão avançada** baseada no formato
5. **Metadados EXIF** para informações da foto

---

**Documentação da API completa**: http://localhost:8000/docs