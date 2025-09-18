#!/usr/bin/env python3
"""
Teste específico para o método search_messages do Supabase
"""

import os
from dotenv import load_dotenv
from supabase_service import supabase_service

# Carrega variáveis de ambiente
load_dotenv()

def test_search_messages():
    """Testa o método search_messages do SupabaseService"""
    print("🔍 TESTE DO MÉTODO SEARCH_MESSAGES")
    print("=" * 50)
    
    try:
        # Primeiro, vamos ver todos os registros para um user_id específico
        print("📊 Consultando todos os registros para test_user_memory...")
        all_messages = supabase_service.get_user_messages("test_user_memory", limit=10)
        print(f"✅ Total de mensagens encontradas: {len(all_messages)}")
        
        for i, msg in enumerate(all_messages, 1):
            print(f"   {i}. User: {msg['user_message'][:50]}...")
            print(f"      Agent: {msg['agent_response'][:50]}...")
            print(f"      Created: {msg['created_at']}")
            print()
        
        # Agora vamos testar a busca por termo específico
        print("🔍 Testando busca por 'João'...")
        search_results = supabase_service.search_messages("test_user_memory", "João")
        print(f"✅ Resultados da busca por 'João': {len(search_results)}")
        
        for i, msg in enumerate(search_results, 1):
            print(f"   {i}. User: {msg['user_message']}")
            print(f"      Agent: {msg['agent_response']}")
            print()
        
        # Teste busca por 'pizza'
        print("🔍 Testando busca por 'pizza'...")
        search_results = supabase_service.search_messages("test_user_memory", "pizza")
        print(f"✅ Resultados da busca por 'pizza': {len(search_results)}")
        
        for i, msg in enumerate(search_results, 1):
            print(f"   {i}. User: {msg['user_message']}")
            print(f"      Agent: {msg['agent_response']}")
            print()
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_messages()