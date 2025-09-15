from typing import List, Dict, Any, Optional
from agno.agent import Agent
from agno.team import Team
from mem0 import MemoryClient
from agents import get_agent_by_name, get_all_agents
import uuid
from datetime import datetime

# Armazenamento em memória para times (em produção, usar banco de dados)
teams_storage: Dict[str, Dict[str, Any]] = {}

def create_team(name: str, description: str, agent_names: List[str], user_id: str = "default_user") -> Dict[str, Any]:
    """Cria um novo time com os agentes especificados"""
    try:
        # Busca os agentes pelos nomes
        agents = []
        for agent_name in agent_names:
            agent = get_agent_by_name(agent_name, user_id=user_id)
            if not agent:
                raise ValueError(f"Agente '{agent_name}' não encontrado")
            agents.append(agent)
        
        if not agents:
            raise ValueError("É necessário pelo menos um agente para criar um time")
        
        # Cria o time usando a classe Team do Agno
        team = Team(
            name=name,
            agents=agents,
            description=description
        )
        
        # Gera ID único para o time
        team_id = str(uuid.uuid4())
        
        # Armazena informações do time
        team_data = {
            "id": team_id,
            "name": name,
            "description": description,
            "agent_names": agent_names,
            "user_id": user_id,
            "team_instance": team,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        teams_storage[team_id] = team_data
        
        return {
            "id": team_id,
            "name": name,
            "description": description,
            "agents": agent_names,
            "user_id": user_id,
            "created_at": team_data["created_at"]
        }
        
    except Exception as e:
        raise Exception(f"Erro ao criar time: {str(e)}")

def get_all_teams(user_id: str = "default_user") -> List[Dict[str, Any]]:
    """Retorna todos os times do usuário"""
    user_teams = []
    for team_data in teams_storage.values():
        if team_data["user_id"] == user_id:
            user_teams.append({
                "id": team_data["id"],
                "name": team_data["name"],
                "description": team_data["description"],
                "agents": team_data["agent_names"],
                "created_at": team_data["created_at"],
                "updated_at": team_data["updated_at"]
            })
    return user_teams

def get_team_by_id(team_id: str, user_id: str = "default_user") -> Optional[Dict[str, Any]]:
    """Busca um time específico pelo ID"""
    team_data = teams_storage.get(team_id)
    if team_data and team_data["user_id"] == user_id:
        return {
            "id": team_data["id"],
            "name": team_data["name"],
            "description": team_data["description"],
            "agents": team_data["agent_names"],
            "created_at": team_data["created_at"],
            "updated_at": team_data["updated_at"]
        }
    return None

def get_team_instance_by_id(team_id: str, user_id: str = "default_user") -> Optional[Team]:
    """Retorna a instância do Team para execução"""
    team_data = teams_storage.get(team_id)
    if team_data and team_data["user_id"] == user_id:
        return team_data["team_instance"]
    return None

def update_team(team_id: str, name: Optional[str] = None, description: Optional[str] = None, 
                agent_names: Optional[List[str]] = None, user_id: str = "default_user") -> Optional[Dict[str, Any]]:
    """Atualiza um time existente"""
    team_data = teams_storage.get(team_id)
    if not team_data or team_data["user_id"] != user_id:
        return None
    
    try:
        # Atualiza os campos fornecidos
        if name is not None:
            team_data["name"] = name
        if description is not None:
            team_data["description"] = description
        
        if agent_names is not None:
            # Valida e atualiza agentes
            agents = []
            for agent_name in agent_names:
                agent = get_agent_by_name(agent_name, user_id=user_id)
                if not agent:
                    raise ValueError(f"Agente '{agent_name}' não encontrado")
                agents.append(agent)
            
            # Recria o team com novos agentes
            team_data["team_instance"] = Team(
                name=team_data["name"],
                agents=agents,
                description=team_data["description"]
            )
            team_data["agent_names"] = agent_names
        
        team_data["updated_at"] = datetime.now().isoformat()
        
        return {
            "id": team_data["id"],
            "name": team_data["name"],
            "description": team_data["description"],
            "agents": team_data["agent_names"],
            "updated_at": team_data["updated_at"]
        }
        
    except Exception as e:
        raise Exception(f"Erro ao atualizar time: {str(e)}")

def delete_team(team_id: str, user_id: str = "default_user") -> bool:
    """Remove um time"""
    team_data = teams_storage.get(team_id)
    if team_data and team_data["user_id"] == user_id:
        del teams_storage[team_id]
        return True
    return False

def run_team(team_id: str, message: str, user_id: str = "default_user") -> str:
    """Executa um time com uma mensagem"""
    team = get_team_instance_by_id(team_id, user_id)
    if not team:
        raise ValueError(f"Time com ID '{team_id}' não encontrado")
    
    try:
        # Busca memórias relevantes antes da execução
        print(f"[DEBUG] Iniciando busca de memória para team_id: {team_id}, user_id: {user_id}")
        memory_context = get_team_memory_context(team_id, user_id, message)
        
        # Adiciona contexto de memória à mensagem se houver
        enhanced_message = message
        if memory_context:
            enhanced_message = f"Contexto de conversas anteriores:\n{memory_context}\n\nMensagem atual: {message}"
            print(f"[DEBUG] Mensagem com contexto: {enhanced_message}")
        else:
            print(f"[DEBUG] Nenhum contexto de memória encontrado")
        
        response = team.run(enhanced_message)
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        # Salva a interação na memória Mem0
        save_team_memory(team_id, user_id, message, response_content)
        
        return response_content
    except Exception as e:
        raise Exception(f"Erro ao executar time: {str(e)}")

def get_team_memory_context(team_id: str, user_id: str, current_message: str) -> str:
    """Busca memórias relevantes do time para usar como contexto"""
    try:
        memory_client = MemoryClient()
        team_user_id = f"{user_id}_team_{team_id}"
        
        print(f"[DEBUG] Buscando memórias para team_user_id: {team_user_id}")
        print(f"[DEBUG] Query: {current_message}")
        
        # Busca memórias relevantes baseadas na mensagem atual
        memories = memory_client.search(query=current_message, user_id=team_user_id, limit=3)
        
        print(f"[DEBUG] Memórias encontradas: {len(memories) if memories else 0}")
        
        if not memories:
            print("[DEBUG] Nenhuma memória encontrada")
            return ""
        
        # Formata as memórias como contexto
        context_parts = []
        for memory in memories:
            context_parts.append(f"- {memory['memory']}")
            print(f"[DEBUG] Memória: {memory['memory']}")
        
        context = "\n".join(context_parts)
        print(f"[DEBUG] Contexto final: {context}")
        return context
    except Exception as e:
        print(f"Erro ao buscar memória do time: {e}")
        return ""

def save_team_memory(team_id: str, user_id: str, message: str, response: str):
    """Salva a interação do time na memória Mem0"""
    try:
        memory_client = MemoryClient()
        messages = [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
        # Usa um identificador único para o time
        team_user_id = f"{user_id}_team_{team_id}"
        memory_client.add(messages, user_id=team_user_id)
        return True
    except Exception as e:
        print(f"Erro ao salvar memória do time: {e}")
        return False