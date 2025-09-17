# AgentOS API - Documentação Completa

## Visão Geral

A AgentOS API é uma plataforma completa para gerenciamento de agentes de IA, times e funcionalidades de memória e conhecimento. Esta API permite criar, gerenciar e executar agentes inteligentes com capacidades avançadas.

## Autenticação

Todos os endpoints requerem autenticação via header:
```
X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67
```

## Base URL
```
http://localhost:8000
```

## Endpoints Principais

### 1. Health Check
**GET** `/health`

Verifica o status da API e retorna informações básicas.

**Resposta:**
```json
{
  "status": "ok",
  "message": "AgentOS API está funcionando corretamente",
  "agents_count": 5
}
```

### 2. Gerenciamento de Agentes

#### Listar Agentes
**GET** `/agents`

Retorna lista de todos os agentes disponíveis.

**Resposta:**
```json
{
  "default_agents": [
    {
      "name": "Assistente Principal",
      "role": "Assistente geral",
      "instructions": ["Seja prestativo e educado"]
    }
  ],
  "custom_agents": [],
  "total": 5
}
```

#### Criar Agente
**POST** `/agents`

**Body:**
```json
{
  "name": "Assistente de Vendas",
  "model": {
    "provider": "openai",
    "name": "gpt-4o-mini"
  },
  "system_message": "Você é um assistente especializado em vendas.",
  "enable_user_memories": true,
  "tools": ["DuckDuckGoTools"],
  "add_history_to_context": true,
  "num_history_runs": 5,
  "add_datetime_to_context": true,
  "markdown": true,
  "user_id": "default_user"
}
```

#### Executar Agente
**POST** `/agents/{agent_id}/run`

**Body:**
```json
{
  "message": "Olá, como você pode me ajudar?",
  "user_id": "test_user_123",
  "session_id": "session_456"
}
```

**Resposta:**
```json
{
  "messages": ["Resposta do agente"],
  "transferir": false,
  "session_id": "session_456",
  "user_id": "test_user_123",
  "agent_id": "agent_id",
  "custom": [],
  "agent_usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "model": "gpt-4o-mini"
  }
}
```

### 3. Gerenciamento de Times

#### Criar Time
**POST** `/teams`

**Body:**
```json
{
  "name": "Time de Suporte",
  "agents": ["Assistente Principal"],
  "instructions": "Este time é responsável por fornecer suporte técnico.",
  "user_id": "default_user"
}
```

#### Executar Time
**POST** `/teams/{team_id}/run`

**Body:**
```json
{
  "message": "Olá time, como vocês podem me ajudar?",
  "user_id": "test_user_123",
  "session_id": "session_456"
}
```

### 4. Chat Endpoint
**POST** `/chat`

Endpoint alternativo para interação com agentes.

**Body:**
```json
{
  "message": "Olá, preciso de ajuda",
  "agent_name": "Assistente Principal",
  "user_id": "test_user_123"
}
```

### 5. Gerenciamento de Memória

#### Buscar Memórias
**GET** `/memory/search?user_id=test_user&query=exemplo&limit=5`

#### Adicionar Memória
**POST** `/memory/add`

**Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Pergunta do usuário"},
    {"role": "assistant", "content": "Resposta do assistente"}
  ],
  "user_id": "test_user_123",
  "metadata": {}
}
```

### 6. Gerenciamento de Conhecimento

#### Buscar Conhecimento
**GET** `/knowledge/search?query=exemplo&knowledge_id=produto&limit=5`

#### Criar Base de Conhecimento
**POST** `/knowledge`

**Body:**
```json
{
  "type": "text",
  "name": "Base de Produtos",
  "description": "Conhecimento sobre produtos",
  "content": "Conteúdo da base de conhecimento",
  "reader": "default",
  "chunker": "default"
}
```

## Códigos de Status

- **200**: Sucesso
- **400**: Erro de validação
- **401**: Não autorizado (chave de API inválida)
- **404**: Recurso não encontrado
- **500**: Erro interno do servidor

## Estruturas de Dados

### AgentCreateRequest
```json
{
  "id": "string (opcional)",
  "name": "string (obrigatório)",
  "model": {
    "provider": "openai",
    "name": "gpt-4o-mini"
  },
  "system_message": "string (obrigatório)",
  "enable_user_memories": true,
  "tools": ["DuckDuckGoTools"],
  "add_history_to_context": true,
  "num_history_runs": 5,
  "add_datetime_to_context": true,
  "markdown": true,
  "user_id": "default_user"
}
```

### TeamCreateRequest
```json
{
  "id": "string (opcional)",
  "name": "string (obrigatório)",
  "agents": ["lista de IDs de agentes"],
  "instructions": "string (obrigatório)",
  "user_id": "default_user"
}
```

### ChatRequest
```json
{
  "message": "string (obrigatório)",
  "agent_name": "string (opcional)",
  "user_id": "default_user"
}
```

## Exemplos de Uso

### Fluxo Completo: Criar e Usar um Agente

1. **Criar um agente:**
```bash
curl -X POST "http://localhost:8000/agents" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json" \
  -d '{"name": "Meu Assistente", "system_message": "Seja útil"}'
```

2. **Enviar mensagem para o agente:**
```bash
curl -X POST "http://localhost:8000/agents/Meu Assistente/run" \
  -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá!", "user_id": "user123"}'
```

## Documentação Interativa

Acesse a documentação Swagger em:
```
http://localhost:8000/docs
```

## Notas Importantes

1. **Autenticação**: Todos os endpoints requerem a chave de API no header
2. **IDs de Agentes**: Podem ser nomes ou UUIDs
3. **Sessões**: O `session_id` é opcional mas recomendado para conversas longas
4. **Memória**: Habilitada por padrão para manter contexto entre interações
5. **Ferramentas**: DuckDuckGoTools é a ferramenta padrão disponível

## Troubleshooting

### Erros Comuns

1. **"run() got an unexpected keyword argument 'user_id'"**
   - Problema conhecido no endpoint de execução de agentes
   - Use o endpoint `/chat` como alternativa

2. **"Agente não encontrado"**
   - Verifique se o ID/nome do agente está correto
   - Use `/agents` para listar agentes disponíveis

3. **"É necessário pelo menos um agente para criar um time"**
   - Certifique-se de que a lista de agentes não está vazia
   - Verifique se os agentes especificados existem

## Suporte

Para mais informações, consulte:
- Documentação Swagger: `http://localhost:8000/docs`
- Logs da aplicação para debugging
- Arquivo de comandos cURL: `COMANDOS_CURL.md`