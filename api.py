from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import uuid
from agents import (
    get_all_agents, get_agent_by_name, get_agent_by_id, save_agent_memory,
    create_custom_agent, update_custom_agent, delete_custom_agent, get_custom_agents,
    custom_agents_storage
)
from teams import (
    create_team, get_all_teams, get_team_by_id, update_team, delete_team, run_team
)
from memory import memory_manager
from knowledge import knowledge_manager, get_knowledge_by_id, create_knowledge_base_with_config, delete_knowledge_base, add_source_to_knowledge
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração de autenticação
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
security = HTTPBearer()

async def verify_api_key(x_api_key: str = Header(None)):
    """Verifica se a X-API-Key é válida"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="X-API-Key header é obrigatório",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="X-API-Key inválida",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return x_api_key

class ChatRequest(BaseModel):
    message: str
    agent_name: Optional[str] = None
    user_id: Optional[str] = "default_user"

class HealthResponse(BaseModel):
    status: str
    message: str
    agents_count: int

class AgentResponse(BaseModel):
    name: str
    role: str
    instructions: List[str]
    user_id: str

class AgentCreateRequest(BaseModel):
    id: Optional[str] = Field(None, description="UUID opcional para o agente", example="550e8400-e29b-41d4-a716-446655440000")
    name: str = Field(..., description="Nome do agente", example="Assistente de Vendas")
    model: Dict[str, str] = Field(
        {"provider": "openai", "name": "gpt-4o-mini"}, 
        description="Configuração do modelo",
        example={"provider": "openai", "name": "gpt-4o-mini"}
    )
    system_message: str = Field(
        ..., 
        description="Mensagem de sistema do agente",
        example="Você é um assistente especializado em vendas. Seja sempre prestativo e profissional."
    )
    enable_user_memories: bool = Field(
        True, 
        description="Habilitar memórias do usuário",
        example=True
    )
    tools: List[str] = Field(
        ["DuckDuckGoTools"], 
        description="Ferramentas disponíveis",
        example=["DuckDuckGoTools"]
    )
    account_id: Optional[str] = Field(
        None, 
        description="UUID da conta para controle de acesso",
        example="f7dae33c-6364-4d88-908f-f5f64426a5c9"
    )

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    instructions: Optional[List[str]] = None

class TeamCreateRequest(BaseModel):
    id: Optional[str] = Field(None, description="UUID opcional para o time")
    name: str
    agents: List[str] = Field(..., description="Lista de IDs dos agentes")
    instructions: str = Field(..., description="Instruções para o time")
    account_id: Optional[str] = Field(None, description="UUID da conta para controle de acesso")

class TeamUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_names: Optional[List[str]] = None

class TeamRunRequest(BaseModel):
    team_id: str
    message: str
    user_id: Optional[str] = "default_user"

class MemorySearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = "default_user"
    limit: Optional[int] = 5

class MemoryAddRequest(BaseModel):
    messages: List[Dict[str, str]]
    user_id: Optional[str] = "default_user"
    metadata: Optional[Dict[str, Any]] = None

class KnowledgeSearchRequest(BaseModel):
    query: str
    knowledge_id: Optional[str] = "produto"
    limit: Optional[int] = 5

class KnowledgeSourceRequest(BaseModel):
    knowledge_id: str
    source_id: str
    source_type: str
    config: Dict[str, Any]

class KnowledgeCreateRequest(BaseModel):
    id: Optional[str] = Field(None, description="UUID opcional para o conhecimento")
    type: str = Field("text", description="Tipo do conhecimento")
    name: str = Field(..., description="Nome do conhecimento")
    description: str = Field(..., description="Descrição do conhecimento")
    content: Optional[str] = Field(None, description="Conteúdo do conhecimento")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados")
    reader: str = Field("default", description="Leitor padrão")
    chunker: str = Field("default", description="Chunker padrão")
    vectordb: Optional[Dict[str, Any]] = None
    sources: List[Dict[str, Any]] = []

class AgentRunRequest(BaseModel):
    message: str = Field(
        ..., 
        description="Mensagem para o agente",
        example="Qual é o futuro da IA?"
    )
    user_id: str = Field(
        ..., 
        description="ID do usuário para mensagens",
        example="user_especifico_456"
    )
    session_id: Optional[str] = Field(
        None, 
        description="ID da sessão",
        example="session_123"
    )

class TeamRunRequest2(BaseModel):
    message: str = Field(..., description="Mensagem para o time")
    user_id: str = Field(..., description="ID do usuário para mensagens")
    session_id: Optional[str] = Field(None, description="ID da sessão")

class MCPRequest(BaseModel):
    action: str = Field(..., description="Ação MCP a ser executada")
    user_id: Optional[str] = Field("default_user", description="ID do usuário")
    content: Optional[str] = Field(None, description="Conteúdo da memória")
    topic: Optional[str] = Field(None, description="Tópico da memória")
    memory_id: Optional[str] = Field(None, description="ID da memória")
    query: Optional[str] = Field(None, description="Query de busca")
    limit: Optional[int] = Field(5, description="Limite de resultados")

def create_api_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI"""
    app = FastAPI(
        title="AgentOS API",
        description="API para gerenciamento de agentes inteligentes com memória persistente",
        version="1.0.0",
        openapi_tags=[
            {
                "name": "Health",
                "description": "Verificação de saúde da API"
            },
            {
                "name": "Agentes",
                "description": "Operações relacionadas aos agentes de IA"
            },
            {
                "name": "Times",
                "description": "Gerenciamento de times de agentes"
            },
            {
                "name": "Chat",
                "description": "Interações de chat com agentes e times"
            },
            {
                "name": "Memória",
                "description": "Gerenciamento de memória persistente"
            },
            {
                "name": "Base de Conhecimento",
                "description": "Operações de RAG com Pinecone"
            }
        ]
    )

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Endpoint de verificação de saúde da API (sem autenticação para Docker health check)"""
        agents = get_all_agents()
        return HealthResponse(
            status="healthy",
            message="AgentOS API está funcionando corretamente",
            agents_count=len(agents)
        )

    async def chat_with_agent(agent_name: str, request: ChatRequest):
        """Função auxiliar para chat com agente"""
        try:
            # Busca o agente pelo nome
            user_id = request.user_id or "default_user"
            agent = get_agent_by_name(agent_name, user_id=user_id)
            
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agente '{agent_name}' não encontrado")
            
            # Executa o agente com a mensagem
            response = agent.run(request.message)
            
            # Extrai o conteúdo da resposta
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Salva a interação na memória Mem0
            messages = [
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": response_content}
            ]
            save_agent_memory(user_id, messages)
            
            return response_content
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro no chat com agente {agent_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

    @app.post("/chat", tags=["Chat"])
    async def chat_endpoint(request: ChatRequest, api_key: str = Depends(verify_api_key)):
        """Endpoint principal para chat com agentes"""
        user_id = request.user_id or "default_user"
        response_content = await chat_with_agent(request.agent_name or "Assistente Principal", request)
        return {"message": "Chat realizado com sucesso", "response": response_content, "user_id": user_id}

    # Endpoints CRUD para Agentes
    @app.post("/agents", summary="Criar novo agente", tags=["Agentes"],
              responses={
                  200: {
                      "description": "Agente criado com sucesso",
                      "content": {
                          "application/json": {
                              "example": {
                                  "message": "Agente criado com sucesso",
                                  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
                                  "name": "Assistente de Vendas"
                              }
                          }
                      }
                  }
              })
    async def create_agent(request: AgentCreateRequest, api_key: str = Depends(verify_api_key)):
        """Cria um novo agente personalizado"""
        try:
            # Gera UUID se não fornecido
            agent_id = request.id or str(uuid.uuid4())
            
            agent = create_custom_agent(
                agent_id=agent_id,
                name=request.name,
                model=request.model,
                system_message=request.system_message,
                enable_user_memories=request.enable_user_memories,
                tools=request.tools,
                # Valores padrão para campos removidos
                add_history_to_context=True,
                num_history_runs=5,
                add_datetime_to_context=True,
                markdown=True,
                user_id=request.account_id or "default_user"
            )
            return {
                "message": "Agente criado com sucesso",
                "agent": {
                    "id": agent_id,
                    "name": request.name,
                    "model": request.model,
                    "system_message": request.system_message,
                    "enable_user_memories": request.enable_user_memories,
                    "tools": request.tools,
                    "account_id": request.account_id
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents", summary="Listar todos os agentes", tags=["Agentes"])
    async def list_agents(account_id: str = None, api_key: str = Depends(verify_api_key)):
        """Lista todos os agentes (padrão + personalizados) filtrados por account_id"""
        try:
            # Agentes padrão
            default_agents = get_all_agents(account_id=account_id)
            default_agents_data = []
            for agent in default_agents:
                default_agents_data.append({
                    "name": agent.config.name,
                    "role": getattr(agent, 'role', 'Agente'),
                    "instructions": getattr(agent, 'instructions', []),
                    "account_id": account_id,
                    "type": "default"
                })
            
            # Agentes personalizados
            from agents import custom_agents_storage
            custom_agents_data = []
            for agent_key, agent_data in custom_agents_storage.items():
                if not account_id or agent_data.get("account_id") == account_id:
                    custom_agents_data.append({
                        "id": agent_data.get("id", agent_key),
                        "name": agent_data["name"],
                        "role": agent_data.get("role", "Agente Personalizado"),
                        "instructions": agent_data.get("instructions", []),
                        "account_id": agent_data.get("account_id"),
                        "type": "custom",
                        "model": agent_data.get("model", {}),
                        "system_message": agent_data.get("system_message", ""),
                        "tools": agent_data.get("tools", [])
                    })
            
            return {
                "default_agents": default_agents_data,
                "custom_agents": custom_agents_data,
                "total": len(default_agents_data) + len(custom_agents_data)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents/{agent_id}", summary="Buscar agente específico", tags=["Agentes"])
    async def get_agent(agent_id: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Busca um agente específico pelo ID"""
        try:
            # Primeiro verifica nos agentes personalizados
            from agents import custom_agents_storage
            for agent_key, agent_data in custom_agents_storage.items():
                if agent_data.get("id") == agent_id and agent_data["user_id"] == user_id:
                    return {
                        "id": agent_data.get("id", agent_key),
                        "name": agent_data["name"],
                        "role": agent_data.get("role", "Agente Personalizado"),
                        "model": agent_data.get("model", {"provider": "openai", "name": "gpt-4o-mini"}),
                        "system_message": agent_data.get("system_message", ""),
                        "instructions": agent_data.get("instructions", []),
                        "enable_user_memories": agent_data.get("enable_user_memories", True),
                        "tools": agent_data.get("tools", ["DuckDuckGoTools"]),
                        "add_history_to_context": agent_data.get("add_history_to_context", True),
                        "num_history_runs": agent_data.get("num_history_runs", 5),
                        "add_datetime_to_context": agent_data.get("add_datetime_to_context", True),
                        "markdown": agent_data.get("markdown", True),
                        "user_id": user_id,
                        "type": "custom"
                    }
            
            # Se não encontrou nos personalizados, busca nos padrão
            agent = get_agent_by_id(agent_id, user_id=user_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agente não encontrado")
            
            return {
                "id": agent_id,
                "name": getattr(agent, 'name', getattr(agent.config, 'name', 'Agente Padrão')),
                "role": "Agente Padrão",
                "model": {"provider": "openai", "name": "gpt-4o-mini"},
                "system_message": getattr(agent, 'system_message', ''),
                "instructions": getattr(agent, 'instructions', []),
                "enable_user_memories": True,
                "tools": ["DuckDuckGoTools"],
                "add_history_to_context": True,
                "num_history_runs": 5,
                "add_datetime_to_context": True,
                "markdown": True,
                "user_id": user_id,
                "type": "default"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/agents/{agent_id}", summary="Atualizar agente", tags=["Agentes"])
    async def update_agent(agent_id: str, request: AgentUpdateRequest, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Atualiza um agente personalizado existente"""
        try:
            # Primeiro, encontra o agente pelo ID para obter o nome atual
            agent_found = None
            agent_name = None
            for agent_key, agent_data in custom_agents_storage.items():
                if agent_data["user_id"] == user_id and agent_data["id"] == agent_id:
                    agent_found = agent_data
                    agent_name = agent_data["name"]
                    break
            
            if not agent_found:
                raise HTTPException(status_code=404, detail="Agente não encontrado")
            
            updated_agent = update_custom_agent(
                name=agent_name,
                new_name=request.name,
                role=request.role,
                instructions=request.instructions,
                user_id=user_id
            )
            
            if not updated_agent:
                raise HTTPException(status_code=404, detail="Agente não encontrado ou não é personalizável")
            
            return {
                "message": "Agente atualizado com sucesso",
                "agent": {
                    "id": agent_id,
                    "name": updated_agent.config.name,
                    "role": getattr(updated_agent, 'role', 'Agente'),
                    "instructions": getattr(updated_agent, 'instructions', []),
                    "user_id": user_id
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/agents/{agent_id}", summary="Remover agente", tags=["Agentes"])
    async def delete_agent(agent_id: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Remove um agente personalizado"""
        try:
            success = delete_custom_agent(agent_id, user_id=user_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Agente não encontrado ou não é personalizável")
            
            return {"message": f"Agente '{agent_id}' removido com sucesso"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/agents/{agent_id}/run", summary="Executar agente", tags=["Agentes"],
              responses={
                  200: {
                      "description": "Resposta do agente",
                      "content": {
                          "application/json": {
                              "example": {
                                  "messages": ["Olá! Como posso ajudá-lo hoje?"],
                                  "transferir": False,
                                  "session_id": "session_123",
                                  "user_id": "user_especifico_456",
                                  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
                                  "custom": [],
                                  "agent_usage": {
                                      "input_tokens": 15,
                                      "output_tokens": 8,
                                      "model": "gpt-4o-mini"
                                  }
                              }
                          }
                      }
                  }
              })
    async def run_agent(agent_id: str, request: AgentRunRequest, api_key: str = Depends(verify_api_key)):
        """Executa um agente específico com uma mensagem"""
        try:
            agent = get_agent_by_id(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agente não encontrado")
            
            # Executa o agente apenas com a mensagem
            response = agent.run(request.message)
            
            # Extrai o conteúdo da resposta se for um objeto
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "messages": [response_content],
                "transferir": False,
                "session_id": request.session_id,
                "user_id": request.user_id,
                "agent_id": agent_id,
                "custom": [],
                "agent_usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "model": "gpt-4o-mini"
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Endpoints CRUD para Teams
    @app.post("/teams", summary="Criar novo time", tags=["Times"])
    async def create_new_team(request: TeamCreateRequest, api_key: str = Depends(verify_api_key)):
        """Cria um novo time de agentes"""
        try:
            team = create_team(
                name=request.name,
                description=request.instructions,  # Usando instructions como description
                agent_names=request.agents,  # Usando agents como agent_names
                user_id=request.user_id
            )
            
            if not team:
                raise HTTPException(status_code=400, detail="Erro ao criar time. Verifique se todos os agentes existem.")
            
            return {
                "message": "Time criado com sucesso",
                "team": {
                    "name": request.name,
                    "instructions": request.instructions,
                    "agents": request.agents,
                    "user_id": request.user_id
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/teams", summary="Listar todos os times", tags=["Times"])
    async def list_teams(account_id: str = None, api_key: str = Depends(verify_api_key)):
        """Lista todos os times filtrados por account_id"""
        try:
            teams = get_all_teams(account_id=account_id)
            teams_data = []
            
            for team_data in teams:
                 teams_data.append({
                     "id": team_data["id"],
                     "name": team_data["name"],
                     "description": team_data["description"],
                     "agent_names": team_data["agents"],
                     "account_id": team_data.get("account_id")
                 })
            
            return {
                "teams": teams_data,
                "total": len(teams_data)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/teams/{team_id}", summary="Buscar time específico", tags=["Times"])
    async def get_team(team_id: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Busca um time específico pelo ID"""
        try:
            team = get_team_by_id(team_id, user_id=user_id)
            if not team:
                raise HTTPException(status_code=404, detail="Time não encontrado")
            
            return {
                "id": team["id"],
                "name": team["name"],
                "description": team["description"],
                "agent_names": team["agents"],
                "user_id": user_id
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/teams/{team_id}", summary="Atualizar time", tags=["Times"])
    async def update_existing_team(team_id: str, request: TeamUpdateRequest, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
         """Atualiza um time existente"""
         try:
             updated_team = update_team(
                 team_id=team_id,
                 name=request.name,
                 description=request.description,
                 agent_names=request.agent_names,
                 user_id=user_id
             )
             
             if not updated_team:
                 raise HTTPException(status_code=404, detail="Time não encontrado")
             
             return {
                 "message": "Time atualizado com sucesso",
                 "team": {
                     "id": updated_team["id"],
                     "name": updated_team["name"],
                     "description": updated_team["description"],
                     "agent_names": updated_team["agent_names"],
                     "user_id": updated_team["user_id"]
                 }
             }
         except HTTPException:
             raise
         except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/teams/{team_id}", summary="Deletar time", tags=["Times"])
    async def delete_existing_team(team_id: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
         """Remove um time"""
         try:
             success = delete_team(team_id, user_id=user_id)
             
             if not success:
                 raise HTTPException(status_code=404, detail="Time não encontrado")
             
             return {"message": f"Time removido com sucesso"}
         except HTTPException:
             raise
         except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

    @app.post("/teams/{team_id}/run", summary="Executar time", tags=["Times"])
    async def run_team_endpoint(team_id: str, request: TeamRunRequest2, api_key: str = Depends(verify_api_key)):
        """Executa um time específico com uma mensagem"""
        try:
            team = get_team_by_id(team_id)
            if not team:
                raise HTTPException(status_code=404, detail="Time não encontrado")
            
            # Executa o time apenas com a mensagem
            response = run_team(team_id, request.message)
            
            # Extrai o conteúdo da resposta se for um objeto
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "messages": [response_content],
                "transferir": False,
                "session_id": request.session_id,
                "user_id": request.user_id,
                "team_id": team_id,
                "custom": [],
                "team_usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "model": "gpt-4o-mini"
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/memory/search", summary="Buscar memórias", tags=["Memória"])
    async def search_memories(user_id: str = "default_user", query: str = "", limit: int = 5, api_key: str = Depends(verify_api_key)):
        """Busca memórias relevantes para o usuário"""
        try:
            if not query:
                raise HTTPException(status_code=400, detail="Query é obrigatória")
            
            memories = memory_manager.search_memories(user_id, query, limit)
            return {
                "user_id": user_id,
                "query": query,
                "memories": memories,
                "total": len(memories)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/memory/all", summary="Listar todas as memórias", tags=["Memória"])
    async def get_all_memories(user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Recupera todas as memórias de um usuário"""
        try:
            memories = memory_manager.get_all_memories(user_id)
            return {
                "user_id": user_id,
                "memories": memories,
                "total": len(memories)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/memory/add", summary="Adicionar memória", tags=["Memória"])
    async def add_memory(request: MemoryAddRequest, api_key: str = Depends(verify_api_key)):
        """Adiciona uma nova memória para o usuário"""
        try:
            success = memory_manager.add_memory(
                user_id=request.user_id,
                messages=request.messages,
                metadata=request.metadata
            )
            
            if success:
                return {
                    "message": "Memória adicionada com sucesso",
                    "user_id": request.user_id
                }
            else:
                raise HTTPException(status_code=500, detail="Falha ao adicionar memória")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Endpoints para Base de Conhecimento
    @app.get("/knowledge", summary="Listar bases de conhecimento", tags=["Base de Conhecimento"])
    async def list_knowledge_bases(api_key: str = Depends(verify_api_key)):
        """Lista todas as bases de conhecimento disponíveis"""
        try:
            bases = knowledge_manager.list_knowledge_bases()
            return {
                "knowledge_bases": bases,
                "total": len(bases)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/knowledge/search", summary="Buscar na base de conhecimento", tags=["Base de Conhecimento"])
    async def search_knowledge(request: KnowledgeSearchRequest, api_key: str = Depends(verify_api_key)):
        """Realiza busca semântica na base de conhecimento"""
        try:
            results = knowledge_manager.search_knowledge(
                query=request.query,
                knowledge_id=request.knowledge_id,
                limit=request.limit
            )
            return {
                "query": request.query,
                "knowledge_id": request.knowledge_id,
                "results": results,
                "total": len(results)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/knowledge/sync", summary="Sincronizar base de conhecimento", tags=["Base de Conhecimento"])
    async def sync_knowledge(knowledge_id: str = "produto", api_key: str = Depends(verify_api_key)):
        """Sincroniza uma base de conhecimento com suas fontes"""
        try:
            success = knowledge_manager.sync_knowledge_base(knowledge_id)
            return {
                "message": f"Base de conhecimento '{knowledge_id}' sincronizada com sucesso",
                "knowledge_id": knowledge_id,
                "success": success
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/knowledge/sources", summary="Adicionar fonte à base de conhecimento", tags=["Base de Conhecimento"])
    async def add_knowledge_source(request: KnowledgeSourceRequest, api_key: str = Depends(verify_api_key)):
        """Adiciona uma nova fonte de dados à base de conhecimento"""
        try:
            source_config = {
                "id": request.source_id,
                "type": request.source_type,
                "config": request.config
            }
            success = knowledge_manager.add_knowledge_source(request.knowledge_id, source_config)
            return {
                "message": f"Fonte '{request.source_id}' adicionada à base '{request.knowledge_id}'",
                "knowledge_id": request.knowledge_id,
                "source_id": request.source_id,
                "success": success
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/knowledge/{knowledge_id}", summary="Buscar conhecimento específico", tags=["Base de Conhecimento"])
    async def get_knowledge(knowledge_id: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Busca uma base de conhecimento específica pelo ID"""
        try:
            knowledge = get_knowledge_by_id(knowledge_id, user_id=user_id)
            if not knowledge:
                raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
            
            return {
                "id": knowledge_id,
                "type": getattr(knowledge, 'type', 'text'),
                "name": knowledge.config.name,
                "description": getattr(knowledge, 'description', ''),
                "content": getattr(knowledge, 'content', ''),
                "metadata": getattr(knowledge, 'metadata', {}),
                "reader": getattr(knowledge, 'reader', 'default'),
                "chunker": getattr(knowledge, 'chunker', 'default'),
                "sources": [source.config.path for source in knowledge.sources],
                "user_id": user_id
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/knowledge/{knowledge_id}/sync", summary="Sincronizar conhecimento", tags=["Base de Conhecimento"])
    async def sync_knowledge_specific(knowledge_id: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Sincroniza uma base de conhecimento específica"""
        try:
            knowledge = get_knowledge_by_id(knowledge_id, user_id=user_id)
            if not knowledge:
                raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
            
            # Sincroniza a base de conhecimento
            knowledge.sync()
            
            return {
                "message": f"Base de conhecimento '{knowledge_id}' sincronizada com sucesso",
                "knowledge_id": knowledge_id,
                "user_id": user_id
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/knowledge/{knowledge_id}/sources", summary="Adicionar fonte ao conhecimento", tags=["Base de Conhecimento"])
    async def add_knowledge_source_specific(knowledge_id: str, request: KnowledgeSourceRequest, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Adiciona uma nova fonte a uma base de conhecimento existente"""
        try:
            knowledge = get_knowledge_by_id(knowledge_id, user_id=user_id)
            if not knowledge:
                raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
            
            # Adiciona a nova fonte
            success = add_source_to_knowledge(
                knowledge_id=knowledge_id,
                source_path=request.source_path,
                source_type=request.source_type,
                user_id=user_id
            )
            
            if not success:
                raise HTTPException(status_code=400, detail="Falha ao adicionar fonte")
            
            return {
                "message": "Fonte adicionada com sucesso",
                "knowledge_id": knowledge_id,
                "source_path": request.source_path,
                "user_id": user_id
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/knowledge/{knowledge_id}", summary="Atualizar conhecimento", tags=["Base de Conhecimento"])
    async def update_knowledge(knowledge_id: str, request: KnowledgeCreateRequest, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Atualiza uma base de conhecimento existente"""
        try:
            knowledge = get_knowledge_by_id(knowledge_id, user_id=user_id)
            if not knowledge:
                raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
            
            # Atualiza os campos fornecidos
            if request.name:
                knowledge.config.name = request.name
            if request.description:
                setattr(knowledge, 'description', request.description)
            if request.content:
                setattr(knowledge, 'content', request.content)
            if request.metadata:
                setattr(knowledge, 'metadata', request.metadata)
            
            return {
                "message": "Base de conhecimento atualizada com sucesso",
                "knowledge_id": knowledge_id,
                "user_id": user_id
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/knowledge/{knowledge_id}", summary="Remover conhecimento", tags=["Base de Conhecimento"])
    async def delete_knowledge(knowledge_id: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Remove uma base de conhecimento"""
        try:
            success = delete_knowledge_base(knowledge_id, user_id=user_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
            
            return {"message": f"Base de conhecimento '{knowledge_id}' removida com sucesso"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/knowledge", summary="Criar nova base de conhecimento", tags=["Base de Conhecimento"])
    async def create_knowledge_base(request: KnowledgeCreateRequest, api_key: str = Depends(verify_api_key)):
        """Cria uma nova base de conhecimento"""
        try:
            knowledge_id = request.id or str(uuid.uuid4())
            
            config = {
                "name": request.name,
                "type": request.type,
                "description": request.description,
                "content": request.content,
                "metadata": request.metadata,
                "reader": request.reader,
                "chunker": request.chunker,
                "vectordb": request.vectordb or {
                    "provider": "pinecone",
                    "config": {
                        "index": "agno-knowledge-base",
                        "environment": "gcp-starter"
                    }
                },
                "sources": request.sources or []
            }
            
            success = create_knowledge_base_with_config(knowledge_id, config)
            
            return {
                "id": knowledge_id,
                "message": f"Base de conhecimento '{knowledge_id}' criada com sucesso",
                "success": success
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/mcp", summary="Operações MCP para memórias", tags=["Memória"])
    async def mcp_endpoint(request: MCPRequest, api_key: str = Depends(verify_api_key)):
        """Endpoint para operações MCP (Model Context Protocol) relacionadas à memória"""
        try:
            user_id = request.user_id or "default_user"
            
            if request.action == "add_memory":
                if not request.content:
                    raise HTTPException(status_code=400, detail="Conteúdo é obrigatório para adicionar memória")
                
                messages = [{"role": "user", "content": request.content}]
                metadata = {"topic": request.topic} if request.topic else None
                
                success = memory_manager.add_memory(
                    user_id=user_id,
                    messages=messages,
                    metadata=metadata
                )
                
                return {
                    "action": "add_memory",
                    "success": success,
                    "user_id": user_id,
                    "message": "Memória adicionada com sucesso" if success else "Falha ao adicionar memória"
                }
            
            elif request.action == "search_memory":
                if not request.query:
                    raise HTTPException(status_code=400, detail="Query é obrigatória para buscar memórias")
                
                memories = memory_manager.search_memories(
                    user_id=user_id,
                    query=request.query,
                    limit=request.limit or 5
                )
                
                return {
                    "action": "search_memory",
                    "user_id": user_id,
                    "query": request.query,
                    "memories": memories,
                    "total": len(memories)
                }
            
            elif request.action == "get_all_memories":
                memories = memory_manager.get_all_memories(user_id)
                
                return {
                    "action": "get_all_memories",
                    "user_id": user_id,
                    "memories": memories,
                    "total": len(memories)
                }
            
            elif request.action == "delete_memory":
                if not request.memory_id:
                    raise HTTPException(status_code=400, detail="ID da memória é obrigatório para deletar")
                
                success = memory_manager.delete_memory(user_id, request.memory_id)
                
                return {
                    "action": "delete_memory",
                    "success": success,
                    "user_id": user_id,
                    "memory_id": request.memory_id,
                    "message": "Memória removida com sucesso" if success else "Falha ao remover memória"
                }
            
            else:
                raise HTTPException(status_code=400, detail=f"Ação '{request.action}' não suportada")
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

# Instância global da aplicação para uvicorn
app = create_api_app()

if __name__ == "__main__":
    import uvicorn
    from config import Config
    
    server_config = Config.get_server_config()
    print(f"🚀 Iniciando AgentOS API em http://{server_config['host']}:{server_config['port']}")
    print(f"📚 Documentação disponível em http://{server_config['host']}:{server_config['port']}/docs")
    
    uvicorn.run(
        "api:app",
        host=server_config['host'],
        port=server_config['port'],
        reload=True
    )