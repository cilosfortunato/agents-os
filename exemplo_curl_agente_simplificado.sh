#!/bin/bash

# Configurações
BASE_URL="http://localhost:80"
AUTH_HEADER="X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67"
CONTENT_TYPE="Content-Type: application/json"

echo "=== Criando Agente com Estrutura Simplificada ==="

# 1. Criar agente (sem ID - será gerado automaticamente)
echo "1. Criando agente sem ID (UUID será gerado automaticamente)..."
curl -X POST $BASE_URL/agents \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "name": "MeuAgente",
    "model": {"provider": "openai", "name": "gpt-4o-mini"},
    "system_message": "Você é um assistente útil que responde perguntas sobre IA.",
    "enable_user_memories": true,
    "tools": ["DuckDuckGoTools"]
  }'

echo -e "\n\n"

# 2. Criar agente com ID específico
echo "2. Criando agente com ID específico..."
curl -X POST $BASE_URL/agents \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "MeuAgenteComID",
    "model": {"provider": "openai", "name": "gpt-4o-mini"},
    "system_message": "Você é um assistente útil que responde perguntas sobre IA.",
    "enable_user_memories": true,
    "tools": ["DuckDuckGoTools"]
  }'

echo -e "\n\n"

# 3. Enviar mensagem para o agente
echo "3. Enviando mensagem para o agente..."
curl -X POST $BASE_URL/agents/550e8400-e29b-41d4-a716-446655440000/run \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{
    "message": "Qual é o futuro da IA?",
    "user_id": "user_especifico_456",
    "session_id": "session_123"
  }'

echo -e "\n\n=== Teste Concluído ==="