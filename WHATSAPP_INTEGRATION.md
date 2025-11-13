# Integração WhatsApp - ProRAF API

## 📱 Visão Geral

A API ProRAF agora suporta integração direta com WhatsApp, permitindo que usuários realizem operações sem login tradicional (usuário/senha). A autenticação é feita através de:

1. **Número de telefone** cadastrado no sistema
2. **Hash compartilhado** (HMAC-SHA256) usando a mesma `SECRET_KEY`

## 🔐 Autenticação

### Como Funciona

A autenticação WhatsApp usa **HMAC-SHA256** para gerar um hash seguro:

```python
hash = HMAC-SHA256(telefone, SECRET_KEY)
```

### Gerando Hash

Use o endpoint de desenvolvimento para gerar hashes:

```bash
GET /whatsapp/generate-hash/{telefone}
```

**Exemplo:**
```bash
curl http://localhost:8000/whatsapp/generate-hash/55996852212
```

**Resposta:**
```json
{
  "telefone": "55996852212",
  "hash": "e5a6689160dcdf4072e85e21195a5d5f07d58bce2a069e6513eebb5e0be7c1d2",
  "info": "Use este hash nas requisições WhatsApp para autenticação"
}
```

## 📋 Endpoints Disponíveis

### 1. Listar Telefones Cadastrados

**Endpoint:** `GET /whatsapp/phones?hash={hash}`

**Descrição:** Retorna lista de todos os telefones cadastrados no sistema.

**Uso:** API do WhatsApp verifica se usuário já possui conta antes de iniciar interação.

**Hash necessário:** Gerar com identificador `PHONE_LIST`

```bash
# Gerar hash para listagem
GET /whatsapp/list-hash

# Usar hash na requisição
GET /whatsapp/phones?hash=98d1de7f3cd7be4f57243d3938dc683003e044f366eccdefcc2836ffcba85783
```

**Resposta:**
```json
[
  "55996852212",
  "55998765432",
  "55991234567"
]
```

---

### 2. Verificar se Telefone Existe

**Endpoint:** `POST /whatsapp/verify-phone`

**Descrição:** Verifica se telefone está cadastrado e retorna dados básicos do usuário.

**Request Body:**
```json
{
  "telefone": "55996852212",
  "hash": "e5a6689160dcdf4072e85e21195a5d5f07d58bce2a069e6513eebb5e0be7c1d2"
}
```

**Resposta - Telefone Existe:**
```json
{
  "exists": true,
  "user_id": 1,
  "nome": "Rafael Nogueira",
  "email": "rafael@exemplo.com",
  "tipo_pessoa": "F"
}
```

**Resposta - Telefone Não Existe:**
```json
{
  "exists": false,
  "user_id": null,
  "nome": null,
  "email": null,
  "tipo_pessoa": null
}
```

---

### 3. Criar Produto via WhatsApp

**Endpoint:** `POST /whatsapp/create-product`

**Descrição:** Cria novo produto para usuário autenticado via telefone (sem login tradicional).

**Request Body:**
```json
{
  "telefone": "55996852212",
  "hash": "e5a6689160dcdf4072e85e21195a5d5f07d58bce2a069e6513eebb5e0be7c1d2",
  "name": "Laranja",
  "description": "Laranja Lima orgânica",
  "variedade_cultivar": "Lima"
}
```

**Resposta - Sucesso:**
```json
{
  "success": true,
  "message": "Product 'Laranja' created successfully via WhatsApp",
  "product_id": 42,
  "product_name": "Laranja",
  "qrcode_url": "/static/qrcodes/product_42.png"
}
```

**Resposta - Produto Já Existe:**
```json
{
  "success": false,
  "message": "Product 'Laranja' already exists in your account",
  "product_id": 42,
  "product_name": "Laranja",
  "qrcode_url": null
}
```

## 🔄 Fluxo de Integração WhatsApp

### Cenário 1: Novo Usuário

1. Usuário envia mensagem no WhatsApp
2. Bot WhatsApp extrai número de telefone
3. Bot chama `POST /whatsapp/verify-phone`
4. Se `exists: false`, orienta usuário a se cadastrar no sistema web
5. Se `exists: true`, procede com operações

### Cenário 2: Criar Produto

1. Usuário envia: "Registrar produto: Tomate"
2. Bot WhatsApp extrai:
   - Telefone: `55996852212`
   - Nome do produto: `Tomate`
3. Bot gera hash: `HMAC-SHA256("55996852212", SECRET_KEY)`
4. Bot chama `POST /whatsapp/create-product`:
```json
{
  "telefone": "55996852212",
  "hash": "e5a6689160dcdf4072e85e21195a5d5f...",
  "name": "Tomate",
  "description": "Tomate orgânico"
}
```
5. API cria produto e retorna QR Code
6. Bot envia confirmação ao usuário com link do QR Code

## 🛡️ Segurança

### Proteções Implementadas

