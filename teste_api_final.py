#!/usr/bin/env python3
"""
Script de teste para verificar se a API completa está funcionando corretamente
após a remoção do PostgreSQL e uso exclusivo do Supabase.
"""

import requests
import json
import uuid
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:80"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health():
    """Testa o endpoint de health"""
    print("🔍 Testando endpoint de health...")
    try:
        response = requests.get(f"{BASE_URL}/v1/health", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data}")
            return True
        else:
            print(f"❌ Health check falhou: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_agents():
    """Testa o endpoint de agentes"""
    print("\n🤖 Testando endpoint de agentes...")
    try:
        response = requests.get(f"{BASE_URL}/v1/agents", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agentes encontrados: {len(data)} agentes")
            return True
        else:
            print(f"❌ Busca de agentes falhou: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na busca de agentes: {e}")
        return False

def test_chat():
    """Testa o endpoint de chat"""
    print("\n💬 Testando endpoint de chat...")
    try:
        chat_data = {
            "message": "Olá, como você está?",
            "agent_name": "Especialista em Produtos",
            "user_id": "test-user-123",
            "session_id": str(uuid.uuid4())
        }
        
        response = requests.post(f"{BASE_URL}/v1/chat", headers=headers, json=chat_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat funcionando: {data.get('response', 'Sem resposta')}")
            return True
        else:
            print(f"❌ Chat falhou: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        return False

def test_memory_search():
    """Testa o endpoint de busca de memória"""
    print("\n🧠 Testando endpoint de busca de memória...")
    try:
        params = {
            "user_id": "test-user-123",
            "query": "teste",
            "limit": 5
        }
        
        response = requests.get(f"{BASE_URL}/v1/memory/search", headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Busca de memória funcionando: {len(data.get('memories', []))} memórias encontradas")
            return True
        else:
            print(f"❌ Busca de memória falhou: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na busca de memória: {e}")
        return False

def test_knowledge_search():
    """Testa o endpoint de busca de conhecimento"""
    print("\n📚 Testando endpoint de busca de conhecimento...")
    try:
        response = requests.get(f"{BASE_URL}/v1/knowledge/search?query=teste&limit=3", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Busca de conhecimento funcionando: {len(data.get('results', []))} resultados")
            return True
        else:
            print(f"❌ Busca de conhecimento falhou: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na busca de conhecimento: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API completa...")
    print(f"📍 URL base: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Agentes", test_agents),
        ("Chat", test_chat),
        ("Busca de Memória", test_memory_search),
        ("Busca de Conhecimento", test_knowledge_search)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado final: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 Todos os testes passaram! A API está funcionando corretamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()