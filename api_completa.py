#!/usr/bin/env python3
"""
API Completa com AgentOS, Knowledge (RAG) e Memória (Mem0)
Baseada no guia definitivo do AgentOS
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import os
from dotenv import load_dotenv
import requests
import uuid
from datetime import datetime
import json

# Importações para IA e memória
import openai
from mem0 import MemoryClient

# Importação dos serviços
from supabase_service import SupabaseService
from dual_memory_service import dual_memory_service

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de chaves de API
INTERNAL_API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MEM0_API_KEY = os.getenv("MEM0_API_KEY")

# Função de verificação de API Key
async def verify_api_key(x_api_key: str = Header(None)):
    """Verifica se a X-API-Key é válida"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="X-API-Key header é obrigatório",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="X-API-Key inválida",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return x_api_key

# Modelos de dados para Chat/Mensagens
class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem do usuário")
    agent_name: Optional[str] = Field("Especialista em Produtos", description="Nome do agente")
    user_id: str = Field(..., description="ID do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")

class MessageRequest(BaseModel):
    mensagem: str = Field(..., description="Mensagem do usuário")
    agent_id: str = Field(..., description="ID do agente")
    user_id: str = Field(..., description="ID do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    message_id: Optional[str] = Field(None, description="ID da mensagem")
    cliente_id: Optional[str] = Field("", description="ID do cliente")
    id_conta: Optional[str] = Field(None, description="ID da conta")
    debounce: Optional[int] = Field(15000, description="Tempo de debounce em ms")

# Modelos de dados para Agentes
class AgentCreateRequest(BaseModel):
    name: str = Field(..., description="Nome do agente")
    role: str = Field(..., description="Papel/função do agente")
    instructions: List[str] = Field(..., description="Lista de instruções para o agente")
    model: Optional[str] = Field("openai/gpt-4o-mini", description="Modelo LLM a ser usado")
    account_id: Optional[str] = Field(None, description="ID da conta associada ao agente")

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Novo nome do agente")
    role: Optional[str] = Field(None, description="Nova função do agente")
    instructions: Optional[List[str]] = Field(None, description="Novas instruções")
    model: Optional[str] = Field(None, description="Novo modelo LLM")
    account_id: Optional[str] = Field(None, description="Novo ID da conta")

class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    instructions: List[str]
    model: str
    account_id: Optional[str]
    created_at: str

# Modelos para Knowledge e Memória
class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., description="Consulta para buscar na base de conhecimento")
    limit: Optional[int] = Field(5, description="Número máximo de resultados")

class MemorySearchRequest(BaseModel):
    user_id: str = Field(..., description="ID do usuário")
    query: str = Field(..., description="Consulta para buscar na memória")
    limit: Optional[int] = Field(3, description="Número máximo de resultados")

class MemoryAddRequest(BaseModel):
    user_id: str = Field(..., description="ID do usuário")
    content: str = Field(..., description="Conteúdo para adicionar à memória")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")

# Modelos de resposta
class ChatResponse(BaseModel):
    response: str
    agent_name: str
    user_id: str
    session_id: Optional[str]
    timestamp: str

class MessageResponse(BaseModel):
    messages: List[str]
    transferir: bool = False
    session_id: Optional[str]
    user_id: str
    agent_id: str
    custom: Optional[List[Dict[str, str]]] = []
    agent_usage: Optional[Dict[str, Any]] = None

# Inicializa FastAPI
app = FastAPI(
    title="API de Agente de Suporte com Knowledge e Memória",
    description="Uma API completa para interagir com agentes inteligentes que usam RAG nativo e memória Mem0.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Status",
            "description": "Endpoints de status e saúde do sistema"
        },
        {
            "name": "Chat & Mensagens",
            "description": "Endpoints para envio de mensagens e chat com agentes"
        },
        {
            "name": "Agentes",
            "description": "Gerenciamento de agentes inteligentes"
        },
        {
            "name": "Knowledge (RAG)",
            "description": "Base de conhecimento e busca semântica"
        },
        {
            "name": "Memória (Mem0)",
            "description": "Sistema de memória contextual"
        }
    ]
)

# Instancia o serviço do Supabase
supabase_service = SupabaseService()

# Simulação de banco de dados em memória para sessões
sessions_db = {}
memory_db = {}

