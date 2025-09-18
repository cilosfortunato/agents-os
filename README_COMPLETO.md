# 🚀 Sistema Completo de Agentes com Knowledge (RAG) e Memória (Mem0)

## 📋 Visão Geral

Este projeto implementa um sistema completo de agentes inteligentes utilizando o ecossistema AgentOS/Agno, com funcionalidades avançadas de:

- **Knowledge Base (RAG)** com Pinecone para busca semântica
- **Memória Contextual** com Mem0 para personalização
- **API FastAPI** para exposição dos serviços
- **Agentes Inteligentes** que combinam ambas as tecnologias

## 🎯 Funcionalidades Implementadas

### ✅ 1. Base de Conhecimento (RAG)
- Configuração nativa com Pinecone
- Sincronização automática de documentos
- Busca semântica inteligente
- Integração transparente com agentes

### ✅ 2. Memória Contextual (Mem0)
- Armazenamento de interações passadas
- Busca contextual por usuário
- Personalização de respostas
- Histórico persistente

### ✅ 3. Agentes Inteligentes
- Criação dinâmica de agentes
- Integração com Knowledge e Memória
- Respostas contextualizadas
- Suporte a múltiplos usuários

### ✅ 4. API FastAPI Completa
- Endpoints RESTful
- Documentação automática
- Health checks
- Tratamento de erros

## 📁 Estrutura do Projeto

```
agnos/
├── agente_completo.py          # Sistema principal com Knowledge e Memória
├── api_completa.py             # API FastAPI completa
├── test_api_completa.py        # Testes abrangentes
├── test_debug_storage.py       # Testes de storage de agentes
├── manual_produto.txt          # Base de conhecimento
├── api.py                      # API interna do AgentOS
├── agents.py                   # Gerenciamento de agentes
└── README_COMPLETO.md          # Esta documentação
```

## 🔧 Configuração e Instalação

### 1. Dependências
```bash
pip install "agno[pinecone]" mem0ai python-dotenv fastapi uvicorn
```

### 2. Variáveis de Ambiente
Crie um arquivo `.env`:
```env
OPENAI_API_KEY="sua_chave_openai_aqui"
PINECONE_API_KEY="sua_chave_pinecone_aqui"
MEM0_API_KEY="sua_chave_mem0_aqui"
```

### 3. Configuração do Pinecone
- Crie um índice chamado `agno-knowledge-base`
- Use o ambiente `gcp-starter`
- Dimensão: 1536 (para embeddings OpenAI)

## 🚀 Como Usar

### 1. Sistema Principal
```bash
python agente_completo.py
```
Demonstra a criação e uso de agentes com Knowledge e Memória.

### 2. API FastAPI
```bash
python api_completa.py
```
Inicia a API em `http://localhost:8001`

### 3. Testes Completos
```bash
python test_api_completa.py
```
Executa todos os testes do sistema.

## 📚 Endpoints da API

### Status e Saúde
- `GET /` - Status da API
- `GET /v1/health` - Health check completo

### Knowledge (RAG)
- `GET /v1/knowledge/search` - Buscar na base de conhecimento
- `POST /v1/knowledge/sync` - Sincronizar base de conhecimento

### Memória (Mem0)
- `GET /v1/memory/search` - Buscar memórias do usuário

### Agentes
- `POST /v1/agents` - Criar novo agente inteligente
- `POST /v1/query` - Consulta inteligente com Knowledge e Memória

## 💡 Exemplos de Uso

### Consulta Inteligente
```python
import requests

response = requests.post("http://localhost:8001/v1/query", json={
    "user_id": "usuario123",
    "question": "Como ativar o modo noturno?",
    "agent_name": "Especialista em Produtos"
})

print(response.json())
```

### Busca na Base de Conhecimento
```python
response = requests.get("http://localhost:8001/v1/knowledge/search", params={
    "query": "bateria",
    "limit": 5
})

print(response.json())
```

### Criar Agente Inteligente
```python
response = requests.post("http://localhost:8001/v1/agents", json={
    "name": "Assistente Personalizado",
    "role": "Especialista em suporte técnico",
    "instructions": [
        "Use sempre a base de conhecimento",
        "Mantenha tom profissional",
        "Personalize com base na memória do usuário"
    ]
})

print(response.json())
```

## 🧪 Resultados dos Testes

Todos os testes passaram com sucesso:

- ✅ Status da API
- ✅ Health Check
- ✅ Busca Knowledge
- ✅ Busca Memória
- ✅ Criação de Agente
- ✅ Consulta Inteligente
- ✅ Sincronização Knowledge

**Resultado: 7/7 testes passaram** 🎉

## 🔍 Monitoramento

### Logs do Sistema
O sistema fornece logs detalhados para:
- Criação de agentes
- Sincronização de conhecimento
- Consultas e respostas
- Erros e exceções

### Health Checks
A API monitora automaticamente:
- Status da API interna
- Conectividade com Pinecone
- Conectividade com Mem0
- Status dos serviços

## 🛠️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   AgentOS       │    │   Knowledge     │
│   (Port 8001)   │◄──►│   (Port 80)     │◄──►│   (Pinecone)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mem0 Memory   │    │   OpenAI LLM    │    │   Vector DB     │
│   (Contextual)  │    │   (GPT-4)       │    │   (Embeddings)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Próximos Passos

1. **Escalabilidade**: Implementar cache Redis
2. **Segurança**: Adicionar autenticação JWT
3. **Monitoramento**: Integrar Prometheus/Grafana
4. **Deploy**: Containerização com Docker
5. **CI/CD**: Pipeline automatizado

## 📖 Referências

- [Documentação AgentOS](https://docs.agno.com/agent-os/introduction)
- [Documentação Mem0](https://docs.mem0.ai/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contribuição

Este projeto demonstra a implementação completa do guia definitivo do AgentOS com Knowledge e Memória. Todas as funcionalidades foram testadas e estão funcionando perfeitamente.

---

**Status**: ✅ **COMPLETO E FUNCIONAL**  
**Última atualização**: Janeiro 2025  
**Versão**: 1.0.0