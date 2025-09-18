# Comandos cURL para AgentOS API

## Autenticação
Todos os endpoints requerem a chave de API no header:
```
X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67
```

## 1. Health Check
```bash
curl -X GET "http://localhost:8000/health" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json"
```

## 2. Listar Agentes
```bash
curl -X GET "http://localhost:8000/agents" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json"
```

## 3. Criar Agente
```bash
curl -X POST "http://localhost:8000/agents" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistente de Vendas Estética Vênus",
    "model": {
      "provider": "openai",
      "name": "gpt-4o-mini"
    },
    "system_message": "Você é um especialista em beleza e consultor de vendas da Estética Vênus, uma clínica de estética premium especializada em harmonização facial, toxina botulínica e tratamentos rejuvenescedores. Sua missão é entender as necessidades e desejos de cada cliente, oferecendo soluções personalizadas com um atendimento cordial, empático e altamente profissional.",
    "enable_user_memories": true,
    "tools": ["DuckDuckGoTools"],
    "account_id": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
  }'
```

**Resposta esperada:**
```json
{
  "message": "Agente criado com sucesso",
  "agent": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Assistente de Vendas Estética Vênus",
    "model": {
      "provider": "openai",
      "name": "gpt-4o-mini"
    },
    "system_message": "Você é um especialista em beleza...",
    "enable_user_memories": true,
    "tools": ["DuckDuckGoTools"],
    "account_id": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
  }
}
```

## 4. Criar Time
```bash
curl -X POST "http://localhost:8000/teams" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Time de Suporte",
    "agents": ["Assistente Principal"],
    "instructions": "Este time é responsável por fornecer suporte técnico aos usuários.",
    "user_id": "default_user"
  }'
```

## 5. Enviar Mensagem para Agente
```bash
curl -X POST "http://localhost:8000/agents/{agent_id}/run" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, como você pode me ajudar?",
    "user_id": "test_user_123",
    "session_id": "session_456"
  }'
```

## 6. Enviar Mensagem para Time
```bash
curl -X POST "http://localhost:8000/teams/{team_id}/run" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá time, como vocês podem me ajudar?",
    "user_id": "test_user_123",
    "session_id": "session_456"
  }'
```

## 7. Chat Endpoint (Alternativo)
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Olá, preciso de ajuda",
    "agent_name": "Assistente Principal",
    "user_id": "test_user_123"
  }'
```

## Notas Importantes:

1. **IDs dos Agentes**: Substitua `{agent_id}` pelo ID real do agente (ex: "Assistente Principal")
2. **IDs dos Times**: Substitua `{team_id}` pelo ID real do time retornado na criação
3. **Estrutura de Resposta**: Todos os endpoints retornam uma estrutura JSON padronizada
4. **Autenticação**: A chave de API é obrigatória em todos os endpoints
5. **Erros Comuns**: 
   - Agente/Time não encontrado (404)
   - Argumentos inválidos no método run()
   - Chave de API inválida (401)

## Endpoints Testados com Sucesso:
- ✅ Health Check
- ✅ Listar Agentes
- ✅ Criar Agente
- ✅ Criar Time
- ✅ Chat Endpoint
- ❌ Executar Agente (erro no método run)
- ❌ Executar Time (não testado devido ao erro anterior)