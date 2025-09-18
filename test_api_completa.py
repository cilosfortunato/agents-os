#!/usr/bin/env python3
"""
Teste completo da API com Knowledge (RAG) e Memória (Mem0)
Demonstra todas as funcionalidades implementadas
"""

import requests
import json
import time
from typing import Dict, Any

# Configurações
API_BASE_URL = "http://localhost:8001"
INTERNAL_API_URL = "http://localhost:80"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

def test_api_status():
    """Testa o status da API"""
    print("🔍 Testando status da API...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Online: {data['message']}")
            print(f"Features: {', '.join(data['features'])}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def test_health_check():
    """Testa o health check do sistema"""
    print("\n🏥 Testando health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/v1/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sistema: {data['status']}")
            print("Componentes:")
            for component, status in data['components'].items():
                print(f"  - {component}: {status}")
            print("Features:")
            for feature, enabled in data['features'].items():
                print(f"  - {feature}: {'✅' if enabled else '❌'}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_knowledge_search():
    """Testa a busca na base de conhecimento"""
    print("\n📚 Testando busca na base de conhecimento...")
    try:
        queries = ["modo noturno", "bateria", "garantia"]
        
        for query in queries:
            response = requests.get(f"{API_BASE_URL}/v1/knowledge/search", params={"query": query})
            print(f"Busca por '{query}': Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Encontrados {data['total']} resultados")
                for i, result in enumerate(data['results'][:2]):  # Mostra apenas os 2 primeiros
                    print(f"    {i+1}. {result['content'][:60]}...")
            else:
                print(f"  ❌ Erro na busca: {response.text}")
        
        return True
    except Exception as e:
        print(f"❌ Erro na busca de conhecimento: {e}")
        return False

def test_memory_search():
    """Testa a busca na memória"""
    print("\n🧠 Testando busca na memória...")
    try:
        user_id = "test_user_123"
        query = "produto"
        
        response = requests.get(f"{API_BASE_URL}/v1/memory/search", params={
            "user_id": user_id,
            "query": query
        })
        
        print(f"Busca na memória: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Encontradas {data['total']} memórias para usuário {user_id}")
            for i, memory in enumerate(data['memories']):
                print(f"  {i+1}. {memory['text'][:60]}...")
        else:
            print(f"❌ Erro na busca de memória: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro na busca de memória: {e}")
        return False

def test_agent_creation():
    """Testa a criação de agente inteligente"""
    print("\n🤖 Testando criação de agente inteligente...")
    try:
        agent_data = {
            "name": "Assistente Teste API",
            "role": "Assistente de suporte técnico especializado",
            "instructions": [
                "Você é um assistente especializado em produtos tecnológicos",
                "Use sempre a base de conhecimento para responder perguntas",
                "Mantenha um tom profissional e amigável",
                "Se não souber a resposta, consulte a documentação"
            ],
            "user_id": "api_test_user"
        }
        
        response = requests.post(f"{API_BASE_URL}/v1/agents", json=agent_data)
        print(f"Criação de agente: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            print(f"Agent ID: {data.get('agent_id', 'N/A')}")
            print(f"Features: {', '.join(data['features'])}")
            return data.get('agent_id')
        else:
            print(f"❌ Erro na criação: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na criação de agente: {e}")
        return None

def test_intelligent_query():
    """Testa consulta inteligente com Knowledge e Memória"""
    print("\n💬 Testando consulta inteligente...")
    try:
        queries = [
            "Como ativar o modo noturno?",
            "Quanto tempo dura a bateria?",
            "Qual é a garantia do produto?",
            "Como reiniciar o dispositivo?"
        ]
        
        user_id = "test_user_complete"
        
        for i, question in enumerate(queries):
            print(f"\n--- Pergunta {i+1}: {question} ---")
            
            query_data = {
                "user_id": user_id,
                "question": question,
                "agent_name": "Especialista em Produtos"
            }
            
            response = requests.post(f"{API_BASE_URL}/v1/query", json=query_data)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Resposta: {data['answer'][:100]}...")
                print(f"Contexto usado: {data['context_used']}")
            else:
                print(f"❌ Erro na consulta: {response.text}")
            
            time.sleep(1)  # Pausa entre consultas
        
        return True
    except Exception as e:
        print(f"❌ Erro na consulta inteligente: {e}")
        return False

def test_knowledge_sync():
    """Testa sincronização da base de conhecimento"""
    print("\n🔄 Testando sincronização da base de conhecimento...")
    try:
        response = requests.post(f"{API_BASE_URL}/v1/knowledge/sync")
        print(f"Sincronização: Status {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Erro na sincronização: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTE COMPLETO DA API COM KNOWLEDGE E MEMÓRIA")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Status da API", test_api_status),
        ("Health Check", test_health_check),
        ("Busca Knowledge", test_knowledge_search),
        ("Busca Memória", test_memory_search),
        ("Criação de Agente", test_agent_creation),
        ("Consulta Inteligente", test_intelligent_query),
        ("Sincronização Knowledge", test_knowledge_sync)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = "✅ PASSOU" if result else "❌ FALHOU"
        except Exception as e:
            results[test_name] = f"❌ ERRO: {e}"
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{test_name:.<30} {result}")
        if "✅" in result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente!")
    elif passed > total // 2:
        print("⚠️  Maioria dos testes passou. Verifique os que falharam.")
    else:
        print("❌ Muitos testes falharam. Sistema precisa de ajustes.")
    
    print("\n💡 Para usar a API:")
    print(f"   - Documentação: http://localhost:8001/docs")
    print(f"   - Status: http://localhost:8001/")
    print(f"   - Health: http://localhost:8001/v1/health")

if __name__ == "__main__":
    main()