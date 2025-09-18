#!/bin/bash

# Comandos curl para testar a API AgentOS
# Base URL da API
BASE_URL="http://localhost:8000"
API_KEY="151fb361-f295-4a4f-84c9-ec1f42599a67"

echo "=== Testando API AgentOS ==="
echo

# 1. Health Check
echo "1. Health Check:"
curl -X GET "$BASE_URL/health" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json"
echo -e "\n\n"

# 2. Listar agentes
echo "2. Listar agentes:"
curl -X GET "$BASE_URL/agents" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json"
echo -e "\n\n"

# 3. Criar agente
echo "3. Criar agente:"
curl -X POST "$BASE_URL/agents" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agente Teste",
    "model": {
      "provider": "openai",
      "name": "gpt-4o-mini"
    },
    "system_message": "Você é um assistente útil especializado em testes.",
    "enable_user_memories": true,
    "tools": ["DuckDuckGoTools"],
    "add_history_to_context": true,
    "num_history_runs": 5,
    "add_datetime_to_context": true,
    "markdown": true,
    "user_id": "test_user"
  }'
echo -e "\n\n"

# 4. Criar time
echo "4. Criar time:"
curl -X POST "$BASE_URL/teams" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Time Teste",
    "agents": [],
    "instructions": "Este é um time de teste para validar a API.",
    "user_id": "test_user"
  }'
echo -e "\n\n"

# 5. Listar times
echo "5. Listar times:"
curl -X GET "$BASE_URL/teams" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json"
echo -e "\n\n"

# 6. Enviar mensagem para agente (usando ID do agente criado)
echo "6. Enviar mensagem para agente:"
curl -X POST "$BASE_URL/agents/run" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá! Como você pode me ajudar?",
    "user_id": "test_user",
    "session_id": "test_session_123"
  }'
echo -e "\n\n"

# 7. Enviar mensagem para time (usando ID do time criado)
echo "7. Enviar mensagem para time:"
curl -X POST "$BASE_URL/teams/run" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Preciso de ajuda com um projeto.",
    "user_id": "test_user",
    "session_id": "test_session_456"
  }'
echo -e "\n\n"

# 8. Buscar memórias
echo "8. Buscar memórias:"
curl -X POST "$BASE_URL/memory/search" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "teste",
    "user_id": "test_user",
    "limit": 5
  }'
echo -e "\n\n"

# 9. Adicionar memória
echo "9. Adicionar memória:"
curl -X POST "$BASE_URL/memory/add" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Esta é uma memória de teste"},
      {"role": "assistant", "content": "Memória salva com sucesso"}
    ],
    "user_id": "test_user",
    "metadata": {"topic": "teste"}
  }'
echo -e "\n\n"

# 10. Buscar conhecimento
echo "10. Buscar conhecimento:"
curl -X POST "$BASE_URL/knowledge/search" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "produto",
    "knowledge_id": "produto",
    "limit": 3
  }'
echo -e "\n\n"

echo "=== Testes concluídos ==="