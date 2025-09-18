#!/usr/bin/env python3
"""
Teste da funcionalidade de busca inteligente com extração de palavras-chave
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_memory_service import DualMemoryService

def test_smart_search():
    """Testa a busca inteligente com extração de palavras-chave"""
    print("🧠 TESTE DE BUSCA INTELIGENTE")
    print("=" * 50)
    
    # Inicializa o serviço
    dual_memory = DualMemoryService()
    
    # User ID que sabemos que tem dados
    user_id = "test_user_memory"
    session_id = "test_session_123"
    
    # Testa diferentes tipos de queries
    test_queries = [
        "Você se lembra do meu nome?",
        "Qual é o meu nome e o que eu gosto de comer?", 
        "Você sabe o que eu gosto de comer?",
        "Me fale sobre minhas preferências alimentares"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 TESTE {i}: '{query}'")
        print("-" * 40)
        
        # Testa extração de termos
        search_terms = dual_memory._extract_search_terms(query)
        print(f"📝 Termos extraídos: {search_terms}")
        
        # Testa contexto completo
        context = dual_memory.get_complete_context(user_id, session_id, query)
        
        print(f"🔍 Search Context:")
        print(context['search_context'])
        
        # Verifica se encontrou informações relevantes
        search_context = context['search_context']
        has_joao = 'joão' in search_context.lower() or 'João' in search_context
        has_pizza = 'pizza' in search_context.lower()
        
        print(f"✅ Encontrou 'João': {has_joao}")
        print(f"🍕 Encontrou 'pizza': {has_pizza}")
        
        if has_joao and has_pizza:
            print("🎯 SUCESSO: Busca inteligente funcionou!")
        else:
            print("❌ FALHA: Busca não encontrou informações relevantes")

if __name__ == "__main__":
    test_smart_search()