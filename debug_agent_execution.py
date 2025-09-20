#!/usr/bin/env python3
"""
Script para debugar a execução específica do agente
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_completa import generate_intelligent_response, execute_agent_with_memory
from supabase_service import SupabaseService

def test_agent_search():
    """Testa a busca de agentes no Supabase"""
    try:
        print("=== Teste de Busca de Agentes ===")
        
        supabase_service = SupabaseService()
        agents = supabase_service.list_all_agents()
        
        print(f"✅ Encontrados {len(agents)} agentes:")
        for i, agent in enumerate(agents[:3]):  # Mostra apenas os 3 primeiros
            print(f"  {i+1}. ID: {agent.get('id')}")
            print(f"     Nome: {agent.get('name')}")
            print(f"     Role: {agent.get('role')}")
            print(f"     Model: {agent.get('model')}")
            print(f"     Instructions: {len(agent.get('instructions', []))} instruções")
            print()
        
        return agents[0] if agents else None
        
    except Exception as e:
        print(f"❌ Erro na busca de agentes: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_agent_execution_direct(agent_data):
    """Testa a execução direta do agente"""
    try:
        print("=== Teste de Execução Direta do Agente ===")
        
        if not agent_data:
            print("❌ Nenhum agente disponível para teste")
            return
        
        # Simula contexto de memória vazio
        memory_context = {
            "session_context": "Nova sessão de teste",
            "enriched_context": "Nenhum contexto adicional",
            "search_context": "Nenhum histórico relacionado"
        }
        
        print(f"Testando agente: {agent_data.get('name')}")
        print(f"Modelo: {agent_data.get('model')}")
        
        result = execute_agent_with_memory(
            query="Qual é a capital do Brasil?",
            user_id="test-user-debug",
            agent_data=agent_data,
            memory_context=memory_context
        )
        
        print("✅ Resultado da execução:")
        print(f"Texto: {result['text']}")
        print(f"Usage: {result['usage']}")
        
    except Exception as e:
        print(f"❌ Erro na execução do agente: {str(e)}")
        import traceback
        traceback.print_exc()

def test_generate_intelligent_response():
    """Testa a função generate_intelligent_response completa"""
    try:
        print("\n=== Teste da Função generate_intelligent_response ===")
        
        response = generate_intelligent_response(
            query="Qual é a capital do Brasil?",
            user_id="test-user-debug",
            session_id="test-session-debug",
            agent_name="Especialista em Produtos"
        )
        
        print("✅ Resposta gerada:")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Erro na função generate_intelligent_response: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    agent_data = test_agent_search()
    if agent_data:
        test_agent_execution_direct(agent_data)
    test_generate_intelligent_response()