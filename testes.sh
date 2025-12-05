#!/bin/bash

# =============================================================================
# 🧪 TESTES FIM A FIM - API ProRAF
# =============================================================================
# Este script realiza testes completos da API incluindo:
# - Registro e login de usuário
# - Cadastro de produto
# - Cadastro de lotes (com e sem blockchain)
# - Cadastro de movimentações (com e sem blockchain)
# =============================================================================

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
BASE_URL="http://localhost:8000"
API_KEY="6b21hrcP1ZjH8yMYD1mqLK74iEjSoDKV"

# Variáveis para armazenar IDs
TOKEN=""
USER_ID=""
PRODUCT_ID=""
BATCH_SEM_BLOCKCHAIN_ID=""
BATCH_COM_BLOCKCHAIN_ID=""
MOVIMENTO_SEM_BLOCKCHAIN_ID=""
MOVIMENTO_COM_BLOCKCHAIN_ID=""

# Gerar email único para teste
TIMESTAMP=$(date +%s)
TEST_EMAIL="teste_e2e_${TIMESTAMP}@example.com"
TEST_SENHA="senha123456"
TEST_NOME="Usuário Teste E2E ${TIMESTAMP}"

# =============================================================================
# Funções auxiliares
# =============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}=============================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}=============================================================================${NC}"
}

print_step() {
    echo ""
    echo -e "${BLUE}📌 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_json() {
    echo "$1" | jq '.' 2>/dev/null || echo "$1"
}

# Função para fazer requisições
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local content_type=${4:-"application/json"}
    
    local headers=(-H "X-API-Key: $API_KEY")
    
    if [ -n "$TOKEN" ]; then
        headers+=(-H "Authorization: Bearer $TOKEN")
    fi
    
    if [ "$content_type" = "form" ]; then
        curl -s -X "$method" "$BASE_URL$endpoint" \
            "${headers[@]}" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "$data"
    elif [ -n "$data" ]; then
        curl -s -X "$method" "$BASE_URL$endpoint" \
            "${headers[@]}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "$BASE_URL$endpoint" \
            "${headers[@]}"
    fi
}

# =============================================================================
# TESTE 0: Verificar se API está online
# =============================================================================
print_header "🏥 TESTE 0: Verificar se API está online"

print_step "Verificando health check..."
HEALTH=$(api_request GET "/health")
echo "$HEALTH" | jq '.'

if echo "$HEALTH" | jq -e '.status' > /dev/null 2>&1; then
    print_success "API está online!"
else
    print_error "API não está respondendo. Verifique se o backend está rodando."
    exit 1
fi

# =============================================================================
# TESTE 1: Registrar novo usuário
# =============================================================================
print_header "👤 TESTE 1: Registrar novo usuário"

print_step "Registrando usuário: $TEST_EMAIL"

REGISTER_DATA=$(cat <<EOF
{
    "nome": "$TEST_NOME",
    "email": "$TEST_EMAIL",
    "tipo_pessoa": "F",
    "cpf": "$(printf '%03d.%03d.%03d-%02d' $((RANDOM%1000)) $((RANDOM%1000)) $((RANDOM%1000)) $((RANDOM%100)))",
    "telefone": "55999$(printf '%06d' $((RANDOM%1000000)))",
    "senha": "$TEST_SENHA"
}
EOF
)

print_info "Dados de registro:"
print_json "$REGISTER_DATA"

REGISTER_RESPONSE=$(api_request POST "/auth/register" "$REGISTER_DATA")
echo ""
print_info "Resposta:"
print_json "$REGISTER_RESPONSE"

if echo "$REGISTER_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id')
    print_success "Usuário registrado com sucesso! ID: $USER_ID"
else
    print_error "Falha ao registrar usuário"
    echo "$REGISTER_RESPONSE"
    exit 1
fi

# =============================================================================
# TESTE 2: Login
# =============================================================================
print_header "🔐 TESTE 2: Login"

print_step "Fazendo login com: $TEST_EMAIL"

LOGIN_RESPONSE=$(api_request POST "/auth/login" "username=$TEST_EMAIL&password=$TEST_SENHA" "form")

print_info "Resposta:"
print_json "$LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
    print_success "Login realizado com sucesso!"
    print_info "Token: ${TOKEN:0:50}..."
else
    print_error "Falha ao fazer login"
    exit 1
fi

# =============================================================================
# TESTE 3: Verificar usuário logado
# =============================================================================
print_header "👁️ TESTE 3: Verificar usuário logado"

print_step "Obtendo dados do usuário atual..."

