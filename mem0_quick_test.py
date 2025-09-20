#!/usr/bin/env python3
"""
Teste rápido e limpo do Mem0 para identificar latência
"""

import time
import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

def test_mem0_operations():
    """Testa operações básicas do Mem0 com medição de tempo"""
    print("🔍 TESTE RÁPIDO DE LATÊNCIA DO MEM0")
    print("=" * 50)
    
    try:
        client = MemoryClient()
        test_user = "latency_test_user"
        
        # Teste 1: Busca simples
        print("1️⃣ Testando busca simples...")
        start_time = time.time()
        try:
            memories = client.search(
                query="teste de latência",
                user_id=test_user,
                limit=3
            )
            elapsed = time.time() - start_time
            print(f"   ✅ Busca: {elapsed:.3f}s - {len(memories) if memories else 0} resultados")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Erro na busca ({elapsed:.3f}s): {e}")
        
        # Teste 2: Adicionar memória
        print("2️⃣ Testando adicionar memória...")
        start_time = time.time()
        try:
            messages = [
                {"role": "user", "content": "Teste de performance"},
                {"role": "assistant", "content": "Resposta rápida"}
            ]
            result = client.add(
                messages=messages,
                user_id=test_user
            )
            elapsed = time.time() - start_time
            print(f"   ✅ Adicionar: {elapsed:.3f}s - Sucesso: {bool(result)}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Erro ao adicionar ({elapsed:.3f}s): {e}")
        
        # Teste 3: Busca após adicionar
        print("3️⃣ Testando busca após adicionar...")
        start_time = time.time()
        try:
            memories = client.search(
                query="performance",
                user_id=test_user,
                limit=5
            )
            elapsed = time.time() - start_time
            print(f"   ✅ Busca pós-add: {elapsed:.3f}s - {len(memories) if memories else 0} resultados")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Erro na busca pós-add ({elapsed:.3f}s): {e}")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar cliente: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_mem0_operations()