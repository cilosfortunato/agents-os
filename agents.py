import os
import json
from typing import List
from config import Config

try:
    from agno.agent import Agent
    from agno.models.openrouter import OpenRouterModel
    from agno.tools.duckduckgo import DuckDuckGoTools
    AGNO_AVAILABLE = True
    print("✅ Agno importado com sucesso!")
except ImportError as e:
    print(f"Agno não está disponível: {e}. Usando implementação mock para desenvolvimento.")
    AGNO_AVAILABLE = False

# Classes mock para quando agno não estiver disponível
class MockModel:
    def __init__(self, model_id=None, api_key=None):
        self.model_id = model_id or "mock-model"
        self.api_key = api_key
    
    def __call__(self, *args, **kwargs):
        return "Resposta mock do modelo"

class MockConfig:
    def __init__(self, name=None):
        self.name = name or "Mock Agent"

class MockAgent:
    def __init__(self, name=None, model=None, instructions=None, tools=None, markdown=True, **kwargs):
        self.name = name or "Mock Agent"
        self.model = model
        self.instructions = instructions or []
        self.tools = tools or []
        self.markdown = markdown
        self.config = MockConfig(name=self.name)
    
    def run(self, *args, **kwargs):
        return f"Resposta mock do agente {self.name}"

class MockDuckDuckGoTools:
    def __init__(self):
        self.name = "Mock DuckDuckGo Tools"
    
    def search(self, query):
        return f"Resultado mock da pesquisa para: {query}"

