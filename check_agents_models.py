#!/usr/bin/env python3
"""
Script para verificar todos os agentes e seus modelos
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_service import SupabaseService

def check_all_agents():
    """Verifica todos os agentes e seus modelos"""
    try:
        print("=== Verificando Todos os Agentes ===")
        
        supabase_service = SupabaseService()
        agents = supabase_service.list_all_agents()
        
        print(f"Total de agentes encontrados: {len(agents)}")
        print()
        
        vertex_agents = []
        openai_agents = []
        
        for i, agent in enumerate(agents):
            agent_id = agent.get('id')
            name = agent.get('name')
            model = agent.get('model', 'N/A')
            role = agent.get('role', 'N/A')
            
            print(f"{i+1}. ID: {agent_id}")
            print(f"   Nome: {name}")
            print(f"   Modelo: {model}")
            print(f"   Role: {role}")
            
            # Classifica por tipo de modelo
            if any(vertex_model in model.lower() for vertex_model in ["gemini", "vertex"]):
                vertex_agents.append(agent)
                print("   🟢 VERTEX AI")
            else:
                openai_agents.append(agent)
                print("   🔵 OPENAI")
            
            print()
        
        print(f"Resumo:")
        print(f"- Agentes Vertex AI: {len(vertex_agents)}")
        print(f"- Agentes OpenAI: {len(openai_agents)}")
        
        if not vertex_agents:
            print("\n❌ PROBLEMA: Nenhum agente com modelo Vertex AI encontrado!")
            print("Será necessário criar ou atualizar um agente para usar gemini-2.5-flash")
        else:
            print(f"\n✅ Agentes Vertex AI disponíveis:")
            for agent in vertex_agents:
                print(f"   - {agent.get('name')} (ID: {agent.get('id')})")
        
        return vertex_agents, openai_agents
        
    except Exception as e:
        print(f"❌ Erro ao verificar agentes: {str(e)}")
        import traceback
        traceback.print_exc()
        return [], []

def create_vertex_agent_if_needed(vertex_agents):
    """Cria um agente Vertex AI se necessário"""
    if vertex_agents:
        print("\n✅ Já existem agentes Vertex AI, não é necessário criar novo.")
        return
    
    try:
        print("\n=== Criando Agente Vertex AI ===")
        
        supabase_service = SupabaseService()
        
        agent_data = {
            "name": "Assistente Vertex AI - Gemini",
            "role": "Assistente inteligente especializado em responder perguntas",
            "model": "gemini-2.5-flash",
            "instructions": [
                "Responda de forma clara e precisa",
                "Use informações atualizadas quando possível",
                "Seja educado e profissional"
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        result = supabase_service.create_agent(agent_data)
        print(f"✅ Agente Vertex AI criado com sucesso!")
        print(f"   ID: {result.get('id')}")
        print(f"   Nome: {result.get('name')}")
        print(f"   Modelo: {result.get('model')}")
        
    except Exception as e:
        print(f"❌ Erro ao criar agente Vertex AI: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    vertex_agents, openai_agents = check_all_agents()
    create_vertex_agent_if_needed(vertex_agents)