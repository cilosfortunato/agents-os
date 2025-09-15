from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.tools.mem0 import Mem0Tools  # Não disponível na versão atual
from mem0 import MemoryClient
from config import Config

def create_model():
    """Cria uma instância do modelo configurado"""
    model_config = Config.get_model_config()
    return OpenRouter(
        id=model_config["model_id"],
        temperature=model_config["temperature"]
    )

def create_assistente_principal(user_id: str = "default_user"):
    """Cria o agente assistente principal com memória Mem0"""
    # Inicializa o cliente Mem0 para este usuário
    memory_client = MemoryClient()
    
    # Recupera memórias existentes para contexto
    try:
        user_memories = memory_client.get_all(user_id=user_id)
    except:
        user_memories = []
    
    return Agent(
        name="Assistente Principal",
        role="Assistente geral com memória persistente",
        model=create_model(),
        instructions=[
            "Você é um assistente inteligente e prestativo com memória persistente.",
            "Use sua memória para lembrar de conversas anteriores com o usuário.",
            "Armazene informações importantes sobre preferências e contexto do usuário.",
            "Recupere memórias relevantes para fornecer respostas personalizadas.",
            "Seja cordial, profissional e sempre tente ajudar da melhor forma possível.",
            "Se não souber algo, seja honesto e sugira alternativas."
        ],
        dependencies={"memory": user_memories, "memory_client": memory_client, "user_id": user_id},
        add_dependencies_to_context=True,
        markdown=True
    )

def create_agente_pesquisa(user_id: str = "default_user"):
    """Cria o agente especializado em pesquisa com memória Mem0"""
    # Inicializa o cliente Mem0 para este usuário
    memory_client = MemoryClient()
    
    # Recupera memórias existentes para contexto
    try:
        user_memories = memory_client.get_all(user_id=user_id)
    except:
        user_memories = []
    
    return Agent(
        name="Agente de Pesquisa",
        role="Especialista em pesquisa e análise de informações",
        model=create_model(),
        instructions=[
            "Você é um especialista em pesquisa e análise de informações.",
            "Use o DuckDuckGo para buscar informações atualizadas e relevantes.",
            "Analise criticamente as informações encontradas.",
            "Forneça resumos claros e bem estruturados.",
            "Cite suas fontes quando apropriado.",
            "Use o contexto de pesquisas anteriores para melhorar futuras consultas.",
            "Lembre-se de descobertas importantes para referência futura."
        ],
        tools=[DuckDuckGoTools()],
        dependencies={"memory": user_memories, "memory_client": memory_client, "user_id": user_id},
        add_dependencies_to_context=True,
        markdown=True
    )

def create_agente_tecnico(user_id: str = "default_user"):
    """Cria o agente especializado em questões técnicas com memória Mem0"""
    # Inicializa o cliente Mem0 para este usuário
    memory_client = MemoryClient()
    
    # Recupera memórias existentes para contexto
    try:
        user_memories = memory_client.get_all(user_id=user_id)
    except:
        user_memories = []
    
    return Agent(
        name="Agente Técnico",
        role="Especialista em soluções técnicas e programação",
        model=create_model(),
        instructions=[
            "Você é um especialista técnico em programação e soluções de TI.",
            "Forneça soluções práticas e bem explicadas para problemas técnicos.",
            "Use exemplos de código quando apropriado.",
            "Explique conceitos complexos de forma clara e didática.",
            "Mantenha-se atualizado com as melhores práticas.",
            "Use o contexto de soluções anteriores para problemas similares.",
            "Lembre-se de configurações e preferências técnicas do usuário."
        ],
        tools=[DuckDuckGoTools()],
        dependencies={"memory": user_memories, "memory_client": memory_client, "user_id": user_id},
        add_dependencies_to_context=True,
        markdown=True
    )

def create_agente_saudacao(user_id: str = "default_user"):
    """Cria o agente especializado em saudações e atendimento inicial"""
    # Inicializa o cliente Mem0 para este usuário
    memory_client = MemoryClient()
    
    # Recupera memórias existentes para contexto
    try:
        user_memories = memory_client.get_all(user_id=user_id)
    except:
        user_memories = []
    
    return Agent(
        name="Agente de Saudação",
        role="Especialista em recepção e atendimento inicial",
        model=create_model(),
        instructions=[
            "Você é um agente especializado em saudações calorosas e atendimento inicial.",
            "Seja sempre simpático, educado e acolhedor com os clientes.",
            "Faça perguntas para conhecer melhor o cliente (nome, preferências, ocasião).",
            "Lembre-se de informações pessoais dos clientes para personalizar o atendimento.",
            "Direcione o cliente para o agente de vendas quando apropriado.",
            "Use emojis para tornar a conversa mais calorosa e amigável.",
            "Mantenha um tom profissional mas descontraído."
        ],
        tools=[],
        dependencies={"memory": user_memories, "memory_client": memory_client, "user_id": user_id},
        add_dependencies_to_context=True,
        markdown=True
    )

