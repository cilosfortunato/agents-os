#!/usr/bin/env python3
"""
Cria um agente com modelo Vertex AI
"""

from supabase_service import SupabaseService

def create_vertex_agent():
    """Cria um agente configurado para usar Vertex AI"""
    supabase_service = SupabaseService()
    
    try:
        print("Criando agente com modelo Vertex AI...")
        result = supabase_service.create_agent(
            name="Assistente Vertex AI",
            role="Assistente inteligente usando Vertex AI",
            instructions=[
                "Seja útil e prestativo",
                "Responda de forma clara e objetiva",
                "Use o modelo Vertex AI para gerar respostas de qualidade"
            ],
            model="gemini-2.5-flash",  # Modelo Vertex AI
            account_id="f7dae33c-6364-4d88-908f-f5f64426a5c9"
        )
        print(f"✅ Agente criado com sucesso!")
        print(f"ID: {result.get('id')}")
        print(f"Nome: {result.get('name')}")
        print(f"Modelo: {result.get('model')}")
        return result
    except Exception as e:
        print(f"❌ Erro ao criar agente: {e}")
        return None

def list_agents():
    """Lista todos os agentes"""
    supabase_service = SupabaseService()
    
    try:
        print("\n=== Agentes Disponíveis ===")
        agents = supabase_service.list_all_agents()
        
        for i, agent in enumerate(agents, 1):
            print(f"{i}. {agent.get('name')} (ID: {agent.get('id')})")
            print(f"   Modelo: {agent.get('model')}")
            print(f"   Role: {agent.get('role')}")
            print()
            
    except Exception as e:
        print(f"❌ Erro ao listar agentes: {e}")

if __name__ == "__main__":
    # Lista agentes existentes
    list_agents()
    
    # Cria novo agente com Vertex AI
    create_vertex_agent()
    
    # Lista novamente para confirmar
    print("\n" + "="*50)
    list_agents()