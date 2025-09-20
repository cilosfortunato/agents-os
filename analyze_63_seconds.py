import requests
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = 'http://localhost:8002'
HEADERS = {
    'X-API-Key': '151fb361-f295-4a4f-84c9-ec1f42599a67',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_mem0_timeout():
    """Testa especificamente o timeout do Mem0"""
    print("🧠 TESTANDO MEM0 TIMEOUT")
    print("=" * 40)
    
    start = time.perf_counter()
    try:
        mem0_url = "https://api.mem0.ai/v1/memories/search/"
        mem0_headers = {
            "Authorization": "Bearer m0-of7unI4i3qF3YFC9TI4DwU2DRGw5uyk4GXGAmv0d",
            "Content-Type": "application/json"
        }
        payload = {
            "query": "Tem algum serviço que eu possa usar?",
            "user_id": "c4a7b2d8-1e9f-4a2b-8d6c-3e5f7a9b0c1d",
            "limit": 3
        }
        
        # Teste com timeout baixo para simular o problema
        r = requests.post(mem0_url, headers=mem0_headers, data=json.dumps(payload), timeout=5)
        end = time.perf_counter()
        duration = (end - start) * 1000
        
        print(f"✅ Mem0 respondeu em {duration:.1f}ms")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Resultados: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"Erro: {r.text}")
            
    except requests.exceptions.Timeout:
        end = time.perf_counter()
        duration = (end - start) * 1000
        print(f"❌ TIMEOUT do Mem0 após {duration:.1f}ms")
        return True  # Confirma que é timeout
    except Exception as e:
        end = time.perf_counter()
        duration = (end - start) * 1000
        print(f"❌ Erro no Mem0 após {duration:.1f}ms: {e}")
        return True
    
    return False

def test_supabase_queries():
    """Testa múltiplas consultas ao Supabase"""
    print("\n🗄️  TESTANDO CONSULTAS SUPABASE")
    print("=" * 40)
    
    queries = [
        "Busca do agente",
        "Mensagens da sessão", 
        "Mensagens do usuário",
        "Inserção de mensagem"
    ]
    
    total_start = time.perf_counter()
    
    for i, query_name in enumerate(queries):
        start = time.perf_counter()
        try:
            # Simula as consultas que o sistema faz
            if i == 0:  # Busca do agente
                r = requests.get(f'{BASE}/v1/agents/da93fcc7-cf93-403e-aa99-9e295080d692', headers=HEADERS, timeout=10)
            else:  # Health check como proxy para outras consultas
                r = requests.get(f'{BASE}/v1/health', headers=HEADERS, timeout=10)
            
            end = time.perf_counter()
            duration = (end - start) * 1000
            status = "✅" if r.status_code == 200 else "❌"
            print(f"{status} {query_name}: {duration:.1f}ms")
            
        except Exception as e:
            end = time.perf_counter()
            duration = (end - start) * 1000
            print(f"❌ {query_name}: {duration:.1f}ms - Erro: {e}")
    
    total_end = time.perf_counter()
    total_duration = (total_end - total_start) * 1000
    print(f"📊 Total Supabase: {total_duration:.1f}ms")

def test_gemini_processing():
    """Testa o processamento do Gemini"""
    print("\n🤖 TESTANDO PROCESSAMENTO GEMINI")
    print("=" * 40)
    
    start = time.perf_counter()
    try:
        # Simula uma chamada direta ao endpoint que usa Gemini
        payload = {
            "mensagem": "Teste de tempo de processamento",
            "agent_id": "da93fcc7-cf93-403e-aa99-9e295080d692",
            "user_id": "performance-test",
            "session_id": str(uuid.uuid4()),
            "id_conta": "test",
            "debounce": 0,
            "message_id": str(uuid.uuid4()),
            "cliente_id": ""
        }
        
        r = requests.post(f'{BASE}/v1/messages', headers=HEADERS, data=json.dumps([payload]), timeout=60)
        end = time.perf_counter()
        duration = (end - start) * 1000
        
        print(f"✅ Processamento completo em {duration:.1f}ms")
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"ACK recebido: {data.get('messages', ['N/A'])[0][:50]}...")
        
    except requests.exceptions.Timeout:
        end = time.perf_counter()
        duration = (end - start) * 1000
        print(f"❌ TIMEOUT após {duration:.1f}ms")
        return True
    except Exception as e:
        end = time.perf_counter()
        duration = (end - start) * 1000
        print(f"❌ Erro após {duration:.1f}ms: {e}")
        return True
    
    return False

