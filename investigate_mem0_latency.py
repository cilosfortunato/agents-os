#!/usr/bin/env python3
"""
Investigação detalhada da latência do Mem0
Testa diferentes aspectos da conexão e operações para identificar o gargalo específico
"""

import time
import os
import requests
import json
from mem0 import MemoryClient
from dotenv import load_dotenv
import logging

# Configurar logging detalhado
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Carregar variáveis de ambiente
load_dotenv()

def test_mem0_api_direct():
    """Testa a API do Mem0 diretamente via HTTP"""
    print("\n=== TESTE 1: API Mem0 Direta (HTTP) ===")
    
    api_key = os.getenv('MEM0_API_KEY')
    if not api_key:
        print("❌ MEM0_API_KEY não encontrada")
        return
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Teste 1.1: Health check da API
    start_time = time.time()
    try:
        response = requests.get(
            'https://api.mem0.ai/v1/memories',
            headers=headers,
            timeout=10,
            params={'user_id': 'test_user', 'limit': 1}
        )
        elapsed = time.time() - start_time
        print(f"✅ Health check: {elapsed:.3f}s - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Erro de autenticação - verificar MEM0_API_KEY")
            return
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ Timeout na API direta após {elapsed:.3f}s")
        return
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Erro na API direta ({elapsed:.3f}s): {e}")
        return

def test_mem0_client_operations():
    """Testa operações específicas do cliente Mem0"""
    print("\n=== TESTE 2: Cliente Mem0 (Operações) ===")
    
    try:
        client = MemoryClient()
        test_user = "test_latency_user"
        
        # Teste 2.1: Busca simples
        print("🔍 Testando busca simples...")
        start_time = time.time()
        try:
            memories = client.search(
                query="teste",
                user_id=test_user,
                limit=3
            )
            elapsed = time.time() - start_time
            print(f"✅ Busca simples: {elapsed:.3f}s - Resultados: {len(memories) if memories else 0}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Erro na busca simples ({elapsed:.3f}s): {e}")
        
        # Teste 2.2: Adicionar memória
        print("💾 Testando adicionar memória...")
        start_time = time.time()
        try:
            messages = [
                {"role": "user", "content": "Teste de latência"},
                {"role": "assistant", "content": "Resposta de teste"}
            ]
            result = client.add(
                messages=messages,
                user_id=test_user
            )
            elapsed = time.time() - start_time
            print(f"✅ Adicionar memória: {elapsed:.3f}s - Sucesso: {bool(result)}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Erro ao adicionar memória ({elapsed:.3f}s): {e}")
        
        # Teste 2.3: Busca após adicionar
        print("🔍 Testando busca após adicionar...")
        start_time = time.time()
        try:
            memories = client.search(
                query="latência",
                user_id=test_user,
                limit=5
            )
            elapsed = time.time() - start_time
            print(f"✅ Busca pós-adição: {elapsed:.3f}s - Resultados: {len(memories) if memories else 0}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Erro na busca pós-adição ({elapsed:.3f}s): {e}")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar cliente Mem0: {e}")

def test_network_connectivity():
    """Testa conectividade de rede com diferentes endpoints"""
    print("\n=== TESTE 3: Conectividade de Rede ===")
    
    endpoints = [
        ("Google DNS", "https://dns.google"),
        ("Mem0 API", "https://api.mem0.ai"),
        ("OpenAI API", "https://api.openai.com"),
    ]
    
    for name, url in endpoints:
        start_time = time.time()
        try:
            response = requests.get(url, timeout=5)
            elapsed = time.time() - start_time
            print(f"✅ {name}: {elapsed:.3f}s - Status: {response.status_code}")
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            print(f"⏰ {name}: Timeout após {elapsed:.3f}s")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ {name}: Erro ({elapsed:.3f}s) - {e}")

def test_concurrent_mem0_requests():
    """Testa múltiplas requisições simultâneas ao Mem0"""
    print("\n=== TESTE 4: Requisições Concorrentes ===")
    
    import threading
    import concurrent.futures
    
    def single_search(user_id, query):
        try:
            client = MemoryClient()
            start_time = time.time()
            memories = client.search(
                query=query,
                user_id=user_id,
                limit=3
            )
            elapsed = time.time() - start_time
            return {"success": True, "time": elapsed, "count": len(memories) if memories else 0}
        except Exception as e:
            elapsed = time.time() - start_time
            return {"success": False, "time": elapsed, "error": str(e)}
    
    # Executar 3 buscas simultâneas
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        start_time = time.time()
        
        for i in range(3):
            future = executor.submit(single_search, f"concurrent_user_{i}", f"teste concorrente {i}")
            futures.append(future)
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
        
        total_elapsed = time.time() - start_time
        
    print(f"⏱️ Tempo total para 3 buscas concorrentes: {total_elapsed:.3f}s")
    for i, result in enumerate(results):
        if result["success"]:
            print(f"✅ Busca {i+1}: {result['time']:.3f}s - {result['count']} resultados")
        else:
            print(f"❌ Busca {i+1}: {result['time']:.3f}s - Erro: {result['error']}")

def main():
    print("🔍 INVESTIGAÇÃO DETALHADA DE LATÊNCIA DO MEM0")
    print("=" * 60)
    
    # Verificar chave de API
    api_key = os.getenv('MEM0_API_KEY')
    if not api_key:
        print("❌ MEM0_API_KEY não encontrada no ambiente")
        return
    
    print(f"🔑 MEM0_API_KEY: {api_key[:10]}...{api_key[-10:]}")
    
    # Executar todos os testes
    test_mem0_api_direct()
    test_mem0_client_operations()
    test_network_connectivity()
    test_concurrent_mem0_requests()
    
    print("\n" + "=" * 60)
    print("🏁 INVESTIGAÇÃO CONCLUÍDA")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Analisar os tempos de resposta acima")
    print("2. Identificar qual operação está causando o gargalo")
    print("3. Verificar se é problema de rede, autenticação ou API")
    print("4. Implementar otimizações baseadas nos resultados")

if __name__ == "__main__":
    main()