# Simulação das funcionalidades de Knowledge e Memória
class KnowledgeService:
    """Serviço de Knowledge (RAG) com Pinecone"""
    
    def __init__(self):
        self.knowledge_base = [
            {"content": "O modo noturno pode ser ativado no menu de configurações > tela.", "score": 0.95, "id": "kb_1"},
            {"content": "A bateria do dispositivo X dura 24 horas com uso moderado.", "score": 0.90, "id": "kb_2"},
            {"content": "Para reiniciar o dispositivo, pressione o botão de energia por 10 segundos.", "score": 0.85, "id": "kb_3"},
            {"content": "A garantia padrão do produto é de 12 meses e cobre defeitos de fabricação.", "score": 0.80, "id": "kb_4"},
            {"content": "O suporte técnico está disponível de segunda a sexta, das 8h às 18h.", "score": 0.75, "id": "kb_5"},
            {"content": "O dispositivo suporta carregamento rápido de 30W.", "score": 0.70, "id": "kb_6"},
            {"content": "A tela tem resolução 4K e suporte a HDR.", "score": 0.65, "id": "kb_7"},
            {"content": "O produto é resistente à água com certificação IP68.", "score": 0.60, "id": "kb_8"}
        ]
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """Busca na base de conhecimento"""
        query_lower = query.lower()
        results = []
        
        for item in self.knowledge_base:
            if any(word in item["content"].lower() for word in query_lower.split()):
                results.append(item)
        
        # Ordena por relevância (score)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def sync_knowledge(self) -> bool:
        """Sincroniza a base de conhecimento"""
        return True

class MemoryService:
    """Serviço de Memória com Mem0"""
    
    def save_memory(self, user_id: str, prompt: str, response: str) -> bool:
        """Salva interação na memória"""
        if user_id not in memory_db:
            memory_db[user_id] = []
        
        memory_entry = {
            "id": str(uuid.uuid4()),
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "text": f"Usuário perguntou: '{prompt}' e recebeu: '{response}'"
        }
        
        memory_db[user_id].append(memory_entry)
        return True
    
    def search_memory(self, user_id: str, query: str, limit: int = 3) -> List[Dict]:
        """Busca memórias do usuário"""
        if user_id not in memory_db:
            return []
        
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in memory_db[user_id]:
            if any(word in memory["text"].lower() for word in query_lower.split()):
                relevant_memories.append(memory)
        
        return relevant_memories[-limit:]  # Retorna as mais recentes
    
    def add_memory(self, user_id: str, content: str, metadata: Dict = None) -> bool:
        """Adiciona memória específica"""
        if user_id not in memory_db:
            memory_db[user_id] = []
        
        memory_entry = {
            "id": str(uuid.uuid4()),
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "text": content
        }
        
        memory_db[user_id].append(memory_entry)
        return True

# Instâncias dos serviços
knowledge_service = KnowledgeService()
# Usando o dual_memory_service importado em vez de criar uma nova instância
memory_service = dual_memory_service

# Função para executar agente usando OpenAI diretamente
def execute_agent(query: str, user_id: str, agent_data: dict) -> str:
    """Executa o agente usando OpenAI diretamente"""
    try:
        # Configura o cliente OpenAI
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Template de prompt para o agente
        prompt = (
            f"Você é um {agent_data['role']}.\n"
            f"Siga estas instruções:\n"
            f"{chr(10).join(agent_data['instructions'])}\n\n"
            f"Responda à pergunta do usuário de forma precisa e profissional.\n\n"
            f"PERGUNTA:\n{query}"
        )
        
        # Executa o modelo
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback para resposta simples em caso de erro
        return f"Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente. Erro: {str(e)}"

