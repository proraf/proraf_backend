# 📦 Listar Produtos do Usuário via WhatsApp

## 🎯 Endpoint

**POST** `/whatsapp/list-products`

## 📝 Descrição

Retorna lista completa de todos os produtos cadastrados pelo usuário autenticado via WhatsApp.

## 🔐 Autenticação

Requer:
- `telefone`: Número de telefone do usuário
- `hash`: Hash HMAC-SHA256 do telefone

## 📊 Resposta

### Estrutura

```json
{
  "success": true,
  "message": "Você possui 5 produto(s) cadastrado(s)",
  "total_products": 5,
  "active_products": 4,
  "inactive_products": 1,
  "products": [
    {
      "id": 1,
      "name": "Laranja",
      "comertial_name": "Laranja Premium",
      "description": "Laranjas orgânicas certificadas",
      "variedade_cultivar": "Pera Rio",
      "status": true,
      "code": "ABC123XYZ",
      "batches_count": 3
    }
  ]
}
```

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `success` | boolean | Indica se a operação foi bem-sucedida |
| `message` | string | Mensagem descritiva |
| `total_products` | integer | Total de produtos cadastrados |
| `active_products` | integer | Quantidade de produtos ativos |
| `inactive_products` | integer | Quantidade de produtos inativos |
| `products` | array | Lista de produtos com detalhes |

### Produto

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | integer | ID único do produto |
| `name` | string | Nome do produto |
| `comertial_name` | string | Nome comercial (opcional) |
| `description` | string | Descrição detalhada (opcional) |
| `variedade_cultivar` | string | Variedade ou cultivar (opcional) |
| `status` | boolean | true = ativo, false = inativo |
| `code` | string | Código único do produto |
| `batches_count` | integer | Quantidade de lotes cadastrados |

## 📥 Exemplos de Requisição

### cURL

```bash
# 1. Obter hash
HASH=$(curl -s http://localhost:8001/whatsapp/generate-hash/55996852212 | jq -r '.hash')

# 2. Listar produtos
curl -X POST http://localhost:8001/whatsapp/list-products \
  -H "Content-Type: application/json" \
  -d "{
    \"telefone\": \"55996852212\",
    \"hash\": \"$HASH\"
  }"
```

### Python

```python
import requests
import hmac
import hashlib

BASE_URL = "http://localhost:8001"
SECRET_KEY = "sua-secret-key"
PHONE = "55996852212"

def generate_hash(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

# Listar produtos
hash_value = generate_hash(PHONE)
response = requests.post(
    f"{BASE_URL}/whatsapp/list-products",
    json={
        "telefone": PHONE,
        "hash": hash_value
    }
)

products = response.json()
print(f"Total: {products['total_products']}")
for product in products['products']:
    print(f"- {product['name']} (ID: {product['id']})")
```

### JavaScript

```javascript
async function listProducts(phone) {
  const hash = generateHash(phone, SECRET_KEY);
  
  const response = await fetch('http://localhost:8001/whatsapp/list-products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      telefone: phone,
      hash: hash
    })
  });
  
  const data = await response.json();
  return data.products;
}
```

## 📤 Exemplos de Resposta

### Com Produtos

```json
{
  "success": true,
  "message": "Você possui 3 produto(s) cadastrado(s)",
  "total_products": 3,
  "active_products": 2,
  "inactive_products": 1,
  "products": [
    {
      "id": 5,
      "name": "Abacaxi",
      "comertial_name": "Abacaxi Premium",
      "description": "Abacaxi pérola da melhor qualidade",
      "variedade_cultivar": "Pérola",
      "status": true,
      "code": "P5K8L2M9",
      "batches_count": 2
    },
    {
      "id": 3,
      "name": "Laranja",
      "comertial_name": "Laranja Orgânica",
      "description": "Laranjas 100% orgânicas certificadas",
      "variedade_cultivar": "Pera Rio",
      "status": true,
      "code": "ABC123XY",
      "batches_count": 5
    },
    {
      "id": 7,
      "name": "Manga",
      "comertial_name": null,
      "description": "Manga rosa premium",
      "variedade_cultivar": "Rosa",
      "status": false,
      "code": "M7N8O9P0",
      "batches_count": 0
    }
  ]
}
```

