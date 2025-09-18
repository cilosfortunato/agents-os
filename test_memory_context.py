#!/usr/bin/env python3
"""
Teste do contexto de memória
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_memory_service import dual_memory_service
import json

def test_memory_context():
    """Testa o contexto de memória retornado pelo dual_memory_service"""
    print("🧠 TESTE DO CONTEXTO DE MEMÓRIA")
    print("=" * 50)
    
    user_id = "test_user_memory"
    session_id = "session_memory_test"
    query = "Você se lembra do meu nome e do que eu gosto de comer?"
    
    print(f"👤 User ID: {user_id}")
    print(f"📋 Session ID: {session_id}")
    print(f"❓ Query: {query}")
    print()
    
    try:
        # Busca o contexto completo
        memory_context = dual_memory_service.get_complete_context(
            user_id=user_id,
            session_id=session_id,
            query=query,
            session_limit=5,
            memory_limit=3
        )
        
        print("📊 CONTEXTO RETORNADO:")
        print("-" * 30)
        print(json.dumps(memory_context, indent=2, ensure_ascii=False))
        print()
        
        # Analisar cada parte do contexto
        print("🔍 ANÁLISE DO CONTEXTO:")
        print("-" * 30)
        
        session_context = memory_context.get("session_context", "")
        enriched_context = memory_context.get("enriched_context", "")
        search_context = memory_context.get("search_context", "")
        
        print(f"📝 Session Context: {session_context}")
        print(f"🔍 Enriched Context: {enriched_context}")
        print(f"📚 Search Context: {search_context}")
        print()
        
        # Verificar se há informações sobre João e pizza
        all_context = f"{session_context} {enriched_context} {search_context}".lower()
        
        has_joao = "joão" in all_context
        has_pizza = "pizza" in all_context
        
        print("🎯 VERIFICAÇÃO DE CONTEÚDO:")
        print("-" * 30)
        print(f"  🏷️  Contém 'João': {'✅' if has_joao else '❌'}")
        print(f"  🍕 Contém 'pizza': {'✅' if has_pizza else '❌'}")
        
        if has_joao and has_pizza:
            print("✅ SUCESSO: O contexto contém as informações necessárias!")
        else:
            print("❌ PROBLEMA: O contexto não contém todas as informações")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_context()