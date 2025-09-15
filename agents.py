from agno import Agent
from agno.models import OpenRouterModel
from agno.tools import DuckDuckGoTools
from config import Config
import os
import json

def create_model():
    """Cria uma instância do modelo OpenRouter configurado"""
    return OpenRouterModel(
        model_id="openai/gpt-4o-mini",
        api_key=Config.OPENAI_API_KEY
    )

def create_assistente_principal(user_id: str = "default_user"):
    """Cria o agente assistente principal usando AgentOS"""
    return Agent(
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

def create_agente_pesquisa(user_id: str = "default_user"):
    """Cria o agente especializado em pesquisa usando AgentOS"""
    return Agent(
        name="Agente de Pesquisa",
        model=create_model(),
        instructions=[
            "Você é um especialista em pesquisa e análise de informações.",
            "Use o DuckDuckGo para buscar informações atualizadas e relevantes.",
            "Analise criticamente as informações encontradas.",
            "Forneça resumos claros e bem estruturados.",
            "Cite suas fontes quando apropriado."
        ],
        tools=[DuckDuckGoTools()],
        markdown=True
    )

def create_agente_tecnico(user_id: str = "default_user"):
    """Cria o agente especializado em questões técnicas usando AgentOS"""
    return Agent(
        name="Agente Técnico",
        model=create_model(),
        instructions=[
            "Você é um especialista técnico em programação e soluções de TI.",
            "Forneça soluções práticas e bem explicadas para problemas técnicos.",
            "Use exemplos de código quando apropriado.",
            "Explique conceitos complexos de forma clara e didática.",
            "Mantenha-se atualizado com as melhores práticas."
        ],
        tools=[DuckDuckGoTools()],
        markdown=True
    )

def create_agente_saudacao(user_id: str = "default_user"):
    """Cria o agente especializado em saudações e atendimento inicial usando AgentOS"""
    return Agent(
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

def create_agente_vendas_kit_festas(user_id: str = "default_user"):
    """Cria o agente especializado em vendas de kit festas usando AgentOS"""
    return Agent(
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
    """Placeholder para salvar memória - implementação futura"""
    # TODO: Implementar integração com sistema de memória
    return True

# Armazenamento dinâmico de agentes personalizados
custom_agents_storage = {}

def create_custom_agent(name: str, role: str, instructions: list, user_id: str = "default_user"):
    """Cria um agente personalizado dinamicamente usando AgentOS"""
    agent = Agent(
        name=name,
        model=create_model(),
        instructions=instructions,
        tools=[DuckDuckGoTools()],
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
    """Busca um agente pelo nome (padrão ou personalizado) usando AgentOS"""
    # Primeiro busca nos agentes padrão
    agents = get_all_agents(user_id=user_id)
    for agent in agents:
        if agent.name == name:
            return agent
    
    # Depois busca nos agentes personalizados
    agent_key = f"{user_id}_{name}"
    if agent_key in custom_agents_storage:
        return custom_agents_storage[agent_key]["agent"]
    
    return None