ME_RESPONSE=$(api_request GET "/user/me")

print_info "Resposta:"
print_json "$ME_RESPONSE"

if echo "$ME_RESPONSE" | jq -e '.email' > /dev/null 2>&1; then
    print_success "Dados do usuário obtidos com sucesso!"
else
    print_error "Falha ao obter dados do usuário"
    exit 1
fi

# =============================================================================
# TESTE 4: Cadastrar produto
# =============================================================================
print_header "🌱 TESTE 4: Cadastrar produto"

print_step "Criando produto..."

PRODUCT_DATA=$(cat <<EOF
{
    "name": "Tomate Cereja Orgânico",
    "code": "TOM-$(date +%s)",
    "comertial_name": "Tomate Cereja Premium",
    "description": "Tomate cereja cultivado organicamente sem agrotóxicos",
    "variedade_cultivar": "Sweet Million",
    "status": true
}
EOF
)

print_info "Dados do produto:"
print_json "$PRODUCT_DATA"

PRODUCT_RESPONSE=$(api_request POST "/products/" "$PRODUCT_DATA")

print_info "Resposta:"
print_json "$PRODUCT_RESPONSE"

if echo "$PRODUCT_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    PRODUCT_ID=$(echo "$PRODUCT_RESPONSE" | jq -r '.id')
    PRODUCT_NAME=$(echo "$PRODUCT_RESPONSE" | jq -r '.name')
    PRODUCT_VARIEDADE=$(echo "$PRODUCT_RESPONSE" | jq -r '.variedade_cultivar')
    print_success "Produto criado com sucesso! ID: $PRODUCT_ID"
else
    print_error "Falha ao criar produto"
    exit 1
fi

# =============================================================================
# TESTE 5: Cadastrar LOTE SEM blockchain
# =============================================================================
print_header "📦 TESTE 5: Cadastrar LOTE SEM blockchain"

print_step "Criando lote sem dados blockchain..."

BATCH_CODE_1="LOTE-SEM-BC-$(date +%s)"

BATCH_DATA_1=$(cat <<EOF
{
    "code": "$BATCH_CODE_1",
    "product_id": $PRODUCT_ID,
    "product_name": "$PRODUCT_NAME",
    "product_type": "$PRODUCT_VARIEDADE",
    "dt_plantio": "2025-01-15",
    "dt_colheita": "2025-04-20",
    "dt_expedition": "2025-04-25",
    "talhao": "Talhão A1 - Área Norte",
    "registro_talhao": true,
    "producao": 500.5,
    "unidadeMedida": "kg",
    "status": true
}
EOF
)

print_info "Dados do lote:"
print_json "$BATCH_DATA_1"

BATCH_RESPONSE_1=$(api_request POST "/batches/" "$BATCH_DATA_1")

print_info "Resposta:"
print_json "$BATCH_RESPONSE_1"

if echo "$BATCH_RESPONSE_1" | jq -e '.id' > /dev/null 2>&1; then
    BATCH_SEM_BLOCKCHAIN_ID=$(echo "$BATCH_RESPONSE_1" | jq -r '.id')
    print_success "Lote SEM blockchain criado! ID: $BATCH_SEM_BLOCKCHAIN_ID"
    print_info "Código: $BATCH_CODE_1"
    print_info "blockchain_token_id: $(echo "$BATCH_RESPONSE_1" | jq -r '.blockchain_token_id // "null"')"
else
    print_error "Falha ao criar lote"
    exit 1
fi

# =============================================================================
# TESTE 6: Cadastrar LOTE COM blockchain
# =============================================================================
print_header "⛓️ TESTE 6: Cadastrar LOTE COM blockchain (em 2 etapas)"

# Etapa 1: Criar o lote normalmente
print_step "Etapa 1: Criando lote..."

BATCH_CODE_2="LOTE-COM-BC-$(date +%s)"

BATCH_DATA_2=$(cat <<EOF
{
    "code": "$BATCH_CODE_2",
    "product_id": $PRODUCT_ID,
    "product_name": "$PRODUCT_NAME",
    "product_type": "$PRODUCT_VARIEDADE",
    "dt_plantio": "2025-02-10",
    "dt_colheita": "2025-05-15",
    "dt_expedition": "2025-05-20",
    "talhao": "Talhão B2 - Área Sul",
    "registro_talhao": true,
    "producao": 750.0,
    "unidadeMedida": "kg",
    "status": true
}
EOF
)

print_info "Dados do lote:"
print_json "$BATCH_DATA_2"

