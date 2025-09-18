# Guia de Deploy - AgentOS API

## Problema Resolvido

O problema no deploy estava relacionado à diferença entre a imagem Docker e os endpoints do Swagger em produção. A solução incluiu:

1. ✅ **Dockerfile atualizado** - Configurado para usar a porta 80
2. ✅ **Imagem Docker reconstruída** - Com todas as correções aplicadas
3. ✅ **Scripts de deploy criados** - Para automatizar o processo
4. ✅ **Testes validados** - Health check e endpoints funcionando

## Scripts de Deploy Disponíveis

### PowerShell (Windows)
```powershell
.\deploy.ps1
```

### Bash (Linux/Mac)
```bash
./deploy.sh
```

## Deploy Manual

### 1. Build da Imagem
```bash
docker build -t agnos-api:latest .
```

### 2. Tag para Produção
```bash
docker tag agnos-api:latest agnos-api:prod
```

### 3. Teste Local
```bash
docker run -d -p 8080:80 --env-file .env --name agnos-api-test agnos-api:latest
```

### 4. Verificação
```bash
curl http://localhost:8080/v1/health
```

### 5. Limpeza
```bash
docker stop agnos-api-test
docker rm agnos-api-test
```

## Deploy em Produção

### Opção 1: Docker Registry
```bash
# Push para registry
docker push agnos-api:prod

# Pull e run em produção
docker pull agnos-api:prod
docker run -d -p 80:80 --env-file .env --name agnos-api-prod agnos-api:prod
```

### Opção 2: Docker Compose
Crie um `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  agnos-api:
    image: agnos-api:prod
    ports:
      - "80:80"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Execute:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Variáveis de Ambiente Necessárias

Certifique-se de que o arquivo `.env` em produção contenha:

```env
# Configurações da API
PORT=80
HOST=0.0.0.0

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Supabase
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...

# Pinecone
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=agno-knowledge-base
PINECONE_ENVIRONMENT=gcp-starter

# Mem0
MEM0_API_KEY=m0-...
```

## Endpoints Disponíveis

Após o deploy, os seguintes endpoints estarão disponíveis:

- **Swagger UI**: `http://localhost/docs`
- **Health Check**: `http://localhost/v1/health`
- **Chat**: `http://localhost/v1/chat`
- **Mensagens**: `http://localhost/v1/messages`
- **Agentes**: `http://localhost/v1/agents`
- **Knowledge**: `http://localhost/v1/knowledge/search`
- **Memória**: `http://localhost/v1/memory/search`

## Verificação Pós-Deploy

1. **Health Check**:
   ```bash
   curl http://localhost/v1/health
   ```

2. **Swagger UI**:
   Acesse `http://localhost/docs` no navegador

3. **Teste de Endpoint**:
   ```bash
   curl -X POST "http://localhost/v1/messages" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: 151fb361-f295-4a4f-84c9-ec1f42599a67" \
        -d '[{"mensagem": "teste", "agent_id": "test", "user_id": "test"}]'
   ```

## Troubleshooting

### Container não inicia
- Verifique as variáveis de ambiente
- Verifique os logs: `docker logs agnos-api-prod`

### Health check falha
- Verifique se a porta 80 está disponível
- Verifique conectividade com Supabase/Pinecone/Mem0

### Endpoints diferentes
- Confirme que a imagem foi reconstruída após as correções
- Verifique se está usando a tag correta da imagem

## Rollback

Em caso de problemas:

```bash
# Parar container atual
docker stop agnos-api-prod

# Voltar para versão anterior
docker run -d -p 80:80 --env-file .env --name agnos-api-prod agnos-api:previous-version
```