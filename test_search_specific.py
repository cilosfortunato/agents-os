#!/usr/bin/env python3
"""
Teste de busca por termos específicos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_memory_service import dual_memory_service

def test_search_specific_terms():
    """Testa busca por termos específicos"""
    print("🔍 TESTE DE BUSCA POR TERMOS ESPECÍFICOS")
    print("=" * 50)
    
    user_id = "test_user_memory"
    
    # Teste 1: Buscar por "João"
    print("🔍 Buscando por 'João':")
    result_joao = dual_memory_service.search_user_history(user_id, "João", 5)
    print(result_joao)
    print()
    
    # Teste 2: Buscar por "pizza"
    print("🔍 Buscando por 'pizza':")
    result_pizza = dual_memory_service.search_user_history(user_id, "pizza", 5)
    print(result_pizza)
    print()
    
    # Teste 3: Buscar por "nome"
    print("🔍 Buscando por 'nome':")
    result_nome = dual_memory_service.search_user_history(user_id, "nome", 5)
    print(result_nome)
    print()
    
    # Teste 4: Contexto completo com query mais inteligente
    print("🧠 Testando contexto completo com query 'João pizza':")
    context = dual_memory_service.get_complete_context(
        user_id=user_id,
        session_id="session_memory_test",
        query="João pizza",  # Query mais específica
        session_limit=5,
        memory_limit=3
    )
    
    print("📊 CONTEXTO COM QUERY ESPECÍFICA:")
    print("-" * 30)
    print(f"📝 Session Context: {context.get('session_context', '')}")
    print(f"🔍 Enriched Context: {context.get('enriched_context', '')}")
    print(f"📚 Search Context: {context.get('search_context', '')}")
    
    # Verificar se encontrou as informações
    all_context = f"{context.get('session_context', '')} {context.get('enriched_context', '')} {context.get('search_context', '')}".lower()
    
    has_joao = "joão" in all_context
    has_pizza = "pizza" in all_context
    
    print("\n🎯 VERIFICAÇÃO DE CONTEÚDO:")
    print("-" * 30)
    print(f"  🏷️  Contém 'João': {'✅' if has_joao else '❌'}")
    print(f"  🍕 Contém 'pizza': {'✅' if has_pizza else '❌'}")
    
    if has_joao and has_pizza:
        print("✅ SUCESSO: Encontrou as informações com query específica!")
    else:
        print("❌ PROBLEMA: Ainda não encontrou todas as informações")

if __name__ == "__main__":
    test_search_specific_terms()