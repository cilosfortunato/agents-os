"""
Teste para reproduzir o cenário exato que causa latência de 63 segundos
"""
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_memory_service import dual_memory_service
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configurar logging para ver os detalhes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_exact_latency_scenario():
    """Reproduz o cenário exato que causa a latência"""
    print("🔍 REPRODUZINDO CENÁRIO EXATO DE LATÊNCIA")
    print("=" * 60)
    
    # Parâmetros exatos do fluxo real
    user_id = "116883357474955@lid"  # User ID real do teste
    session_id = "645d4334-8660-49b0-813b-872662cd2b7c"  # Session ID real
    query = "Oi! Pode se apresentar?"  # Query real do teste
    
    print(f"👤 User ID: {user_id}")
    print(f"📋 Session ID: {session_id}")
    print(f"❓ Query: {query}")
    print()
    
    # Teste 1: get_complete_context (o método que está sendo chamado)
    print("🧠 TESTE 1: get_complete_context (método real)")
    print("-" * 50)
    
    start_time = time.perf_counter()
    try:
        memory_context = dual_memory_service.get_complete_context(
            user_id=user_id,
            session_id=session_id,
            query=query,
            session_limit=5,
            memory_limit=3
        )
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000
        
        print(f"✅ get_complete_context completou em: {duration:.1f}ms")
        print(f"📊 Contexto retornado:")
        for key, value in memory_context.items():
            print(f"  {key}: {len(value)} caracteres")
        
    except Exception as e:
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000
        print(f"❌ get_complete_context falhou após: {duration:.1f}ms")
        print(f"Erro: {e}")
    
    print()
    
    # Teste 2: Apenas get_enriched_context (isolado)
    print("🔍 TESTE 2: get_enriched_context (isolado)")
    print("-" * 50)
    
    start_time = time.perf_counter()
    try:
        enriched_context = dual_memory_service.get_enriched_context(
            user_id=user_id,
            query=query,
            limit=3
        )
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000
        
        print(f"✅ get_enriched_context completou em: {duration:.1f}ms")
        print(f"📊 Contexto: {len(enriched_context)} caracteres")
        
    except Exception as e:
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000
        print(f"❌ get_enriched_context falhou após: {duration:.1f}ms")
        print(f"Erro: {e}")
    
    print()
    
    # Teste 3: Simular o ThreadPoolExecutor exato
    print("⚡ TESTE 3: ThreadPoolExecutor (simulação exata)")
    print("-" * 50)
    
    def _get_session():
        return dual_memory_service.get_session_context(session_id, 5)

    def _get_enriched():
        return dual_memory_service.get_enriched_context(user_id, query, 3)

    def _get_search():
        search_terms = dual_memory_service._extract_search_terms(query)
        return dual_memory_service._search_with_multiple_terms(user_id, search_terms, 5)
    
    start_time = time.perf_counter()
    results = {
        "session_context": "",
        "enriched_context": "",
        "search_context": ""
    }
    
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {
                executor.submit(_get_session): "session_context",
                executor.submit(_get_enriched): "enriched_context",
                executor.submit(_get_search): "search_context",
            }
            
            for fut in as_completed(future_map):
                key = future_map[fut]
                try:
                    result = fut.result()
                    current_time = time.perf_counter()
                    duration = (current_time - start_time) * 1000
                    print(f"✅ {key}: {duration:.1f}ms")
                    results[key] = result
                except Exception as e:
                    current_time = time.perf_counter()
                    duration = (current_time - start_time) * 1000
                    print(f"❌ {key}: {duration:.1f}ms - Erro: {e}")
                    results[key] = ""
        
        end_time = time.perf_counter()
        total_duration = (end_time - start_time) * 1000
        print(f"📊 Total ThreadPoolExecutor: {total_duration:.1f}ms")
        
    except Exception as e:
        end_time = time.perf_counter()
        total_duration = (end_time - start_time) * 1000
        print(f"❌ ThreadPoolExecutor falhou após: {total_duration:.1f}ms")
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_exact_latency_scenario()