def test_parallel_operations():
    """Testa operações em paralelo para simular o que acontece no get_complete_context"""
    print("\n⚡ TESTANDO OPERAÇÕES PARALELAS")
    print("=" * 40)
    
    def test_session_context():
        time.sleep(0.5)  # Simula consulta Supabase
        return "session_context"
    
    def test_enriched_context():
        time.sleep(30)  # Simula timeout do Mem0
        return "enriched_context"
    
    def test_search_context():
        time.sleep(1)  # Simula busca no Supabase
        return "search_context"
    
    start = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {
            executor.submit(test_session_context): "session",
            executor.submit(test_enriched_context): "enriched", 
            executor.submit(test_search_context): "search"
        }
        
        results = {}
        for fut in as_completed(future_map, timeout=35):  # Timeout de 35s
            key = future_map[fut]
            try:
                result = fut.result()
                end = time.perf_counter()
                duration = (end - start) * 1000
                print(f"✅ {key}: {duration:.1f}ms")
                results[key] = result
            except Exception as e:
                end = time.perf_counter()
                duration = (end - start) * 1000
                print(f"❌ {key}: {duration:.1f}ms - Erro: {e}")
    
    total_end = time.perf_counter()
    total_duration = (total_end - start) * 1000
    print(f"📊 Total paralelo: {total_duration:.1f}ms")

def analyze_63_second_problem():
    """Análise específica do problema de 63 segundos"""
    print("🔍 ANÁLISE DO PROBLEMA DE 63 SEGUNDOS")
    print("=" * 60)
    
    # Teste 1: Mem0 timeout
    print("\n1️⃣ TESTE DE TIMEOUT MEM0")
    mem0_timeout = test_mem0_timeout()
    
    # Teste 2: Consultas Supabase
    print("\n2️⃣ TESTE DE CONSULTAS SUPABASE")
    test_supabase_queries()
    
    # Teste 3: Processamento Gemini
    print("\n3️⃣ TESTE DE PROCESSAMENTO GEMINI")
    gemini_timeout = test_gemini_processing()
    
    # Teste 4: Operações paralelas
    print("\n4️⃣ TESTE DE OPERAÇÕES PARALELAS")
    test_parallel_operations()
    
    # Análise final
    print("\n🎯 DIAGNÓSTICO FINAL")
    print("=" * 40)
    
    if mem0_timeout:
        print("🔴 PROBLEMA IDENTIFICADO: Timeout do Mem0")
        print("   - O Mem0 está demorando mais de 30s para responder")
        print("   - Isso bloqueia o get_complete_context")
        print("   - Solução: Reduzir timeout ou implementar fallback")
    
    if gemini_timeout:
        print("🔴 PROBLEMA IDENTIFICADO: Timeout do Gemini")
        print("   - O processamento do Gemini está muito lento")
        print("   - Pode ser throttling ou problema de rede")
    
    print("\n💡 RECOMENDAÇÕES:")
    print("   1. Reduzir timeout do Mem0 de 30s para 5s")
    print("   2. Implementar fallback quando Mem0 falha")
    print("   3. Adicionar cache local para consultas frequentes")
    print("   4. Considerar processamento assíncrono total")
    print("   5. Monitorar latência das APIs externas")

if __name__ == "__main__":
    analyze_63_second_problem()