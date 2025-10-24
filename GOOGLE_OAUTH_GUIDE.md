# Google OAuth2 Integration - Guia Completo

## 🔐 Configuração Realizada

### 1. Dependências Instaladas
- `google-auth`: Autenticação Google
- `google-auth-oauthlib`: OAuth2 flow
- `google-auth-httplib2`: HTTP transport

### 2. Estrutura Implementada

#### Arquivos Criados/Modificados:
- `proraf/oauth2_config.py`: Configuração OAuth2
- `proraf/services/google_oauth_service.py`: Serviços Google
- `proraf/routers/google_auth.py`: Endpoints OAuth
- `proraf/models/user.py`: Campos Google adicionados
- `proraf/schemas/user.py`: Schemas atualizados

#### Campos Adicionados ao User:
- `google_id`: ID único do usuário no Google
- `avatar_url`: URL da foto do perfil
- `provider`: 'local' ou 'google'
- `senha`: Agora opcional (nullable)

## 🚀 Endpoints Disponíveis

### 1. `/auth/google/login` (GET)
**Inicia o fluxo OAuth2**
```json
Response:
{
    "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
    "state": "random_state_string"
}
```

### 2. `/auth/google/callback` (GET)
**Processa callback do Google**
```
Query Parameters:
- code: Authorization code
- state: State validation

Response:
{
    "access_token": "jwt_token_here",
    "token_type": "bearer", 
    "user": {UserResponse}
}
```

### 3. `/auth/google/verify-token` (POST)
**Verifica Google ID Token (para SPAs)**
```json
Request:
{
    "id_token": "google_id_token_here"
}

Response:
{
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {UserResponse}
}
```

## 📱 Fluxos de Autenticação

### Fluxo 1: Web Application (Backend)
1. Frontend chama `GET /auth/google/login`
2. Backend retorna URL de autorização
3. Frontend redireciona usuário para URL do Google
4. Usuário autoriza no Google
5. Google redireciona para `/auth/google/callback`
6. Backend processa e retorna JWT token
7. Frontend usa JWT token para requests

### Fluxo 2: SPA/Mobile (Frontend)
1. Frontend usa Google JS SDK para obter ID token
2. Frontend envia ID token para `POST /auth/google/verify-token`
3. Backend valida token e retorna JWT
4. Frontend usa JWT token para requests

## ⚙️ Configuração Google Cloud

### 1. Configurado no Console:
- **Project ID**: `proraf-475919`
- **Client ID**: `149795163999-vd3lf5uf5u0od7i2msjj0pkp3nlfm217.apps.googleusercontent.com`
- **Redirect URI**: `http://localhost:8000/auth/google/callback`

### 2. APIs Habilitadas:
- Google Identity API
- Google+ API (People API)

### 3. Scopes Solicitados:
- `openid`: Identificação básica
- `userinfo.email`: Email do usuário
- `userinfo.profile`: Nome e foto do perfil

## 🔄 Lógica de Usuários

### Cenários Tratados:

1. **Novo usuário Google**: Cria conta automaticamente
2. **Usuário Google existente**: Autentica normalmente
3. **Conta local existente + Google**: Vincula contas pelo email
4. **Atualização de dados**: Atualiza avatar automaticamente

### Campos Padrão para Usuários Google:
- `tipo_pessoa`: 'F' (Pessoa Física)
- `tipo_perfil`: 'user'
- `senha`: null (não usa senha)
- `provider`: 'google'

## 🧪 Como Testar

### 1. Teste Manual via Swagger:
```
1. Acesse: http://localhost:8000/docs
2. Abra endpoint: GET /auth/google/login
3. Execute para obter URL de autorização
4. Abra URL no navegador
5. Autorize com sua conta Google
6. Será redirecionado com código
7. Use código no endpoint callback
```

### 2. Teste Direto:
```bash
# 1. Obter URL de autorização
curl -X GET "http://localhost:8000/auth/google/login"

# 2. Abrir URL no navegador e autorizar

# 3. Usar código retornado
curl -X GET "http://localhost:8000/auth/google/callback?code=YOUR_CODE&state=YOUR_STATE"
```

### 3. Teste com ID Token (SPA):
```javascript
// Frontend JavaScript
const idToken = googleUser.getAuthResponse().id_token;

fetch('/auth/google/verify-token', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id_token: idToken})
});
```

## 🚨 Pontos Importantes

### Segurança:
- ✅ State parameter para CSRF protection
- ✅ Token verification via Google
- ✅ JWT token generation
- ✅ Unique constraints (google_id, email)

### Produção:
- 🔧 **Alterar redirect_uri** para domínio de produção
- 🔧 **Usar Redis** para oauth_states em vez de memória
- 🔧 **Configurar HTTPS** obrigatório
- 🔧 **Validar origins** no Google Console

### Limitações Atuais:
- State storage em memória (não persiste restart)
- Redirect URI fixo (localhost:8000)
- Scopes básicos (pode adicionar mais se necessário)

## ✅ Status da Implementação

- ✅ Google OAuth2 flow completo
- ✅ User creation/linking
- ✅ JWT token generation  
- ✅ Database migrations
- ✅ API endpoints
- ✅ Error handling
- ✅ Multiple authentication flows

**A integração está COMPLETA e pronta para uso!** 🎉