1. **HMAC-SHA256**: Algoritmo criptográfico seguro
2. **SECRET_KEY compartilhada**: Apenas aplicações com a chave podem gerar hashes válidos
3. **Timing attack protection**: Usa `hmac.compare_digest()` para comparações seguras
4. **Validação em duas camadas**: 
   - Hash deve ser válido
   - Telefone deve existir no sistema

### Boas Práticas

- ⚠️ **NUNCA exponha a SECRET_KEY** em código cliente ou logs
- ✅ Gere hashes apenas no servidor da aplicação WhatsApp
- ✅ Use HTTPS em produção para todas as requisições
- ⚠️ **Remova** ou **proteja** os endpoints de desenvolvimento (`/generate-hash`, `/list-hash`) em produção

## 🧪 Testando a Integração

### Passo 1: Obter Hash para um Telefone

```bash
curl http://localhost:8000/whatsapp/generate-hash/55996852212
```

### Passo 2: Verificar Telefone

```bash
curl -X POST http://localhost:8000/whatsapp/verify-phone \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "e5a6689160dcdf4072e85e21195a5d5f07d58bce2a069e6513eebb5e0be7c1d2"
  }'
```

### Passo 3: Criar Produto

```bash
curl -X POST http://localhost:8000/whatsapp/create-product \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "55996852212",
    "hash": "e5a6689160dcdf4072e85e21195a5d5f07d58bce2a069e6513eebb5e0be7c1d2",
    "name": "Laranja",
    "description": "Laranja orgânica"
  }'
```

## 🔧 Implementação no Bot WhatsApp

### Exemplo Python (Bot WhatsApp)

```python
import hmac
import hashlib
import requests

# Configuração (deve estar no .env)
SECRET_KEY = "JDIfhk25swGJBtJzSVAz72SnZgFSlhqo"  # Mesma SECRET_KEY da API
API_URL = "http://localhost:8000"

def gerar_hash(telefone: str) -> str:
    """Gera hash HMAC-SHA256 para autenticação"""
    hash_object = hmac.new(
        SECRET_KEY.encode('utf-8'),
        telefone.encode('utf-8'),
        hashlib.sha256
    )
    return hash_object.hexdigest()

def verificar_usuario(telefone: str):
    """Verifica se usuário existe no sistema"""
    hash_auth = gerar_hash(telefone)
    
    response = requests.post(
        f"{API_URL}/whatsapp/verify-phone",
        json={
            "telefone": telefone,
            "hash": hash_auth
        }
    )
    
    return response.json()

def criar_produto(telefone: str, nome_produto: str, descricao: str = None):
    """Cria produto para usuário via WhatsApp"""
    hash_auth = gerar_hash(telefone)
    
    response = requests.post(
        f"{API_URL}/whatsapp/create-product",
        json={
            "telefone": telefone,
            "hash": hash_auth,
            "name": nome_produto,
            "description": descricao
        }
    )
    
    return response.json()

# Exemplo de uso
if __name__ == "__main__":
    telefone_usuario = "55996852212"
    
    # Verifica se usuário existe
    usuario = verificar_usuario(telefone_usuario)
    print(f"Usuário existe: {usuario['exists']}")
    
    if usuario['exists']:
        # Cria produto
        resultado = criar_produto(
            telefone_usuario,
            "Laranja",
            "Laranja Lima orgânica"
        )
        print(f"Produto criado: {resultado['success']}")
        print(f"Mensagem: {resultado['message']}")
```

## 📊 Códigos de Status HTTP

| Status | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Produto criado com sucesso |
| 401 | Hash de autenticação inválido |
| 404 | Telefone não encontrado no sistema |

## ❓ FAQ

**P: O hash é sempre o mesmo para um telefone?**  
R: Sim, desde que a SECRET_KEY não mude. O hash é determinístico.

**P: Posso reutilizar o hash?**  
R: Sim, o hash não expira. Ele é válido enquanto a SECRET_KEY permanecer a mesma.

**P: E se mudar a SECRET_KEY?**  
R: Todos os hashes anteriores se tornarão inválidos. Será necessário regerá-los.

**P: Como proteger os endpoints de desenvolvimento?**  
R: Em produção, remova ou adicione autenticação adicional aos endpoints `/generate-hash` e `/list-hash`.

**P: Posso usar esta integração para outras operações além de criar produtos?**  
R: Sim! O sistema foi projetado para ser extensível. Você pode adicionar novos endpoints seguindo o mesmo padrão de autenticação.

## 📝 Notas de Produção

Antes de colocar em produção:

- [ ] Remover ou proteger endpoints de desenvolvimento
- [ ] Configurar HTTPS
- [ ] Validar rate limiting nas rotas WhatsApp
- [ ] Implementar logging de operações via WhatsApp
- [ ] Adicionar monitoramento de uso das rotas
- [ ] Documentar SECRET_KEY no processo de deploy

---

**Implementado em:** 13/11/2025  
**Versão da API:** 0.1.0  
**Status:** ✅ Funcional e testado
