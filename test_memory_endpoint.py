#!/usr/bin/env python3
"""
Teste específico para o endpoint /v1/memory/search
"""

import requests
import json

def test_memory_endpoint():
    """Testa o endpoint /v1/memory/search diretamente"""
    print("🔍 TESTE DO ENDPOINT /v1/memory/search")
    print("=" * 50)
    
    base_url = "http://localhost:80"
    headers = {
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
        "Content-Type": "application/json"
    }
    
    try:
        # Teste 1: Buscar por "João"
        print("🔍 Testando busca por 'João'...")
        params = {
            "user_id": "test_user_memory",
            "query": "João",
            "limit": 5
        }
        
        response = requests.get(f"{base_url}/v1/memory/search", params=params, headers=headers)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memórias encontradas: {data['total']}")
            print(f"📋 Query: {data['query']}")
            print(f"👤 User ID: {data['user_id']}")
            
            for i, memory in enumerate(data['memories'], 1):
                print(f"   {i}. Fonte: {memory['source']}")
                print(f"      Conteúdo: {memory['content'][:100]}...")
                print(f"      Timestamp: {memory['timestamp']}")
                print()
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
        
        # Teste 2: Buscar por "pizza"
        print("🔍 Testando busca por 'pizza'...")
        params = {
            "user_id": "test_user_memory",
            "query": "pizza",
            "limit": 5
        }
        
        response = requests.get(f"{base_url}/v1/memory/search", params=params, headers=headers)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memórias encontradas: {data['total']}")
            
            for i, memory in enumerate(data['memories'], 1):
                print(f"   {i}. Fonte: {memory['source']}")
                print(f"      Conteúdo: {memory['content'][:100]}...")
                print()
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_endpoint()