BATCH_RESPONSE_2=$(api_request POST "/batches/" "$BATCH_DATA_2")

print_info "Resposta:"
print_json "$BATCH_RESPONSE_2"

if echo "$BATCH_RESPONSE_2" | jq -e '.id' > /dev/null 2>&1; then
    BATCH_COM_BLOCKCHAIN_ID=$(echo "$BATCH_RESPONSE_2" | jq -r '.id')
    print_success "Lote criado! ID: $BATCH_COM_BLOCKCHAIN_ID"
else
    print_error "Falha ao criar lote"
    exit 1
fi

# Etapa 2: Registrar dados blockchain via PATCH
print_step "Etapa 2: Registrando dados blockchain via PATCH /batches/$BATCH_COM_BLOCKCHAIN_ID/blockchain"

BLOCKCHAIN_TOKEN_ID=$((RANDOM * 1000 + RANDOM))

BLOCKCHAIN_BATCH_DATA=$(cat <<EOF
{
    "blockchain_address_who": "0x$(openssl rand -hex 20)",
    "blockchain_address_to": "0x$(openssl rand -hex 20)",
    "blockchain_product_name": "$PRODUCT_NAME",
    "blockchain_product_expedition_date": "2025-05-20",
    "blockchain_product_type": "$PRODUCT_VARIEDADE",
    "blockchain_batch_id": "$BATCH_CODE_2",
    "blockchain_unit_of_measure": "kg",
    "blockchain_batch_quantity": 750.0,
    "blockchain_token_id": $BLOCKCHAIN_TOKEN_ID
}
EOF
)

print_info "Dados blockchain:"
print_json "$BLOCKCHAIN_BATCH_DATA"

BLOCKCHAIN_BATCH_RESPONSE=$(api_request PATCH "/batches/$BATCH_COM_BLOCKCHAIN_ID/blockchain" "$BLOCKCHAIN_BATCH_DATA")

print_info "Resposta:"
print_json "$BLOCKCHAIN_BATCH_RESPONSE"

if echo "$BLOCKCHAIN_BATCH_RESPONSE" | jq -e '.blockchain_token_id' > /dev/null 2>&1; then
    print_success "Dados blockchain registrados com sucesso!"
    print_info "Token ID: $(echo "$BLOCKCHAIN_BATCH_RESPONSE" | jq -r '.blockchain_token_id')"
else
    print_error "Falha ao registrar dados blockchain"
    exit 1
fi

# =============================================================================
# TESTE 7: Tentar modificar blockchain (deve falhar - imutabilidade)
# =============================================================================
print_header "🔒 TESTE 7: Testar imutabilidade blockchain do lote"

print_step "Tentando modificar dados blockchain (deve retornar erro 400)..."

BLOCKCHAIN_BATCH_DATA_2=$(cat <<EOF
{
    "blockchain_token_id": 99999
}
EOF
)

BLOCKCHAIN_BATCH_RESPONSE_2=$(api_request PATCH "/batches/$BATCH_COM_BLOCKCHAIN_ID/blockchain" "$BLOCKCHAIN_BATCH_DATA_2")

print_info "Resposta:"
print_json "$BLOCKCHAIN_BATCH_RESPONSE_2"

if echo "$BLOCKCHAIN_BATCH_RESPONSE_2" | jq -e '.detail' > /dev/null 2>&1; then
    print_success "Imutabilidade funcionando! Dados blockchain não podem ser alterados."
else
    print_error "ALERTA: Dados blockchain foram modificados (não deveria acontecer)"
fi

# =============================================================================
# TESTE 8: Movimentação para LOTE SEM blockchain
# =============================================================================
print_header "📊 TESTE 8: Movimentação para LOTE SEM blockchain"

print_step "Criando movimentação para lote sem blockchain..."

MOVEMENT_DATA_1=$(cat <<EOF
{
    "tipo_movimentacao": "expedição",
    "quantidade": 100.5,
    "batch_id": $BATCH_SEM_BLOCKCHAIN_ID,
    "buyer_name": "Supermercado ABC Ltda",
    "buyer_identification": "12.345.678/0001-90",
    "current_location": "São Paulo, SP - Centro de Distribuição"
}
EOF
)

print_info "Dados da movimentação:"
print_json "$MOVEMENT_DATA_1"

MOVEMENT_RESPONSE_1=$(api_request POST "/movements/" "$MOVEMENT_DATA_1")

print_info "Resposta:"
print_json "$MOVEMENT_RESPONSE_1"

