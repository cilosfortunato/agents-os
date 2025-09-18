#!/usr/bin/env python3
"""
Teste específico para debugar o fluxo completo de memória
"""
import requests
import time
import json
from datetime import datetime

# Configurações
API_BASE = "http://localhost:8002"
HEADERS = {"X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"}

def test_memory_flow():
    """Testa o fluxo completo de memória passo a passo"""
    print("🔍 TESTE DETALHADO DO FLUXO DE MEMÓRIA")
    print("=" * 60)
    
    # IDs únicos para este teste
    user_id = f"test_user_{int(time.time())}"
    session_id = f"session_{int(time.time())}"
    agent_id = "test_agent_123"
    
    print(f"📋 IDs do teste:")
    print(f"   User ID: {user_id}")
    print(f"   Session ID: {session_id}")
    print(f"   Agent ID: {agent_id}")
    
    # Primeira mensagem
    print(f"\n📤 PRIMEIRA MENSAGEM")
    message1 = {
        "mensagem": "Oi, meu nome é João e eu adoro pizza margherita",
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": agent_id,
        "message_id": "msg-001"
    }
    
    print(f"📋 Enviando: {message1['mensagem']}")
    response1 = requests.post(f"{API_BASE}/v1/messages", json=message1, headers=HEADERS)
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✅ Resposta 1: {result1['messages'][0][:100]}...")
        print(f"📊 Session ID retornado: {result1.get('session_id')}")
    else:
        print(f"❌ Erro na primeira mensagem: {response1.status_code}")
        print(f"   Detalhes: {response1.text}")
        return
    
    # Aguarda para garantir que foi salvo
    print(f"\n⏳ Aguardando 3 segundos para garantir salvamento...")
    time.sleep(3)
    
    # Verifica memória via endpoint
    print(f"\n🔍 VERIFICANDO MEMÓRIA VIA ENDPOINT")
    try:
        memory_search = requests.get(
            f"{API_BASE}/v1/memory/search",
            params={"user_id": user_id, "query": "João pizza", "limit": 5},
            headers=HEADERS
        )
        
        if memory_search.status_code == 200:
            memory_data = memory_search.json()
            print(f"📊 Status da busca: {memory_search.status_code}")
            print(f"📊 Memórias encontradas: {len(memory_data.get('memories', []))}")
            
            for i, mem in enumerate(memory_data.get('memories', [])):
                print(f"   {i+1}. Fonte: {mem.get('source', 'N/A')}")
                print(f"      Conteúdo: {mem.get('content', 'N/A')[:100]}...")
                print(f"      Timestamp: {mem.get('timestamp', 'N/A')}")
        else:
            print(f"❌ Erro na busca de memória: {memory_search.status_code}")
            print(f"   Resposta: {memory_search.text}")
    except Exception as e:
        print(f"❌ Erro ao verificar memória: {e}")
    
    # Segunda mensagem - teste de memória
    print(f"\n📤 SEGUNDA MENSAGEM - Testando memória")
    message2 = {
        "mensagem": "Qual é o meu nome e qual comida eu gosto?",
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": agent_id,
        "message_id": "msg-002"
    }
    
    print(f"📋 Enviando: {message2['mensagem']}")
    response2 = requests.post(f"{API_BASE}/v1/messages", json=message2, headers=HEADERS)
    
    if response2.status_code == 200:
        result2 = response2.json()
        response_text = result2['messages'][0]
        print(f"✅ Resposta 2: {response_text}")
        
        # Análise da resposta
        print(f"\n📊 ANÁLISE DA MEMÓRIA:")
        lembrou_nome = "joão" in response_text.lower()
        lembrou_pizza = "pizza" in response_text.lower() or "margherita" in response_text.lower()
        
        print(f"  🏷️  Lembrou do nome (João): {'✅' if lembrou_nome else '❌'}")
        print(f"  🍕 Lembrou da comida (pizza): {'✅' if lembrou_pizza else '❌'}")
        
        if lembrou_nome and lembrou_pizza:
            print(f"🎉 SUCESSO: O sistema lembrou do contexto!")
        else:
            print(f"⚠️  PROBLEMA: O sistema não lembrou do contexto anterior")
    else:
        print(f"❌ Erro na segunda mensagem: {response2.status_code}")
        print(f"   Detalhes: {response2.text}")
    
    # Verificação final da memória
    print(f"\n🔍 VERIFICAÇÃO FINAL DA MEMÓRIA")
    try:
        final_search = requests.get(
            f"{API_BASE}/v1/memory/search",
            params={"user_id": user_id, "query": "conversa", "limit": 10},
            headers=HEADERS
        )
        
        if final_search.status_code == 200:
            final_data = final_search.json()
            print(f"📊 Total de memórias após teste: {len(final_data.get('memories', []))}")
            
            for i, mem in enumerate(final_data.get('memories', [])):
                print(f"   {i+1}. {mem.get('content', 'N/A')[:80]}...")
        else:
            print(f"❌ Erro na verificação final: {final_search.status_code}")
    except Exception as e:
        print(f"❌ Erro na verificação final: {e}")

if __name__ == "__main__":
    test_memory_flow()