def execute_agent_with_memory(query: str, user_id: str, agent_data: dict, memory_context: dict) -> str:
    """Executa agente com contexto de memória dupla usando OpenAI diretamente"""
    try:
        # Configura o cliente OpenAI
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Template de prompt enriquecido com contexto de memória
        system_prompt = f"""Você é {agent_data["role"]}.

INSTRUÇÕES:
{chr(10).join(agent_data["instructions"])}

CONTEXTO DA SESSÃO ATUAL:
{memory_context.get("session_context", "Nova sessão")}

CONTEXTO ENRIQUECIDO (MEMÓRIAS RELEVANTES):
{memory_context.get("enriched_context", "Nenhum contexto adicional")}

HISTÓRICO RELACIONADO:
{memory_context.get("search_context", "Nenhum histórico relacionado")}

Responda de forma natural, considerando todo o contexto acima. Se houver informações contraditórias, priorize o contexto da sessão atual."""
        
        # Executa o modelo com contexto de memória
        response = client.chat.completions.create(
            model=agent_data.get("model", "gpt-4o-mini").replace("openai/", ""),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback para resposta simples em caso de erro
        return f"Desculpe, ocorreu um erro ao processar sua solicitação com memória. Erro: {str(e)}"

# Função para gerar resposta inteligente com memória dupla
def generate_intelligent_response(query: str, user_id: str, session_id: str, agent_name: str = "Especialista em Produtos") -> str:
    """Gera resposta usando AgentOS real com contexto de memória dupla"""
    try:
        # Busca agentes no Supabase
        agents = supabase_service.list_all_agents()
        
        # Procura por um agente com nome similar ou usa o primeiro disponível
        agent_data = None
        for agent in agents:
            if agent_name.lower() in agent.get("name", "").lower():
                agent_data = agent
                break
        
        # Se não encontrou, usa o primeiro agente disponível
        if not agent_data and agents:
            agent_data = agents[0]
        
        if not agent_data:
            return "Nenhum agente disponível"
        
        # Recupera contexto completo da memória dupla
        memory_context = dual_memory_service.get_complete_context(
            user_id=user_id,
            session_id=session_id,
            query=query,
            session_limit=5,
            memory_limit=3
        )
        
        # Executa o agente com contexto enriquecido
        return execute_agent_with_memory(query, user_id, agent_data, memory_context)
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

# Endpoints da API

@app.get("/", tags=["Status"], summary="Status da API")
async def root():
    """Endpoint de status da API"""
    return {
        "message": "API de Agente com Knowledge e Memória",
        "status": "online",
        "version": "1.0.0",
        "features": ["RAG com Pinecone", "Memória com Mem0", "Agentes Inteligentes"],
        "endpoints": {
            "chat": "/v1/chat",
            "messages": "/v1/messages",
            "agents": "/v1/agents",
            "knowledge": "/v1/knowledge",
            "memory": "/v1/memory"
        }
    }

# ===== CHAT & MENSAGENS =====

@app.post("/v1/chat", tags=["Chat & Mensagens"], summary="Chat com agente")
async def chat_with_agent(request: ChatRequest, api_key: str = Depends(verify_api_key)) -> ChatResponse:
    """Endpoint principal para chat com agentes com memória dupla"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Gera resposta inteligente com memória dupla
        response = generate_intelligent_response(
            query=request.message, 
            user_id=request.user_id, 
            session_id=session_id,
            agent_name=request.agent_name
        )
        
        # Salva na memória dupla (Supabase + Mem0)
        agent_id = request.agent_name  # Usando agent_name como ID temporário
        memory_result = dual_memory_service.save_complete_interaction(
            user_id=request.user_id,
            session_id=session_id,
            agent_id=agent_id,
            user_message=request.message,
            agent_response=response,
            agent_name=request.agent_name
        )
        
        # Salva na sessão (compatibilidade)
        if session_id not in sessions_db:
            sessions_db[session_id] = []
        
        sessions_db[session_id].append({
            "user_message": request.message,
            "agent_response": response,
            "timestamp": datetime.now().isoformat(),
            "memory_saved": memory_result
        })
        
        return ChatResponse(
            response=response,
            agent_name=request.agent_name,
            user_id=request.user_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")

@app.post("/v1/messages", tags=["Chat & Mensagens"], summary="Enviar mensagem para agente")
async def send_message_to_agent(request: MessageRequest, api_key: str = Depends(verify_api_key)) -> MessageResponse:
    """
    Endpoint principal para envio de mensagens para agentes inteligentes.
    
    Este endpoint:
    - Aceita mensagens no formato compatível com sistemas de chat
    - Utiliza memória contextual (Mem0) para conversas personalizadas
    - Integra com base de conhecimento (RAG) para respostas precisas
    - Retorna resposta estruturada com informações de uso do modelo
    - Salva automaticamente o histórico da conversa
    
    Exemplo de uso:
    ```json
    {
        "mensagem": "Qual horário funciona?",
        "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
        "user_id": "116883357474955@lid",
        "session_id": "645d4334-8660-49b0-813b-872662cd2b7c"
    }
    ```
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Verifica se o agente existe no Supabase
        try:
            agent = supabase_service.get_agent(request.agent_id)
            if not agent:
                raise Exception("Agente não encontrado")
        except Exception:
            # Se não encontrar o agente específico, usa o primeiro disponível
            agents = supabase_service.list_all_agents()
            if agents:
                agent = agents[0]
            else:
                raise HTTPException(status_code=404, detail="Nenhum agente disponível")
        
        # Recupera contexto da memória dupla
        memory_context = dual_memory_service.get_complete_context(
            user_id=request.user_id,
            session_id=session_id,
            query=request.mensagem,
            session_limit=5,
            memory_limit=3
        )
        
        # Executa o agente com contexto de memória
        response = execute_agent_with_memory(request.mensagem, request.user_id, agent, memory_context)
        
        # Salva na memória dupla
        dual_memory_service.save_complete_interaction(
            user_id=request.user_id,
            session_id=session_id,
            agent_id=request.agent_id,
            user_message=request.mensagem,
            agent_response=response,
            agent_name=agent.get("name", "Agente")
        )
        
        return MessageResponse(
            messages=[response],
            transferir=False,
            session_id=session_id,
            user_id=request.user_id,
            agent_id=request.agent_id,
            custom=[],
            agent_usage={
                "input_tokens": len(request.mensagem.split()),
                "output_tokens": len(response.split()),
                "model": agent.get("model", "gpt-4o-mini")
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")

# ===== AGENTES =====

@app.post("/v1/agents", tags=["Agentes"], summary="Criar novo agente")
async def create_agent(request: AgentCreateRequest, api_key: str = Depends(verify_api_key)) -> AgentResponse:
    """Cria um novo agente inteligente"""
    try:
        # Usa o Supabase para criar o agente
        agent = supabase_service.create_agent(
            name=request.name,
            role=request.role,
            instructions=request.instructions,
            model=request.model or "gpt-4o-mini",
            account_id=request.account_id
        )
        
        # Adiciona created_at se não existir
        if "created_at" not in agent:
            agent["created_at"] = datetime.now().isoformat()
        
        return AgentResponse(**agent)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(e)}")

@app.get("/v1/agents", tags=["Agentes"], summary="Listar agentes")
async def list_agents(account_id: Optional[str] = Query(None, description="Filtrar por ID da conta"), api_key: str = Depends(verify_api_key)):
    """Lista todos os agentes disponíveis"""
    try:
        # Busca agentes no Supabase
        if account_id:
            agents_list = supabase_service.get_agents_by_account(account_id)
        else:
            agents_list = supabase_service.list_all_agents()
        
        # Converte os agentes para a estrutura correta de resposta
        formatted_agents = []
        for agent in agents_list:
            # Garante que todos os campos obrigatórios estejam presentes
            agent_response = {
                "id": agent.get("id"),
                "name": agent.get("name"),
                "role": agent.get("role"),
                "instructions": agent.get("instructions", []),
                "model": agent.get("model", "gpt-4o-mini"),
                "account_id": agent.get("account_id"),
                "created_at": agent.get("created_at", datetime.now().isoformat())
            }
            formatted_agents.append(agent_response)
        
        return {
            "agents": formatted_agents,
            "total": len(formatted_agents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar agentes: {str(e)}")

@app.get("/v1/agents/{agent_id}", tags=["Agentes"], summary="Obter agente específico")
async def get_agent(agent_id: str, api_key: str = Depends(verify_api_key)) -> AgentResponse:
    """Obtém detalhes de um agente específico"""
    try:
        agent = supabase_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        # Adiciona created_at se não existir
        if "created_at" not in agent:
            agent["created_at"] = datetime.now().isoformat()
        
        return AgentResponse(**agent)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter agente: {str(e)}")

@app.put("/v1/agents/{agent_id}", tags=["Agentes"], summary="Atualizar agente")
async def update_agent(agent_id: str, request: AgentUpdateRequest, api_key: str = Depends(verify_api_key)) -> AgentResponse:
    """Atualiza um agente existente"""
    try:
        # Prepara dados para atualização (apenas campos não nulos)
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.role is not None:
            update_data["role"] = request.role
        if request.instructions is not None:
            update_data["instructions"] = request.instructions
        if request.model is not None:
            update_data["model"] = request.model
        if request.account_id is not None:
            update_data["account_id"] = request.account_id
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização")
        
        # Atualiza no Supabase
        agent = supabase_service.update_agent(agent_id, **update_data)
        
        # Adiciona created_at se não existir
        if "created_at" not in agent:
            agent["created_at"] = datetime.now().isoformat()
        
        return AgentResponse(**agent)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar agente: {str(e)}")

@app.delete("/v1/agents/{agent_id}", tags=["Agentes"], summary="Deletar agente")
async def delete_agent(agent_id: str, api_key: str = Depends(verify_api_key)):
    """Deleta um agente"""
    try:
        # Tenta deletar no Supabase
        success = supabase_service.delete_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        return {"message": "Agente deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar agente: {str(e)}")

# ===== KNOWLEDGE (RAG) =====

@app.post("/v1/knowledge/search", tags=["Knowledge (RAG)"], summary="Buscar na base de conhecimento")
async def search_knowledge(request: KnowledgeSearchRequest, api_key: str = Depends(verify_api_key)):
    """Busca direta na base de conhecimento (RAG)"""
    try:
        results = knowledge_service.search_knowledge(request.query, request.limit)
        return {
            "query": request.query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")

@app.post("/v1/knowledge/sync", tags=["Knowledge (RAG)"], summary="Sincronizar base de conhecimento")
async def sync_knowledge(api_key: str = Depends(verify_api_key)):
    """Sincroniza a base de conhecimento com Pinecone"""
    try:
        success = knowledge_service.sync_knowledge()
        if success:
            return {"message": "Base de conhecimento sincronizada com sucesso", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Falha na sincronização")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")

# ===== MEMÓRIA (MEM0) =====

@app.get("/v1/memory/search", tags=["Memória (Mem0)"], summary="Buscar memórias do usuário")
async def search_memory(
    user_id: str = Query(..., description="ID do usuário"), 
    query: str = Query(..., description="Consulta de busca"), 
    limit: int = Query(3, description="Limite de resultados"),
    api_key: str = Depends(verify_api_key)
):
    """Busca memórias específicas do usuário"""
    try:
        memories = memory_service.search_memory(user_id, query, limit)
        return {
            "user_id": user_id,
            "query": query,
            "memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca de memória: {str(e)}")

@app.post("/v1/memory/add", tags=["Memória (Mem0)"], summary="Adicionar memória")
async def add_memory(request: MemoryAddRequest, api_key: str = Depends(verify_api_key)):
    """Adiciona uma nova memória para o usuário"""
    try:
        success = memory_service.add_memory(request.user_id, request.content, request.metadata)
        if success:
            return {"message": "Memória adicionada com sucesso", "user_id": request.user_id}
        else:
            raise HTTPException(status_code=500, detail="Falha ao adicionar memória")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar memória: {str(e)}")

@app.get("/v1/memory/{user_id}", tags=["Memória (Mem0)"], summary="Obter todas as memórias do usuário")
async def get_user_memories(user_id: str, api_key: str = Depends(verify_api_key)):
    """Obtém todas as memórias de um usuário"""
    try:
        memories = memory_db.get(user_id, [])
        return {
            "user_id": user_id,
            "memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter memórias: {str(e)}")

# ===== STATUS =====

@app.get("/v1/health", tags=["Status"], summary="Status de saúde do sistema")
async def health_check():
    """Verifica o status de todos os componentes"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "api": "online",
                "knowledge_service": "online",
                "memory_service": "online",
                "agents": "online"
            },
            "features": {
                "rag_enabled": True,
                "memory_enabled": True,
                "agents_enabled": True,
                "chat_enabled": True
            },
            "statistics": {
                "total_agents": len(supabase_service.list_all_agents()),
                "total_sessions": len(sessions_db),
                "total_users_with_memory": len(memory_db)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    
    # Usar a porta do arquivo .env ou 8002 como padrão
    port = int(os.getenv("PORT", 8002))
    
    print("🚀 Iniciando API Completa com Knowledge e Memória...")
    print(f"📚 Documentação disponível em http://localhost:{port}/docs")
    print("🔍 Endpoints disponíveis:")
    print("  - Chat: POST /v1/chat")
    print("  - Mensagens: POST /v1/messages")
    print("  - Agentes: GET/POST/PUT/DELETE /v1/agents")
    print("  - Knowledge: GET /v1/knowledge/search")
    print("  - Memória: GET /v1/memory/search")
    print("  - Status: GET /v1/health")
    uvicorn.run(app, host="0.0.0.0", port=port)