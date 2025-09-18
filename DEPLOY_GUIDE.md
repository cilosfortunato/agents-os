# 🚀 Guia Completo de Deploy - AgentOS

## 📋 Problemas Identificados e Soluções

### ✅ Status dos Testes
- **Dependências**: ✅ Todas instaladas corretamente
- **Variáveis de ambiente**: ✅ Configuradas
- **Módulos locais**: ✅ Funcionando
- **API local**: ✅ Funcionando perfeitamente
- **Docker**: ⚠️ Docker Desktop não está rodando

## 🔧 Correções Implementadas

### 1. Dockerfile Otimizado
- ✅ Adicionado `curl` para health checks
- ✅ Corrigida porta fixa no health check
- ✅ Configuração de usuário não-root
- ✅ Variáveis de ambiente configuradas

### 2. Requirements.txt Atualizado
- ✅ Removido `agno[pinecone]` problemático
- ✅ Adicionado `agno>=0.1.0` separadamente
- ✅ Mantidas todas as dependências necessárias

### 3. Arquivos de Deploy
- ✅ `.dockerignore` criado para otimizar build
- ✅ `.env.example` para deploy seguro
- ✅ Scripts de teste automatizados

## 🐳 Deploy com Docker

### Pré-requisitos
1. **Docker Desktop** deve estar instalado e rodando
2. Variáveis de ambiente configuradas no `.env`

### Passos para Deploy

#### 1. Verificar Docker
```bash
docker --version
docker info
```

#### 2. Build da Imagem
```bash
docker build -t agentos:latest .
```

#### 3. Executar Container
```bash
docker run -d --name agentos \
  -p 7777:7777 \
  --env-file .env \
  agentos:latest
```

#### 4. Verificar Status
```bash
docker ps
docker logs agentos
curl http://localhost:7777/health
```

## ☁️ Deploy em Produção

### Easypanel (Recomendado)

1. **Criar novo serviço**
2. **Configurar variáveis de ambiente**:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   OPENROUTER_API_KEY=sua_chave_aqui
   MEM0_API_KEY=sua_chave_aqui
   X_API_KEY=sua_chave_aqui
   ```
3. **Usar Dockerfile** do repositório
4. **Porta**: 7777
5. **Health Check**: `/health`

### Railway

1. **Conectar repositório GitHub**
2. **Configurar variáveis de ambiente**
3. **Deploy automático** será feito

### Render

1. **Novo Web Service**
2. **Conectar repositório**
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

## 🔍 Troubleshooting

### Problema: Docker não funciona
**Solução**: 
1. Instalar Docker Desktop
2. Iniciar o serviço
3. Verificar com `docker --version`

### Problema: Dependências faltando
**Solução**:
```bash
pip install -r requirements.txt
```

### Problema: Variáveis de ambiente
**Solução**:
1. Copiar `.env.example` para `.env`
2. Preencher com suas chaves reais
3. Verificar com `python test_deploy.py`

### Problema: Porta em uso
**Solução**:
```bash
# Verificar processo na porta
netstat -ano | findstr :7777

# Matar processo se necessário
taskkill /PID <PID> /F
```

## 📊 Monitoramento

### Endpoints de Saúde
- **Health Check**: `GET /health`
- **Documentação**: `GET /docs`
- **Agentes**: `GET /agents`

### Logs
```bash
# Docker
docker logs agentos

# Local
python -m uvicorn api:app --host 0.0.0.0 --port 7777 --log-level info
```

## 🎯 Próximos Passos

1. **Iniciar Docker Desktop**
2. **Executar build e teste**:
   ```bash
   powershell -ExecutionPolicy Bypass -File build_and_test.ps1
   ```
3. **Deploy em produção** usando um dos métodos acima

## 📞 Suporte

Se encontrar problemas:
1. Execute `python test_deploy.py` para diagnóstico
2. Verifique logs do container
3. Confirme variáveis de ambiente
4. Teste endpoints manualmente

---

**Status**: ✅ Sistema funcionando localmente, pronto para deploy em produção!