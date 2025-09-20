import requests
import json
import time
import uuid

BASE = 'http://localhost:8002'
HEADERS = {
    'X-API-Key': '151fb361-f295-4a4f-84c9-ec1f42599a67',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def measure_time(func, description):
    """Mede o tempo de execução de uma função"""
    start = time.perf_counter()
    result = func()
    end = time.perf_counter()
    duration = (end - start) * 1000  # em milissegundos
    print(f"⏱️  {description}: {duration:.1f}ms")
    return result, duration

def test_health():
    """Testa health check"""
    def _test():
        r = requests.get(f'{BASE}/v1/health', headers=HEADERS, timeout=10)
        return r.status_code == 200
    return measure_time(_test, "Health Check")

def test_agent_lookup():
    """Testa busca do agente"""
    def _test():
        r = requests.get(f'{BASE}/v1/agents/da93fcc7-cf93-403e-aa99-9e295080d692', headers=HEADERS, timeout=15)
        return r.status_code == 200
    return measure_time(_test, "Agent Lookup")

def test_message_ack():
    """Testa apenas o ACK da mensagem (sem aguardar processamento)"""
    def _test():
        payload = {
            "mensagem": "Teste de performance - qual o tempo de resposta?",
            "agent_id": "da93fcc7-cf93-403e-aa99-9e295080d692",
            "user_id": "performance-test-user",
            "session_id": str(uuid.uuid4()),
            "id_conta": "performance-test",
            "debounce": 0,  # Sem debounce para resposta imediata
            "message_id": str(uuid.uuid4()),
            "cliente_id": ""
        }
        
        r = requests.post(f'{BASE}/v1/messages', headers=HEADERS, data=json.dumps([payload]), timeout=30)
        return r.status_code == 200
    return measure_time(_test, "Message ACK (POST /v1/messages)")

def test_direct_gemini():
    """Testa chamada direta ao Gemini via API"""
    def _test():
        try:
            import google.generativeai as genai
            genai.configure(api_key="AQ.Ab8RN6LDtoXn4cdQvG62dfzA2M6FozHfH6Tgb8EG4WaS78uc3g")
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content("Responda em uma frase: qual é o horário de funcionamento?")
            return len(response.text) > 0
        except Exception as e:
            print(f"Erro no teste direto Gemini: {e}")
            return False
    return measure_time(_test, "Gemini Direct API Call")

def test_supabase_query():
    """Testa consulta ao Supabase"""
    def _test():
        # Simula uma consulta similar ao que o sistema faz
        import os
        from supabase import create_client, Client
        
        url = "https://usigbcsmzialnulsvpfr.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVzaWdiY3NtemlhbG51bHN2cGZyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDM0Mjg1MiwiZXhwIjoyMDY1OTE4ODUyfQ.udMP2y7D81l4liL1zfzCBNN36w16YbI2HAU_7sIj9Y0"
        
        try:
            supabase: Client = create_client(url, key)
            result = supabase.table("agentes_solo").select("*").eq("id", "da93fcc7-cf93-403e-aa99-9e295080d692").execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Erro no teste Supabase: {e}")
            return False
    return measure_time(_test, "Supabase Agent Query")

def test_mem0_search():
    """Testa busca na memória Mem0"""
    def _test():
        try:
            mem0_url = "https://api.mem0.ai/v1/memories/search/"
            mem0_headers = {
                "Authorization": "Bearer m0-of7unI4i3qF3YFC9TI4DwU2DRGw5uyk4GXGAmv0d",
                "Content-Type": "application/json"
            }
            payload = {
                "query": "teste performance",
                "user_id": "performance-test-user",
                "limit": 3
            }
            r = requests.post(mem0_url, headers=mem0_headers, data=json.dumps(payload), timeout=10)
            return r.status_code == 200
        except Exception as e:
            print(f"Erro no teste Mem0: {e}")
            return False
    return measure_time(_test, "Mem0 Memory Search")

def analyze_performance():
    """Executa todos os testes de performance"""
    print("🔍 ANÁLISE DE PERFORMANCE - IDENTIFICANDO GARGALOS")
    print("=" * 60)
    
    total_start = time.perf_counter()
    
    # Testes individuais
    health_ok, health_time = test_health()
    agent_ok, agent_time = test_agent_lookup()
    supabase_ok, supabase_time = test_supabase_query()
    mem0_ok, mem0_time = test_mem0_search()
    gemini_ok, gemini_time = test_direct_gemini()
    ack_ok, ack_time = test_message_ack()
    
    total_end = time.perf_counter()
    total_time = (total_end - total_start) * 1000
    
    print("\n📊 RESUMO DOS TEMPOS:")
    print(f"   Health Check: {health_time:.1f}ms {'✅' if health_ok else '❌'}")
    print(f"   Agent Lookup: {agent_time:.1f}ms {'✅' if agent_ok else '❌'}")
    print(f"   Supabase Query: {supabase_time:.1f}ms {'✅' if supabase_ok else '❌'}")
    print(f"   Mem0 Search: {mem0_time:.1f}ms {'✅' if mem0_ok else '❌'}")
    print(f"   Gemini Direct: {gemini_time:.1f}ms {'✅' if gemini_ok else '❌'}")
    print(f"   Message ACK: {ack_time:.1f}ms {'✅' if ack_ok else '❌'}")
    print(f"   Total Test Time: {total_time:.1f}ms")
    
    # Análise de gargalos
    print("\n🎯 ANÁLISE DE GARGALOS:")
    times = [
        ("Health Check", health_time),
        ("Agent Lookup", agent_time),
        ("Supabase Query", supabase_time),
        ("Mem0 Search", mem0_time),
        ("Gemini Direct", gemini_time),
        ("Message ACK", ack_time)
    ]
    
    # Ordenar por tempo (maior primeiro)
    times.sort(key=lambda x: x[1], reverse=True)
    
    for i, (name, duration) in enumerate(times):
        if i == 0:
            print(f"   🔴 MAIOR GARGALO: {name} ({duration:.1f}ms)")
        elif i == 1:
            print(f"   🟡 SEGUNDO MAIOR: {name} ({duration:.1f}ms)")
        else:
            print(f"   🟢 {name}: {duration:.1f}ms")
    
    # Recomendações
    print("\n💡 RECOMENDAÇÕES:")
    if mem0_time > 5000:
        print("   - Mem0 está muito lento (>5s). Considere timeout menor ou cache local.")
    if supabase_time > 1000:
        print("   - Supabase está lento (>1s). Verifique índices e conexão.")
    if gemini_time > 5000:
        print("   - Gemini está lento (>5s). Pode ser throttling ou problema de rede.")
    if ack_time > 2000:
        print("   - ACK da mensagem está lento (>2s). Verifique processamento síncrono.")
    
    print(f"\n⚠️  NOTA: O tempo total de 63s pode incluir:")
    print("   - Debounce configurado (1000ms no seu teste)")
    print("   - Processamento assíncrono em background")
    print("   - Timeouts em APIs externas (Mem0, Supabase)")
    print("   - Múltiplas consultas ao banco de dados")

if __name__ == "__main__":
    analyze_performance()