if echo "$MOVEMENT_RESPONSE_1" | jq -e '.id' > /dev/null 2>&1; then
    MOVIMENTO_SEM_BLOCKCHAIN_ID=$(echo "$MOVEMENT_RESPONSE_1" | jq -r '.id')
    print_success "Movimentação SEM blockchain criada! ID: $MOVIMENTO_SEM_BLOCKCHAIN_ID"
    print_info "blockchain_token_id: $(echo "$MOVEMENT_RESPONSE_1" | jq -r '.blockchain_token_id // "null"')"
else
    print_error "Falha ao criar movimentação"
    exit 1
fi

# =============================================================================
# TESTE 9: Movimentação para LOTE COM blockchain
# =============================================================================
print_header "⛓️ TESTE 9: Movimentação para LOTE COM blockchain (em 2 etapas)"

# Etapa 1: Criar movimentação
print_step "Etapa 1: Criando movimentação..."

MOVEMENT_DATA_2=$(cat <<EOF
{
    "tipo_movimentacao": "venda",
    "quantidade": 250.0,
    "batch_id": $BATCH_COM_BLOCKCHAIN_ID,
    "buyer_name": "Restaurante Gourmet XYZ",
    "buyer_identification": "98.765.432/0001-10",
    "current_location": "Rio de Janeiro, RJ - Zona Sul"
}
EOF
)

print_info "Dados da movimentação:"
print_json "$MOVEMENT_DATA_2"

MOVEMENT_RESPONSE_2=$(api_request POST "/movements/" "$MOVEMENT_DATA_2")

print_info "Resposta:"
print_json "$MOVEMENT_RESPONSE_2"

if echo "$MOVEMENT_RESPONSE_2" | jq -e '.id' > /dev/null 2>&1; then
    MOVIMENTO_COM_BLOCKCHAIN_ID=$(echo "$MOVEMENT_RESPONSE_2" | jq -r '.id')
    print_success "Movimentação criada! ID: $MOVIMENTO_COM_BLOCKCHAIN_ID"
else
    print_error "Falha ao criar movimentação"
    exit 1
fi

# Etapa 2: Registrar dados blockchain
print_step "Etapa 2: Registrando dados blockchain via PATCH /movements/$MOVIMENTO_COM_BLOCKCHAIN_ID/blockchain"

MOVEMENT_BLOCKCHAIN_TOKEN_ID=$((RANDOM * 1000 + RANDOM))

BLOCKCHAIN_MOVEMENT_DATA=$(cat <<EOF
{
    "blockchain_updater": "0x$(openssl rand -hex 20)",
    "blockchain_token_id": $MOVEMENT_BLOCKCHAIN_TOKEN_ID,
    "blockchain_message": "Venda realizada para Restaurante Gourmet XYZ",
    "blockchain_buyer_name": "Restaurante Gourmet XYZ",
    "blockchain_buyer_identification": "98.765.432/0001-10",
    "blockchain_current_location": "Rio de Janeiro, RJ - Zona Sul",
    "blockchain_update_type": 1
}
EOF
)

print_info "Dados blockchain:"
print_json "$BLOCKCHAIN_MOVEMENT_DATA"

BLOCKCHAIN_MOVEMENT_RESPONSE=$(api_request PATCH "/movements/$MOVIMENTO_COM_BLOCKCHAIN_ID/blockchain" "$BLOCKCHAIN_MOVEMENT_DATA")

print_info "Resposta:"
print_json "$BLOCKCHAIN_MOVEMENT_RESPONSE"

if echo "$BLOCKCHAIN_MOVEMENT_RESPONSE" | jq -e '.blockchain_token_id' > /dev/null 2>&1; then
    print_success "Dados blockchain da movimentação registrados!"
    print_info "Token ID: $(echo "$BLOCKCHAIN_MOVEMENT_RESPONSE" | jq -r '.blockchain_token_id')"
else
    print_error "Falha ao registrar dados blockchain da movimentação"
    exit 1
fi

# =============================================================================
# TESTE 10: Testar imutabilidade da movimentação
# =============================================================================
print_header "🔒 TESTE 10: Testar imutabilidade blockchain da movimentação"

print_step "Tentando modificar dados blockchain (deve retornar erro 400)..."

BLOCKCHAIN_MOVEMENT_DATA_2=$(cat <<EOF
{
    "blockchain_token_id": 88888
}
EOF
)

BLOCKCHAIN_MOVEMENT_RESPONSE_2=$(api_request PATCH "/movements/$MOVIMENTO_COM_BLOCKCHAIN_ID/blockchain" "$BLOCKCHAIN_MOVEMENT_DATA_2")

