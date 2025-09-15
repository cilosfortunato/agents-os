from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from agents import (
    get_all_agents, get_agent_by_name, save_agent_memory,
    create_custom_agent, update_custom_agent, delete_custom_agent, get_custom_agents
)
from teams import (
    create_team, get_all_teams, get_team_by_id, update_team, delete_team, run_team
)
from memory import memory_manager
from knowledge import knowledge_manager
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
    name: str
    role: str
    instructions: List[str]
    user_id: Optional[str] = "default_user"

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    instructions: Optional[List[str]] = None

class TeamCreateRequest(BaseModel):
    name: str
    description: str
    agent_names: List[str]
    user_id: Optional[str] = "default_user"

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
    knowledge_id: str
    vectordb: Optional[Dict[str, Any]] = None
    sources: List[Dict[str, Any]] = []

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
    async def health_check(api_key: str = Depends(verify_api_key)):
        """Endpoint de verificação de saúde da API"""
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
    @app.post("/agents", summary="Criar novo agente", tags=["Agentes"])
    async def create_agent(request: AgentCreateRequest, api_key: str = Depends(verify_api_key)):
        """Cria um novo agente personalizado"""
        try:
            agent = create_custom_agent(
                name=request.name,
                role=request.role,
                instructions=request.instructions,
                user_id=request.user_id
            )
            return {
                "message": "Agente criado com sucesso",
                "agent": {
                    "name": request.name,
                    "role": request.role,
                    "instructions": request.instructions,
                    "user_id": request.user_id
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents", summary="Listar todos os agentes", tags=["Agentes"])
    async def list_agents(user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Lista todos os agentes (padrão + personalizados)"""
        try:
            # Agentes padrão
            default_agents = get_all_agents(user_id=user_id)
            default_agents_data = []
            for agent in default_agents:
                default_agents_data.append({
                    "name": agent.config.name,
                    "role": getattr(agent, 'role', 'Agente'),
                    "instructions": getattr(agent, 'instructions', []),
                    "user_id": user_id,
                    "type": "default"
                })
            
            # Agentes personalizados
            custom_agents = get_custom_agents(user_id=user_id)
            custom_agents_data = []
            for agent in custom_agents:
                custom_agents_data.append({
                    "name": agent.config.name,
                    "role": agent.role,
                    "instructions": getattr(agent, 'instructions', []),
                    "user_id": user_id,
                    "type": "custom"
                })
            
            return {
                "default_agents": default_agents_data,
                "custom_agents": custom_agents_data,
                "total": len(default_agents_data) + len(custom_agents_data)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents/{agent_name}", summary="Buscar agente específico", tags=["Agentes"])
    async def get_agent(agent_name: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Busca um agente específico pelo nome"""
        try:
            agent = get_agent_by_name(agent_name, user_id=user_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agente não encontrado")
            
            return {
                "name": agent.config.name,
                "role": getattr(agent, 'role', 'Agente'),
                "instructions": getattr(agent, 'instructions', []),
                "user_id": user_id
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/agents/{agent_name}", summary="Atualizar agente", tags=["Agentes"])
    async def update_agent(agent_name: str, request: AgentUpdateRequest, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Atualiza um agente personalizado existente"""
        try:
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
                    "name": updated_agent.config.name,
                    "role": updated_agent.role,
                    "instructions": getattr(updated_agent, 'instructions', []),
                    "user_id": user_id
                }
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/agents/{agent_name}", summary="Remover agente", tags=["Agentes"])
    async def delete_agent(agent_name: str, user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Remove um agente personalizado"""
        try:
            success = delete_custom_agent(agent_name, user_id=user_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Agente não encontrado ou não é personalizável")
            
            return {"message": f"Agente '{agent_name}' removido com sucesso"}
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
                description=request.description,
                agent_names=request.agent_names,
                user_id=request.user_id
            )
            
            if not team:
                raise HTTPException(status_code=400, detail="Erro ao criar time. Verifique se todos os agentes existem.")
            
            return {
                "message": "Time criado com sucesso",
                "team": {
                    "name": request.name,
                    "description": request.description,
                    "agent_names": request.agent_names,
                    "user_id": request.user_id
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/teams", summary="Listar todos os times", tags=["Times"])
    async def list_teams(user_id: str = "default_user", api_key: str = Depends(verify_api_key)):
        """Lista todos os times do usuário"""
        try:
            teams = get_all_teams(user_id=user_id)
            teams_data = []
            
            for team_data in teams:
                 teams_data.append({
                     "id": team_data["id"],
                     "name": team_data["name"],
                     "description": team_data["description"],
                     "agent_names": team_data["agents"],
                     "user_id": team_data.get("user_id", "default_user")
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

    @app.post("/teams/run", summary="Executar time", tags=["Chat"])
    async def run_team_endpoint(request: TeamRunRequest, api_key: str = Depends(verify_api_key)):
        """Executa um time com uma mensagem"""
        try:
            response = run_team(
                team_id=request.team_id,
                message=request.message,
                user_id=request.user_id
            )
            
            if not response:
                raise HTTPException(status_code=404, detail="Time não encontrado")
            
            return {
                "message": "Time executado com sucesso",
                "team_id": request.team_id,
                "response": response,
                "user_id": request.user_id
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
    
    @app.post("/knowledge/create", summary="Criar nova base de conhecimento", tags=["Base de Conhecimento"])
    async def create_knowledge_base(request: KnowledgeCreateRequest, api_key: str = Depends(verify_api_key)):
        """Cria uma nova base de conhecimento"""
        try:
            config = {
                "vectordb": request.vectordb or {
                    "provider": "pinecone",
                    "config": {
                        "index": "agno-knowledge-base",
                        "environment": "gcp-starter"
                    }
                },
                "sources": request.sources
            }
            success = knowledge_manager.create_knowledge_base(request.knowledge_id, config)
            return {
                "message": f"Base de conhecimento '{request.knowledge_id}' criada com sucesso",
                "knowledge_id": request.knowledge_id,
                "success": success
            }
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