### Sem Produtos

```json
{
  "success": true,
  "message": "Você ainda não possui produtos cadastrados",
  "total_products": 0,
  "active_products": 0,
  "inactive_products": 0,
  "products": []
}
```

## 💬 Integração com Bot WhatsApp

### Processamento de Mensagem

```javascript
// Bot recebe mensagem do usuário
const userMessage = message.body.toLowerCase();

if (userMessage.includes('meus produtos') || 
    userMessage.includes('listar produtos') ||
    userMessage.includes('ver produtos')) {
    
    // Chama API
    const hash = generateHash(userPhone, SECRET_KEY);
    const response = await fetch('http://api/whatsapp/list-products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            telefone: userPhone,
            hash: hash
        })
    });
    
    const data = await response.json();
    
    // Formata mensagem para WhatsApp
    let reply = `*📦 Seus Produtos (${data.total_products})*\n\n`;
    reply += `✅ Ativos: ${data.active_products} | `;
    reply += `❌ Inativos: ${data.inactive_products}\n\n`;
    
    if (data.products.length > 0) {
        data.products.forEach((product, index) => {
            const status = product.status ? '✅' : '❌';
            reply += `${index + 1}. ${status} *${product.name}*\n`;
            reply += `   ID: ${product.id} | Código: ${product.code}\n`;
            if (product.variedade_cultivar) {
                reply += `   Variedade: ${product.variedade_cultivar}\n`;
            }
            reply += `   Lotes: ${product.batches_count}\n\n`;
        });
        reply += `_Digite o ID para detalhes ou 'criar lote [ID]'_`;
    } else {
        reply += `Você ainda não tem produtos cadastrados.\n`;
        reply += `Digite "criar produto [nome]" para cadastrar.`;
    }
    
    // Envia resposta
    await client.sendMessage(userPhone, reply);
}
```

### Exemplo de Conversa

```
👤 Usuário: Meus produtos

🤖 Bot:
📦 Seus Produtos (3)

✅ Ativos: 2 | ❌ Inativos: 1

1. ✅ Abacaxi
   ID: 5 | Código: P5K8L2M9
   Variedade: Pérola
   Lotes: 2

2. ✅ Laranja
   ID: 3 | Código: ABC123XY
   Variedade: Pera Rio
   Lotes: 5

3. ❌ Manga
   ID: 7 | Código: M7N8O9P0
   Variedade: Rosa
   Lotes: 0

Digite o ID para detalhes ou 'criar lote [ID]'

---

👤 Usuário: criar lote 3

🤖 Bot: Certo! Vou criar um lote para Laranja.
Digite as informações ou envie "continuar" para pular:
Talhão: [digite ou 'pular']
```

## 🎯 Casos de Uso

### 1. **Consultar antes de criar lote**
```
Usuário: "listar produtos"
Bot: Mostra todos produtos com IDs
Usuário: "criar lote para produto 5"
```

### 2. **Verificar status dos produtos**
```
Usuário: "meus produtos"
Bot: Lista com indicador ✅/❌ de status
```

### 3. **Obter ID para operações**
```
Usuário: "editar produto"
Bot: "Qual produto? Digite 'listar' para ver todos"
Usuário: "listar"
Bot: Mostra produtos com IDs
Usuário: "editar produto 3"
```

### 4. **Visualizar quantidade de lotes**
```
Usuário: "quais produtos têm mais lotes?"
Bot: Lista ordenada por quantidade de lotes
```

## 📱 Formatação para WhatsApp

### Básica