def create_agente_vendas_kit_festas(user_id: str = "default_user"):
    """Cria o agente especializado em vendas de kit festas"""
    # Inicializa o cliente Mem0 para este usuário
    memory_client = MemoryClient()
    
    # Recupera memórias existentes para contexto
    try:
        user_memories = memory_client.get_all(user_id=user_id)
    except:
        user_memories = []
    
    return Agent(
        name="Agente de Vendas Kit Festas",
        role="Especialista em vendas de kits para festas e eventos",
        model=create_model(),
        instructions=[
            "Você é um especialista em vendas de kits para festas em uma loja de doces e salgados.",
            "Conheça bem nossos produtos: kits de aniversário, casamento, formatura, eventos corporativos.",
            "Cada kit inclui: docinhos variados, salgadinhos, bolo temático, decoração básica.",
            "Preços: Kit Básico (50 pessoas) R$ 280, Kit Premium (50 pessoas) R$ 420, Kit Luxo (50 pessoas) R$ 580.",
            "Sempre pergunte sobre: número de convidados, tipo de evento, data, orçamento disponível.",
            "Ofereça personalizações: cores temáticas, sabores especiais, decoração extra.",
            "Lembre-se das preferências e histórico de compras dos clientes.",
            "Seja persuasivo mas não insistente, foque nos benefícios e qualidade.",
            "Ofereça descontos para pedidos antecipados (10% para pedidos com 15 dias de antecedência)."
        ],
        tools=[],
        dependencies={"memory": user_memories, "memory_client": memory_client, "user_id": user_id},
        add_dependencies_to_context=True,
        markdown=True
    )

def get_all_agents(user_id: str = "default_user"):
    """Retorna todos os agentes disponíveis com memória Mem0 configurada"""
    return [
        create_assistente_principal(user_id=user_id),
        create_agente_pesquisa(user_id=user_id),
        create_agente_tecnico(user_id=user_id),
        create_agente_saudacao(user_id=user_id),
        create_agente_vendas_kit_festas(user_id=user_id)
    ]

def save_agent_memory(user_id: str, messages: list):
    """Salva a interação na memória Mem0"""
    try:
        memory_client = MemoryClient()
        memory_client.add(messages, user_id=user_id)
        return True
    except Exception as e:
        print(f"Erro ao salvar memória: {e}")
        return False

# Armazenamento dinâmico de agentes personalizados
custom_agents_storage = {}

def create_custom_agent(name: str, role: str, instructions: list, user_id: str = "default_user"):
    """Cria um agente personalizado dinamicamente"""
    # Inicializa o cliente Mem0 para este usuário
    memory_client = MemoryClient()
    
    # Recupera memórias existentes para contexto
    try:
        user_memories = memory_client.get_all(user_id=user_id)
    except:
        user_memories = []
    
    agent = Agent(
        name=name,
        role=role,
        model=create_model(),
        instructions=instructions,
        tools=[DuckDuckGoTools()],
        dependencies={"memory": user_memories, "memory_client": memory_client, "user_id": user_id},
        add_dependencies_to_context=True,
        markdown=True
    )
    
    # Armazena o agente personalizado
    agent_key = f"{user_id}_{name}"
    custom_agents_storage[agent_key] = {
        "agent": agent,
        "name": name,
        "role": role,
        "instructions": instructions,
        "user_id": user_id
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

def delete_custom_agent(name: str, user_id: str = "default_user"):
    """Remove um agente personalizado"""
    agent_key = f"{user_id}_{name}"
    if agent_key in custom_agents_storage:
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
    """Busca um agente pelo nome (padrão ou personalizado) com memória Mem0 configurada"""
    # Primeiro busca nos agentes padrão
    agents = get_all_agents(user_id=user_id)
    for agent in agents:
        if agent.config.name == name:
            return agent
    
    # Depois busca nos agentes personalizados
    agent_key = f"{user_id}_{name}"
    if agent_key in custom_agents_storage:
        return custom_agents_storage[agent_key]["agent"]
    
    return None