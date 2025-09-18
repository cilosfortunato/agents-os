#!/usr/bin/env python3
"""
Teste detalhado para debugar o fluxo completo de memória
"""

import requests
import json
import time

# Configuração da API
API_BASE = "http://localhost:8002"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def test_memory_flow():
    """Testa o fluxo completo de memória com debug detalhado"""
    
    print("🔍 TESTE DETALHADO DE MEMÓRIA")
    print("=" * 50)
    
    # Dados do teste
    user_id = "test-user-debug"
    session_id = "test-session-debug"
    agent_id = "1677dc47-20d0-442a-80a8-171f00d39d39"
    
    # Primeira mensagem - estabelecendo contexto
    print("\n📤 PRIMEIRA MENSAGEM - Estabelecendo contexto")
    message1 = {
        "mensagem": "Oi, meu nome é João e eu adoro pizza margherita",
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": agent_id,
        "message_id": "msg-001",
        "cliente_id": "",
        "id_conta": "test-account"
    }
    
    print(f"📋 Enviando: {message1['mensagem']}")
    response1 = requests.post(f"{API_BASE}/v1/messages", json=message1, headers=HEADERS)
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✅ Resposta 1: {result1['messages'][0]}")
    else:
        print(f"❌ Erro na primeira mensagem: {response1.status_code} - {response1.text}")
        return
    
    # Aguarda um pouco para garantir que a memória foi salva
    print("\n⏳ Aguardando 2 segundos para garantir que a memória foi salva...")
    time.sleep(2)
    
    # Verifica se a memória foi salva no Supabase
    print("\n🔍 VERIFICANDO MEMÓRIA NO SUPABASE")
    try:
        memory_search = requests.get(
            f"{API_BASE}/v1/memory/search",
            params={"user_id": user_id, "query": "João pizza", "limit": 5},
            headers=HEADERS
        )
        
        if memory_search.status_code == 200:
            memory_data = memory_search.json()
            print(f"📊 Memórias encontradas: {len(memory_data.get('memories', []))}")
            for i, mem in enumerate(memory_data.get('memories', [])):
                print(f"  {i+1}. {mem}")
        else:
            print(f"❌ Erro ao buscar memória: {memory_search.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar memória: {e}")
    
    # Segunda mensagem - testando memória
    print("\n📤 SEGUNDA MENSAGEM - Testando memória")
    message2 = {
        "mensagem": "Qual é o meu nome e qual comida eu gosto?",
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": agent_id,
        "message_id": "msg-002",
        "cliente_id": "",
        "id_conta": "test-account"
    }
    
    print(f"📋 Enviando: {message2['mensagem']}")
    response2 = requests.post(f"{API_BASE}/v1/messages", json=message2, headers=HEADERS)
    
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"✅ Resposta 2: {result2['messages'][0]}")
        
        # Verifica se lembrou do contexto
        resposta = result2['messages'][0].lower()
        lembrou_nome = "joão" in resposta
        lembrou_comida = "pizza" in resposta or "margherita" in resposta
        
        print(f"\n📊 ANÁLISE DA MEMÓRIA:")
        print(f"  🏷️  Lembrou do nome (João): {'✅' if lembrou_nome else '❌'}")
        print(f"  🍕 Lembrou da comida (pizza): {'✅' if lembrou_comida else '❌'}")
        
        if lembrou_nome and lembrou_comida:
            print("🎉 SUCESSO: O sistema de memória está funcionando!")
        else:
            print("⚠️  PROBLEMA: O sistema não lembrou do contexto anterior")
            
    else:
        print(f"❌ Erro na segunda mensagem: {response2.status_code} - {response2.text}")
    
    # Terceira mensagem - teste específico
    print("\n📤 TERCEIRA MENSAGEM - Teste específico")
    message3 = {
        "mensagem": "Me conte sobre nossa conversa anterior",
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": agent_id,
        "message_id": "msg-003",
        "cliente_id": "",
        "id_conta": "test-account"
    }
    
    print(f"📋 Enviando: {message3['mensagem']}")
    response3 = requests.post(f"{API_BASE}/v1/messages", json=message3, headers=HEADERS)
    
    if response3.status_code == 200:
        result3 = response3.json()
        print(f"✅ Resposta 3: {result3['messages'][0]}")
    else:
        print(f"❌ Erro na terceira mensagem: {response3.status_code} - {response3.text}")

if __name__ == "__main__":
    test_memory_flow()