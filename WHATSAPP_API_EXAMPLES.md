# WhatsApp API - Exemplos de Uso

Este documento demonstra como usar as rotas da API WhatsApp para criar e editar produtos e lotes.

## 🔐 Autenticação

Todas as rotas requerem:
- `telefone`: Número de telefone do usuário cadastrado
- `hash`: Hash HMAC-SHA256 do telefone usando a SECRET_KEY compartilhada

### Gerar Hash (Desenvolvimento)

```bash
# Gerar hash para um telefone específico
curl http://localhost:8001/whatsapp/generate-hash/55996852212
```

Resposta:
```json
{
  "telefone": "55996852212",
  "hash": "abc123def456...",
  "info": "Use este hash nas requisições WhatsApp para autenticação"
}
```

---

## 📦 1. Criar Produto via WhatsApp

**Endpoint:** `POST /whatsapp/create-product`

### Exemplo Básico

```bash
curl -X POST http://localhost:8001/whatsapp/create-product \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "name": "Laranja",
    "description": "Laranjas frescas e suculentas",
    "variedade_cultivar": "Pera Rio"
  }'
```

### Resposta de Sucesso

```json
{
  "success": true,
  "message": "Product 'Laranja' created successfully via WhatsApp",
  "product_id": 5,
  "product_name": "Laranja",
  "qrcode_url": "/qrcode/abc123"
}
```

### Exemplo com Produto Duplicado

```json
{
  "success": false,
  "message": "Product 'Laranja' already exists in your account",
  "product_id": 5,
  "product_name": "Laranja"
}
```

---

## ✏️ 2. Editar Produto via WhatsApp

**Endpoint:** `PUT /whatsapp/update-product`

### Exemplo: Atualizar Nome e Descrição

```bash
curl -X PUT http://localhost:8001/whatsapp/update-product \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "product_id": 5,
    "name": "Laranja Orgânica",
    "description": "Laranjas 100% orgânicas certificadas"
  }'
```

### Exemplo: Atualizar Apenas Status

```bash
curl -X PUT http://localhost:8001/whatsapp/update-product \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "product_id": 5,
    "status": false
  }'
```

### Exemplo: Atualizar Múltiplos Campos

```bash
curl -X PUT http://localhost:8001/whatsapp/update-product \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "product_id": 5,
    "name": "Laranja Premium",
    "comertial_name": "Laranja Selecionada",
    "description": "Seleção especial de laranjas premium",
    "variedade_cultivar": "Valência Late",
    "status": true
  }'
```

### Resposta de Sucesso

```json
{
  "success": true,
  "message": "Product 'Laranja Premium' updated successfully via WhatsApp",
  "product_id": 5,
  "product_name": "Laranja Premium"
}
```

### Possíveis Erros

**Produto não encontrado:**
```json
{
  "detail": "Product with ID 999 not found"
}
```

**Produto não pertence ao usuário:**
```json
{
  "detail": "You don't have permission to edit this product"
}
```

---

## 📊 3. Criar Lote via WhatsApp

**Endpoint:** `POST /whatsapp/create-batch`

### Exemplo Completo

```bash
curl -X POST http://localhost:8001/whatsapp/create-batch \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "product_id": 5,
    "talhao": "A1",
    "dt_plantio": "2025-01-15",
    "dt_colheita": "2025-04-20",
    "producao": 500,
    "unidadeMedida": "kg"
  }'
```

### Exemplo Básico (Apenas Campos Obrigatórios)

```bash
curl -X POST http://localhost:8001/whatsapp/create-batch \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "product_id": 5
  }'
```

### Exemplo: Lote com Talhão

```bash
curl -X POST http://localhost:8001/whatsapp/create-batch \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "product_id": 5,
    "talhao": "Setor Norte - Talhão B3"
  }'
```

### Exemplo: Lote com Produção

```bash
curl -X POST http://localhost:8001/whatsapp/create-batch \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "SEU_HASH_AQUI",
    "product_id": 5,
    "producao": 1200,
    "unidadeMedida": "kg"
  }'
```

### Resposta de Sucesso

```json
{
  "success": true,
  "message": "Batch 'LOTE-abc123-xyz789' created successfully for product 'Laranja'",
  "batch_id": 15,
  "batch_code": "LOTE-abc123-xyz789",
  "product_name": "Laranja",
  "qrcode_url": "/qrcode/def456"
}
```

### Possíveis Erros

**Produto não encontrado:**
```json
{
  "detail": "Product with ID 999 not found"
}
```

**Produto não pertence ao usuário:**
```json
{
  "detail": "You don't have permission to create batches for this product"
}
```

**Formato de data inválido:**
```json
{
  "detail": "Invalid dt_plantio format. Use YYYY-MM-DD"
}
```

---

## 🔄 Fluxo Completo de Uso

### 1. Criar Produto
```bash
# Passo 1: Obter hash
HASH=$(curl -s http://localhost:8001/whatsapp/generate-hash/55996852212 | jq -r '.hash')

# Passo 2: Criar produto
PRODUCT_RESPONSE=$(curl -s -X POST http://localhost:8001/whatsapp/create-product \
  -H "Content-Type: application/json" \
  -d "{
    \"telefone\": \"55996852212\",
    \"hash\": \"$HASH\",
    \"name\": \"Tomate Cereja\",
    \"description\": \"Tomates cereja orgânicos\",
    \"variedade_cultivar\": \"Sweet Million\"
  }")

# Passo 3: Extrair ID do produto
PRODUCT_ID=$(echo $PRODUCT_RESPONSE | jq -r '.product_id')
echo "Produto criado com ID: $PRODUCT_ID"
```