def create_model():
    """Cria uma instância do modelo OpenAI via OpenRouter configurado"""
    if AGNO_AVAILABLE:
        try:
            return OpenRouterModel(
                model_id="openai/gpt-4o-mini",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
        except NameError:
            print("OpenRouterModel não disponível, usando mock")
            return MockModel("openai/gpt-4o-mini", os.getenv("OPENAI_API_KEY"))
    else:
        return MockModel("openai/gpt-4o-mini", os.getenv("OPENAI_API_KEY"))

def create_assistente_principal():
    """Cria o agente assistente principal usando AgentOS"""
    AgentClass = Agent if AGNO_AVAILABLE else MockAgent
    return AgentClass(
        name="Assistente Principal",
        model=create_model(),
        instructions=[
            "Você é um assistente inteligente e prestativo.",
            "Seja cordial, profissional e sempre tente ajudar da melhor forma possível.",
            "Se não souber algo, seja honesto e sugira alternativas.",
            "Responda de forma clara e objetiva."
        ],
        markdown=True
    )

def create_agente_pesquisa():
    """Cria o agente especializado em pesquisa usando AgentOS"""
    AgentClass = Agent if AGNO_AVAILABLE else MockAgent
    ToolsClass = DuckDuckGoTools if AGNO_AVAILABLE else MockDuckDuckGoTools
    return AgentClass(
        name="Agente de Pesquisa",
        model=create_model(),
        instructions=[
            "Você é um especialista em pesquisa e análise de informações.",
            "Use o DuckDuckGo para buscar informações atualizadas e relevantes.",
            "Analise criticamente as informações encontradas.",
            "Forneça resumos claros e bem estruturados.",
            "Cite suas fontes quando apropriado."
        ],
        tools=[ToolsClass()],
        markdown=True
    )

def create_agente_tecnico():
    """Cria o agente especializado em questões técnicas usando AgentOS"""
    AgentClass = Agent if AGNO_AVAILABLE else MockAgent
    ToolsClass = DuckDuckGoTools if AGNO_AVAILABLE else MockDuckDuckGoTools
    return AgentClass(
        name="Agente Técnico",
        model=create_model(),
        instructions=[
            "Você é um especialista técnico em programação e soluções de TI.",
            "Forneça soluções práticas e bem explicadas para problemas técnicos.",
            "Use exemplos de código quando apropriado.",
            "Explique conceitos complexos de forma clara e didática.",
            "Mantenha-se atualizado com as melhores práticas."
        ],
        tools=[ToolsClass()],
        markdown=True
    )

def create_agente_saudacao():
    """Cria o agente especializado em saudações e atendimento inicial usando AgentOS"""
    AgentClass = Agent if AGNO_AVAILABLE else MockAgent
    return AgentClass(
        name="Agente de Saudação",
        model=create_model(),
        instructions=[
            "Você é um agente especializado em saudações calorosas e atendimento inicial.",
            "Seja sempre simpático, educado e acolhedor com os clientes.",
            "Faça perguntas para conhecer melhor o cliente (nome, preferências, ocasião).",
            "Direcione o cliente para o agente de vendas quando apropriado.",
            "Use emojis para tornar a conversa mais calorosa e amigável.",
            "Mantenha um tom profissional mas descontraído."
        ],
        markdown=True
    )

def create_agente_vendas_kit_festas():
    """Cria o agente especializado em vendas de kit festas usando AgentOS"""
    AgentClass = Agent if AGNO_AVAILABLE else MockAgent
    return AgentClass(
        name="Agente de Vendas Kit Festas",
        model=create_model(),
        instructions=[
            "Você é um especialista em vendas de kits para festas em uma loja de doces e salgados.",
            "Conheça bem nossos produtos: kits de aniversário, casamento, formatura, eventos corporativos.",
            "Cada kit inclui: docinhos variados, salgadinhos, bolo temático, decoração básica.",
            "Preços: Kit Básico (50 pessoas) R$ 280, Kit Premium (50 pessoas) R$ 420, Kit Luxo (50 pessoas) R$ 580.",
            "Sempre pergunte sobre: número de convidados, tipo de evento, data, orçamento disponível.",
            "Ofereça personalizações: cores temáticas, sabores especiais, decoração extra.",
            "Seja persuasivo mas não insistente, foque nos benefícios e qualidade.",
            "Ofereça descontos para pedidos antecipados (10% para pedidos com 15 dias de antecedência)."
        ],
        markdown=True
    )

def get_all_agents(account_id: str = None):
    """Retorna todos os agentes disponíveis (padrão + personalizados)"""
    agents = [
        create_assistente_principal(),
        create_agente_pesquisa(),
        create_agente_tecnico(),
        create_agente_saudacao(),
        create_agente_vendas_kit_festas()
    ]
    
    # Adiciona agentes personalizados filtrados por account_id se fornecido
    for agent_data in custom_agents_storage.values():
        if account_id is None or agent_data.get("account_id") == account_id:
            agents.append(agent_data["agent"])
    
    return agents

def save_agent_memory(user_id: str, messages: list):
    """Placeholder para salvar memória - implementação futura"""
    # TODO: Implementar integração com sistema de memória
    return True

# Armazenamento dinâmico de agentes personalizados
custom_agents_storage = {}

def create_custom_agent(name: str, role: str = None, instructions: list = None, user_id: str = "default_user", agent_id: str = None, model: dict = None, system_message: str = None, enable_user_memories: bool = True, tools: list = None, add_history_to_context: bool = True, num_history_runs: int = 5, add_datetime_to_context: bool = True, markdown: bool = True):
    """Cria um agente personalizado dinamicamente usando AgentOS"""
    AgentClass = Agent if AGNO_AVAILABLE else MockAgent
    ToolsClass = DuckDuckGoTools if AGNO_AVAILABLE else MockDuckDuckGoTools
    
    # Usa system_message se fornecido, senão usa instructions
    agent_instructions = system_message or (instructions if instructions else ["Você é um assistente útil."])
    
    # Cria o agente com os parâmetros fornecidos
    agent = AgentClass(
        name=name,
        model=create_model(),
        instructions=agent_instructions if isinstance(agent_instructions, list) else [agent_instructions],
        tools=[ToolsClass()] if tools and "DuckDuckGoTools" in tools else [],
        markdown=markdown
    )
    
    # Adiciona ID se fornecido
    if agent_id:
        agent.id = agent_id
    
    # Armazena o agente personalizado
    agent_key = f"{user_id}_{name}"
    custom_agents_storage[agent_key] = {
        "agent": agent,
        "name": name,
        "role": role,
        "instructions": agent_instructions,
        "user_id": user_id,
        "id": agent_id,
        "model": model or {"provider": "openai", "name": "gpt-4o-mini"},
        "system_message": system_message,
        "enable_user_memories": enable_user_memories,
        "tools": tools or [],
        "add_history_to_context": add_history_to_context,
        "num_history_runs": num_history_runs,
        "add_datetime_to_context": add_datetime_to_context,
        "markdown": markdown
    }
    
    return agent

def update_custom_agent(name: str, new_name: str = None, role: str = None, instructions: list = None, user_id: str = "default_user"):
    """Atualiza um agente personalizado"""
    agent_key = f"{user_id}_{name}"
    if agent_key not in custom_agents_storage:
        return None
    
    agent_data = custom_agents_storage[agent_key]
    
    # Atualiza os campos fornecidos
    updated_name = new_name if new_name else agent_data["name"]
    updated_role = role if role else agent_data["role"]
    updated_instructions = instructions if instructions else agent_data["instructions"]
    
    # Remove o agente antigo se o nome mudou
    if new_name and new_name != name:
        del custom_agents_storage[agent_key]
        agent_key = f"{user_id}_{updated_name}"
    
    # Cria o agente atualizado
    updated_agent = create_custom_agent(updated_name, updated_role, updated_instructions, user_id)
    
    return updated_agent

def delete_custom_agent(agent_id: str, user_id: str = "default_user"):
    """Remove um agente personalizado pelo ID"""
    # Busca o agente pelo ID
    for agent_key, agent_data in list(custom_agents_storage.items()):
        agent = agent_data["agent"]
        if hasattr(agent, 'id') and agent.id == agent_id:
            del custom_agents_storage[agent_key]
            return True
        # Fallback para nome se não tiver ID
        agent_name = getattr(agent.config, 'name', None) if hasattr(agent, 'config') else None
        if agent_name == agent_id:
            del custom_agents_storage[agent_key]
            return True
    return False

def get_custom_agents(user_id: str = "default_user"):
    """Retorna todos os agentes personalizados do usuário"""
    user_agents = []
    for agent_key, agent_data in custom_agents_storage.items():
        if agent_data["user_id"] == user_id:
            user_agents.append(agent_data["agent"])
    return user_agents

def get_agent_by_name(name: str, user_id: str = "default_user"):
    """Busca um agente pelo nome (padrão ou personalizado) usando AgentOS"""
    # Primeiro busca nos agentes padrão
    agents = get_all_agents(user_id=user_id)
    for agent in agents:
        agent_name = getattr(agent.config, 'name', None) if hasattr(agent, 'config') else None
        if agent_name == name:
            return agent
    
    # Depois busca nos agentes personalizados
    agent_key = f"{user_id}_{name}"
    if agent_key in custom_agents_storage:
        return custom_agents_storage[agent_key]["agent"]
    
    return None

def get_agent_by_id(agent_id: str, account_id: str = None):
    """Busca um agente pelo ID (padrão ou personalizado) usando AgentOS"""
    # Primeiro busca nos agentes padrão
    agents = get_all_agents()
    for agent in agents:
        if hasattr(agent, 'id') and agent.id == agent_id:
            return agent
        # Fallback para nome se não tiver ID
        agent_name = getattr(agent.config, 'name', None) if hasattr(agent, 'config') else None
        if agent_name == agent_id:
            return agent
    
    # Depois busca nos agentes personalizados
    for agent_key, agent_data in custom_agents_storage.items():
        # Se account_id for fornecido, filtra por ele
        if account_id and agent_data.get("account_id") != account_id:
            continue
            
        agent = agent_data["agent"]
        if hasattr(agent, 'id') and agent.id == agent_id:
            return agent
        # Fallback para nome se não tiver ID
        agent_name = getattr(agent.config, 'name', None) if hasattr(agent, 'config') else None
        if agent_name == agent_id:
            return agent
    
    return None