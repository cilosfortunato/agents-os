# 🚀 Guia de Deploy - AgentOS API Completa

## 📋 Pré-requisitos

- Python 3.8+
- Conta Supabase configurada
- Chave OpenAI válida
- Conta Mem0 (opcional, para memória)
- Servidor com acesso à internet

## 🔧 Configuração Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/cilosfortunato/agents-os.git
cd agents-os
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o Ambiente
```bash
# Copie o arquivo de ambiente
cp .env.deploy .env

# Edite o arquivo .env com suas chaves
nano .env
```

### 4. Configure o Supabase

Execute os seguintes comandos SQL no seu projeto Supabase:

```sql
-- Tabela de agentes
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    model TEXT DEFAULT 'gpt-4o-mini',
    temperature REAL DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 1000,
    tools JSONB DEFAULT '[]',
    knowledge JSONB DEFAULT '{}',
    memory_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de mensagens
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    user_id TEXT NOT NULL,
    session_id UUID,
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
```

### 5. Inicie a API
```bash
# Desenvolvimento
python api_completa.py

# Produção (com Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_completa:app --bind 0.0.0.0:8003
```

## 🔑 Variáveis de Ambiente Obrigatórias

### Essenciais
```env
OPENAI_API_KEY=sua_chave_openai
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role
OUTBOUND_WEBHOOK_URL=https://seu-webhook.com/webhook
```

### Opcionais
```env
MEM0_API_KEY=sua_chave_mem0
X_API_KEY=sua_chave_autenticacao
PORT=8003
LOG_LEVEL=INFO
```

## 🧪 Teste a Instalação

### 1. Health Check
```bash
curl -X GET "http://localhost:8003/v1/health" \
  -H "X-API-Key: sua_chave_api"
```

### 2. Criar um Agente
```bash
curl -X POST "http://localhost:8003/v1/agents" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua_chave_api" \
  -d '{
    "name": "Assistente Teste",
    "description": "Agente para testes",
    "instructions": "Você é um assistente útil e amigável."
  }'
```

### 3. Enviar Mensagem
```bash
curl -X POST "http://localhost:8003/v1/messages" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua_chave_api" \
  -d '{
    "mensagem": "Olá, como você está?",
    "agent_id": "ID_DO_AGENTE_CRIADO",
    "user_id": "usuario_teste",
    "session_id": "sessao_teste",
    "debounce": 15000
  }'
```

## 🐳 Deploy com Docker

### 1. Build da Imagem
```bash
docker build -t agnos-api .
```

### 2. Execute o Container
```bash
docker run -d \
  --name agnos-api \
  -p 8003:8003 \
  --env-file .env \
  agnos-api
```

## 🔧 Configuração de Webhook

Para receber as respostas dos agentes, configure um endpoint que aceite POST:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Resposta do agente: {data}")
    
    # Processe a resposta aqui
    # data contém: messages, session_id, user_id, agent_id, etc.
    
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
```

## 📊 Monitoramento

### Logs da Aplicação
```bash
tail -f logs/agnos.log
```

### Métricas de Performance
- Acesse `/v1/health` para status da API
- Monitore uso de tokens OpenAI
- Acompanhe latência das requisições

## 🚨 Troubleshooting

### Problemas Comuns

1. **Erro de conexão Supabase**
   - Verifique URL e chaves
   - Confirme que as tabelas foram criadas

2. **Timeout OpenAI**
   - Verifique conectividade
   - Confirme cota da API

3. **Webhook não recebe dados**
   - Verifique URL do webhook
   - Confirme que o endpoint está acessível

4. **Memória não funciona**
   - Verifique chave Mem0
   - Confirme configuração do agente

### Logs Úteis
```bash
# Ver logs em tempo real
tail -f logs/agnos.log

# Filtrar erros
grep "ERROR" logs/agnos.log

# Ver últimas 100 linhas
tail -n 100 logs/agnos.log
```

## 📞 Suporte

- **Documentação**: Consulte os arquivos MD no repositório
- **Issues**: Abra uma issue no GitHub
- **Logs**: Sempre inclua logs relevantes ao reportar problemas

---

✅ **Deploy concluído com sucesso!** Sua API AgentOS está pronta para uso em produção.