### 2. Criar Lote para o Produto
```bash
# Criar lote usando o ID do produto
curl -X POST http://localhost:8001/whatsapp/create-batch \
  -H "Content-Type: application/json" \
  -d "{
    \"telefone\": \"55996852212\",
    \"hash\": \"$HASH\",
    \"product_id\": $PRODUCT_ID,
    \"talhao\": \"Estufa 2\",
    \"dt_plantio\": \"2025-11-01\",
    \"dt_colheita\": \"2025-12-15\",
    \"producao\": 300,
    \"unidadeMedida\": \"kg\"
  }"
```

### 3. Atualizar Produto
```bash
# Atualizar descrição do produto
curl -X PUT http://localhost:8001/whatsapp/update-product \
  -H "Content-Type: application/json" \
  -d "{
    \"telefone\": \"55996852212\",
    \"hash\": \"$HASH\",
    \"product_id\": $PRODUCT_ID,
    \"description\": \"Tomates cereja orgânicos certificados - Safra 2025\"
  }"
```

---

## 📱 Integração com Bot do WhatsApp

### Exemplo de Processamento de Mensagens

```javascript
// Bot WhatsApp recebe mensagem do usuário
const message = "Criar lote: produto 5, talhão A1, plantio 2025-11-15, produção 500kg";

// Parser processa a mensagem
const parsed = parseMessage(message);
// {
//   action: 'create-batch',
//   product_id: 5,
//   talhao: 'A1',
//   dt_plantio: '2025-11-15',
//   producao: 500,
//   unidadeMedida: 'kg'
// }

// Bot gera hash e chama API
const hash = generateHash(userPhone, SECRET_KEY);
const response = await fetch('http://api/whatsapp/create-batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    telefone: userPhone,
    hash: hash,
    ...parsed
  })
});

// Bot envia resposta ao usuário
const result = await response.json();
bot.sendMessage(userPhone, result.message);
```

---

## 🧪 Testes com Python

```python
import requests
import hmac
import hashlib

# Configuração
BASE_URL = "http://localhost:8001"
SECRET_KEY = "sua-secret-key-aqui"
PHONE = "55996852212"

def generate_hash(data: str) -> str:
    """Gera hash HMAC-SHA256"""
    return hmac.new(
        SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

# 1. Criar produto
def create_product():
    hash_value = generate_hash(PHONE)
    response = requests.post(
        f"{BASE_URL}/whatsapp/create-product",
        json={
            "telefone": PHONE,
            "hash": hash_value,
            "name": "Manga",
            "description": "Mangas premium",
            "variedade_cultivar": "Tommy Atkins"
        }
    )
    return response.json()

# 2. Editar produto
def update_product(product_id: int):
    hash_value = generate_hash(PHONE)
    response = requests.put(
        f"{BASE_URL}/whatsapp/update-product",
        json={
            "telefone": PHONE,
            "hash": hash_value,
            "product_id": product_id,
            "description": "Mangas premium exportação"
        }
    )
    return response.json()

# 3. Criar lote
def create_batch(product_id: int):
    hash_value = generate_hash(PHONE)
    response = requests.post(
        f"{BASE_URL}/whatsapp/create-batch",
        json={
            "telefone": PHONE,
            "hash": hash_value,
            "product_id": product_id,
            "talhao": "Quadra 5",
            "dt_plantio": "2025-08-10",
            "dt_colheita": "2025-11-20",
            "producao": 800,
            "unidadeMedida": "kg"
        }
    )
    return response.json()

# Executar testes
if __name__ == "__main__":
    print("1. Criando produto...")
    product = create_product()
    print(product)
    
    if product.get("success"):
        product_id = product["product_id"]
        
        print(f"\n2. Editando produto {product_id}...")
        updated = update_product(product_id)
        print(updated)
        
        print(f"\n3. Criando lote para produto {product_id}...")
        batch = create_batch(product_id)
        print(batch)
```

---

## 📋 Resumo das Rotas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/whatsapp/create-product` | Criar novo produto |
| PUT | `/whatsapp/update-product` | Editar produto existente |
| POST | `/whatsapp/create-batch` | Criar novo lote |
| POST | `/whatsapp/verify-phone` | Verificar se telefone existe |
| GET | `/whatsapp/phones` | Listar telefones cadastrados |
| GET | `/whatsapp/generate-hash/{telefone}` | Gerar hash (DEV) |

---

## 🔒 Segurança

- ✅ Todas as rotas validam hash HMAC-SHA256
- ✅ Verificação de propriedade (usuário só edita seus recursos)
- ✅ Validação de dados de entrada com Pydantic
- ✅ Códigos únicos gerados automaticamente
- ✅ Proteção contra SQL injection via ORM

---

## 📝 Notas

1. **Datas:** Use formato ISO `YYYY-MM-DD`
2. **Unidades de Medida:** Exemplos: `kg`, `ton`, `sc` (sacas), `cx` (caixas)
3. **Códigos:** Gerados automaticamente no formato `LOTE-{CODIGO_PRODUTO}-{RANDOM}`
4. **QR Codes:** Gerados automaticamente para produtos e lotes
5. **Partial Updates:** Ao editar produto, apenas campos fornecidos são atualizados
