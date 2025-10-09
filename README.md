# ProRAF - Sistema de Rastreabilidade Agrícola

API REST desenvolvida em Python/FastAPI para gerenciar a rastreabilidade de produtos agrícolas.

## 🚀 Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para mapeamento objeto-relacional
- **Alembic** - Migrations de banco de dados
- **SQLite** - Banco de dados
- **Poetry** - Gerenciamento de dependências
- **PyTest** - Framework de testes
- **Factory Boy** - Geração de dados para testes
- **JWT** - Autenticação via tokens
- **Pydantic** - Validação de dados

## 📋 Pré-requisitos

- Python 3.11 ou superior
- Poetry instalado

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd proraf
```

2. Instale as dependências com Poetry:
```bash
poetry install
```

3. Ative o ambiente virtual:
```bash
poetry shell
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

**IMPORTANTE**: Edite o arquivo `.env` e altere os valores de `SECRET_KEY` e `API_KEY` para valores seguros!

5. Execute as migrations:
```bash
task migrate
```

## 🎯 Comandos Úteis (TaskAPI)

```bash
# Iniciar servidor de desenvolvimento
task dev

# Executar testes
task test

# Executar linter
task lint

# Formatar código
task format

# Criar migration
task makemigrations "nome_da_migration"

# Aplicar migrations
task migrate
```

## 🔐 Segurança

A API possui duas camadas de segurança:

1. **API Key**: Todas as requisições devem incluir o header `X-API-Key` com a chave configurada no `.env`
2. **JWT Token**: Endpoints protegidos requerem autenticação via Bearer token

### Exemplo de requisição:

```bash
# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "X-API-Key: sua-api-key" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario@example.com&password=senha123"

# Acessar endpoint protegido
curl -X GET "http://localhost:8000/products/" \
  -H "X-API-Key: sua-api-key" \
  -H "Authorization: Bearer seu-token-jwt"
```

## 📊 Estrutura do Banco de Dados

### Tabelas:

- **users** - Usuários do sistema (produtores, admin)
- **products** - Produtos agrícolas cadastrados
- **batch** - Lotes de produção
- **movements** - Movimentações de lotes
- **field_data** - Dados geográficos e de campo

## 🌐 Endpoints da API

### Autenticação
- `POST /auth/register` - Registrar novo usuário
- `POST /auth/login` - Login e obtenção de token

### Produtos
- `POST /products/` - Criar produto
- `GET /products/` - Listar produtos
- `GET /products/{id}` - Buscar produto por ID
- `PUT /products/{id}` - Atualizar produto
- `DELETE /products/{id}` - Deletar produto (soft delete)

### Lotes
- `POST /batches/` - Criar lote
- `GET /batches/` - Listar lotes
- `GET /batches/{id}` - Buscar lote por ID
- `GET /batches/code/{code}` - Buscar lote por código
- `PUT /batches/{id}` - Atualizar lote
- `DELETE /batches/{id}` - Deletar lote (soft delete)

### Health Check
- `GET /` - Status da API
- `GET /health` - Verificação de saúde

## 📚 Documentação Interativa

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testes

Execute os testes com cobertura:

```bash
task test
```

Os testes incluem:
- Autenticação e autorização
- CRUD de produtos
- CRUD de lotes
- Validações de dados
- Testes de segurança

## 🔄 Migrations

Para criar uma nova migration após modificar os models:

```bash
task makemigrations "descricao_da_mudanca"
task migrate
```

## 🐳 Docker (Futuro)

A estrutura está preparada para Docker. Os Dockerfiles serão adicionados nas próximas versões:
- `Dockerfile.dev` - Para desenvolvimento
- `Dockerfile.prod` - Para produção
- `docker-compose.yml` - Orquestração de containers

## 🔒 Perfis de Usuário

- **user** (padrão) - Acesso aos próprios lotes e produtos
- **admin** - Acesso total ao sistema

## 📝 Tipos de Pessoa

- **F** - Pessoa Física (requer CPF)
- **J** - Pessoa Jurídica (requer CNPJ)

## 🌱 Fluxo de Rastreabilidade

1. Cadastro de **Produto** (ex: Tomate Cereja)
2. Criação de **Lote** vinculado ao produto
3. Geração automática de **QR Code** para o lote
4. Registro de **Movimentações** (plantio, colheita, expedição)
5. Armazenamento de **Dados de Campo** (localização, imagens)

## 📱 Integração Frontend

Configure a URL do frontend no `.env`:

```env
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

O frontend deve incluir nas requisições:
- Header `X-API-Key` com a API Key
- Header `Authorization: Bearer {token}` após login

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👥 Autores

- Desenvolvimento inicial - [Seu Nome]

## 📞 Suporte

Para suporte, envie um email para suporte@proraf.com ou abra uma issue no repositório.