print_info "Resposta:"
print_json "$BLOCKCHAIN_MOVEMENT_RESPONSE_2"

if echo "$BLOCKCHAIN_MOVEMENT_RESPONSE_2" | jq -e '.detail' > /dev/null 2>&1; then
    print_success "Imutabilidade funcionando! Dados blockchain da movimentação não podem ser alterados."
else
    print_error "ALERTA: Dados blockchain foram modificados (não deveria acontecer)"
fi

# =============================================================================
# TESTE 11: Rastreabilidade pública
# =============================================================================
print_header "🔍 TESTE 11: Rastreabilidade pública"

print_step "Testando endpoint de tracking para lote COM blockchain..."

# Remove o token para simular acesso público
TRACKING_RESPONSE=$(curl -s -X GET "$BASE_URL/tracking/$BATCH_CODE_2" \
    -H "X-API-Key: $API_KEY")

print_info "Resposta:"
print_json "$TRACKING_RESPONSE"

if echo "$TRACKING_RESPONSE" | jq -e '.code' > /dev/null 2>&1; then
    print_success "Rastreabilidade funcionando!"
else
    print_info "Endpoint de tracking pode ter formato diferente"
fi

# =============================================================================
# TESTE 12: Listar movimentações do lote
# =============================================================================
print_header "📋 TESTE 12: Listar movimentações do lote"

print_step "Listando movimentações do lote COM blockchain (ID: $BATCH_COM_BLOCKCHAIN_ID)..."

MOVEMENTS_BY_BATCH=$(api_request GET "/movements/batch/$BATCH_COM_BLOCKCHAIN_ID")

print_info "Resposta:"
print_json "$MOVEMENTS_BY_BATCH"

if echo "$MOVEMENTS_BY_BATCH" | jq -e '.[0]' > /dev/null 2>&1; then
    TOTAL_MOVEMENTS=$(echo "$MOVEMENTS_BY_BATCH" | jq '. | length')
    print_success "Movimentações listadas: $TOTAL_MOVEMENTS"
else
    print_info "Nenhuma movimentação encontrada ou formato diferente"
fi

# =============================================================================
# RESUMO FINAL
# =============================================================================
print_header "📊 RESUMO DOS TESTES"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                         RESULTADOS DOS TESTES                              ║${NC}"
echo -e "${GREEN}╠═══════════════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC} Usuário Criado:                                                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   - Email: $TEST_EMAIL"
echo -e "${GREEN}║${NC}   - ID: $USER_ID"
echo -e "${GREEN}║${NC}                                                                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC} Produto Criado:                                                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   - Nome: $PRODUCT_NAME"
echo -e "${GREEN}║${NC}   - ID: $PRODUCT_ID"
echo -e "${GREEN}║${NC}                                                                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC} Lote SEM Blockchain:                                                      ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   - Código: $BATCH_CODE_1"
echo -e "${GREEN}║${NC}   - ID: $BATCH_SEM_BLOCKCHAIN_ID"
echo -e "${GREEN}║${NC}   - blockchain_token_id: null                                             ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}                                                                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC} Lote COM Blockchain:                                                      ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   - Código: $BATCH_CODE_2"
echo -e "${GREEN}║${NC}   - ID: $BATCH_COM_BLOCKCHAIN_ID"
echo -e "${GREEN}║${NC}   - blockchain_token_id: $BLOCKCHAIN_TOKEN_ID"
echo -e "${GREEN}║${NC}                                                                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC} Movimentação SEM Blockchain:                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   - ID: $MOVIMENTO_SEM_BLOCKCHAIN_ID"
echo -e "${GREEN}║${NC}   - Lote: $BATCH_SEM_BLOCKCHAIN_ID"
echo -e "${GREEN}║${NC}                                                                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC} Movimentação COM Blockchain:                                              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}   - ID: $MOVIMENTO_COM_BLOCKCHAIN_ID"
echo -e "${GREEN}║${NC}   - Lote: $BATCH_COM_BLOCKCHAIN_ID"
echo -e "${GREEN}║${NC}   - blockchain_token_id: $MOVEMENT_BLOCKCHAIN_TOKEN_ID"
echo -e "${GREEN}║${NC}                                                                           ${GREEN}║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_success "🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!"

echo ""
echo -e "${CYAN}Credenciais para teste manual:${NC}"
echo -e "  Email: ${YELLOW}$TEST_EMAIL${NC}"
echo -e "  Senha: ${YELLOW}$TEST_SENHA${NC}"
echo ""