```
📦 Seus Produtos (3)
✅ Ativos: 2 | ❌ Inativos: 1

1. ✅ Abacaxi (ID: 5)
   Lotes: 2

2. ✅ Laranja (ID: 3)
   Lotes: 5

3. ❌ Manga (ID: 7)
   Lotes: 0
```

### Detalhada

```
📦 SEUS PRODUTOS

Total: 3 produtos
Status: ✅ 2 ativos | ❌ 1 inativo

━━━━━━━━━━━━━━━━━━━━━━

1️⃣ ✅ *Abacaxi*
   • ID: 5
   • Código: P5K8L2M9
   • Variedade: Pérola
   • Lotes: 2 cadastrados

2️⃣ ✅ *Laranja*
   • ID: 3
   • Código: ABC123XY
   • Variedade: Pera Rio
   • Lotes: 5 cadastrados

3️⃣ ❌ *Manga* (inativo)
   • ID: 7
   • Código: M7N8O9P0
   • Variedade: Rosa
   • Lotes: 0 cadastrados

━━━━━━━━━━━━━━━━━━━━━━

💡 Comandos disponíveis:
• "criar lote [ID]"
• "editar produto [ID]"
• "detalhes produto [ID]"
```

### Compacta

```
📦 3 produtos (2 ✅, 1 ❌)

1. Abacaxi (ID:5) - 2 lotes
2. Laranja (ID:3) - 5 lotes
3. Manga (ID:7) - 0 lotes ❌

Digite ID para mais detalhes
```

## 🔄 Fluxo de Dados

```
Usuário WhatsApp
      ↓
"meus produtos"
      ↓
Bot WhatsApp
      ↓
Gera Hash(telefone)
      ↓
POST /whatsapp/list-products
      ↓
API ProRAF
      ↓
Autentica usuário
      ↓
Busca produtos no DB
      ↓
Conta lotes por produto
      ↓
Ordena por nome
      ↓
Retorna JSON
      ↓
Bot formata mensagem
      ↓
Envia para usuário
      ↓
"📦 Seus Produtos (3)..."
```

## 🧪 Teste

```bash
# Execute o script de teste
poetry run python test_list_products.py
```

Saída esperada:
```
🧪 Testando rota de listagem de produtos...

1️⃣  Gerando hash para telefone 55996852212...
✅ Hash gerado: 8f3d2a1b5c7e9...

2️⃣  Listando produtos do usuário...
✅ Você possui 3 produto(s) cadastrado(s)

📊 Estatísticas:
   Total de produtos: 3
   Produtos ativos: 2
   Produtos inativos: 1

📦 Lista de Produtos:
================================================================================

1. ✅ Abacaxi
   ID: 5
   Código: P5K8L2M9
   Nome Comercial: Abacaxi Premium
   Variedade: Pérola
   Descrição: Abacaxi pérola da melhor qualidade
   Lotes cadastrados: 2
   Status: Ativo
...
```

## ✅ Checklist de Implementação

- [x] Schema ProductListItem
- [x] Schema WhatsAppProductListResponse
- [x] Rota POST /whatsapp/list-products
- [x] Autenticação via hash
- [x] Contagem de lotes por produto
- [x] Contagem de produtos ativos/inativos
- [x] Ordenação alfabética
- [x] Tratamento de lista vazia
- [x] Documentação completa
- [x] Script de teste
- [x] Exemplos de formatação WhatsApp

## 🎯 Próximos Passos

1. **Filtrar produtos por status**
   - `POST /whatsapp/list-products?status=active`
   
2. **Buscar produto por nome**
   - `POST /whatsapp/search-product`
   
3. **Detalhes de produto específico**
   - `POST /whatsapp/product-details`
   
4. **Listar lotes de um produto**
   - `POST /whatsapp/list-batches`

---

**Status:** ✅ Implementado e Testado  
**Data:** 16 de novembro de 2025
