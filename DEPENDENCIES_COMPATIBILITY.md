# Compatibilidades de Dependências - AgentOS

## Versões Testadas e Compatíveis

### Python
- **Versão Recomendada**: Python 3.9+
- **Versões Testadas**: 3.9, 3.10, 3.11
- **Versão Mínima**: 3.8

### Dependências Principais

#### FastAPI Stack
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

#### AI/ML Libraries
```
openai==1.99.9
mem0ai==0.1.117
pinecone-client==2.2.4
langchain==0.1.0
langchain-openai==0.0.2
```

#### Database & Storage
```
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9  # Para PostgreSQL
sqlite3  # Built-in Python
```

#### Utilities
```
python-dotenv==1.0.0
requests==2.31.0
python-multipart==0.0.6
jinja2==3.1.2
```

#### Development & Testing
```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2  # Para testes de API
black==23.11.0  # Code formatting
flake8==6.1.0  # Linting
```

## Compatibilidades por Sistema Operacional

### Windows
- ✅ Windows 10/11
- ✅ PowerShell 5.1+
- ✅ WSL2 (recomendado para desenvolvimento)

### Linux
- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ CentOS 8+
- ✅ Alpine Linux (para Docker)

### macOS
- ✅ macOS 11+ (Big Sur)
- ✅ Apple Silicon (M1/M2)
- ✅ Intel x86_64

## Serviços Externos

### OpenAI
- **API Version**: v1
- **Modelos Suportados**:
  - gpt-3.5-turbo
  - gpt-4
  - gpt-4-turbo
  - text-embedding-ada-002

### Mem0 AI
- **API Version**: v1
- **Planos Suportados**: Free, Pro, Enterprise
- **Limites**: Conforme plano contratado

### Pinecone
- **API Version**: v1
- **Índices**: Suporte a dimensões 1536 (OpenAI embeddings)
- **Ambientes**: gcp-starter, aws-starter

## Docker

### Base Images Testadas
```dockerfile
# Produção
FROM python:3.11-slim

# Desenvolvimento
FROM python:3.11

# Alpine (menor tamanho)
FROM python:3.11-alpine
```

### Recursos Mínimos
- **RAM**: 512MB (mínimo), 2GB (recomendado)
- **CPU**: 1 core (mínimo), 2+ cores (recomendado)
- **Disco**: 1GB (mínimo), 5GB (recomendado)

## Variáveis de Ambiente Obrigatórias

```bash
# APIs Externas
OPENAI_API_KEY=sk-...
MEM0_API_KEY=m0-...
PINECONE_API_KEY=pcsk_...

# Configuração da API
API_KEY=151fb361-f295-4a4f-84c9-ec1f42599a67
HOST=0.0.0.0
PORT=8000

# Database (opcional)
DATABASE_URL=sqlite:///./agents.db
```

## Problemas Conhecidos e Soluções

### 1. Conflitos de Dependências
**Problema**: Conflito entre pydantic v1 e v2
**Solução**: Usar pydantic==2.5.0+ e atualizar código para v2

### 2. Mem0 API Limits
**Problema**: Rate limiting em planos gratuitos
**Solução**: Implementar retry com backoff exponencial

### 3. Pinecone Connection Issues
**Problema**: Timeout em conexões
**Solução**: Configurar timeout adequado e retry logic

### 4. OpenAI Token Limits
**Problema**: Excesso de tokens em conversas longas
**Solução**: Implementar truncamento inteligente de contexto

## Instalação Recomendada

### 1. Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Instalação de Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuração
```bash
cp .env.example .env
# Editar .env com suas chaves de API
```

## Testes de Compatibilidade

### Comando de Teste Rápido
```bash
python -c "import fastapi, openai, mem0, pinecone; print('✅ Todas as dependências OK')"
```

### Teste Completo
```bash
pytest tests/ -v
```

## Atualizações de Dependências

### Verificar Atualizações
```bash
pip list --outdated
```

### Atualizar com Segurança
```bash
# Testar em ambiente separado primeiro
pip install --upgrade package_name
pytest tests/
```

## Notas de Versão

### v1.0.0 (Atual)
- Suporte inicial a Python 3.9+
- FastAPI 0.104.1
- Integração com Mem0 e Pinecone
- API completa de agentes e times

### Roadmap
- [ ] Suporte a Python 3.12
- [ ] Migração para Pydantic v2.6+
- [ ] Suporte a múltiplos provedores de LLM
- [ ] Cache Redis opcional
- [ ] Métricas e observabilidade

## Contato e Suporte

Para problemas de compatibilidade:
1. Verificar esta documentação
2. Consultar logs de erro
3. Testar em ambiente limpo
4. Reportar issues no GitHub