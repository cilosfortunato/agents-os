#!/usr/bin/env python3
"""
Teste específico do fluxo de memória no processamento de mensagens
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:80"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_memory_flow():
    """Testa o fluxo completo de memória"""
    print("=" * 60)
    print("TESTE DO FLUXO COMPLETO DE MEMÓRIA")
    print("=" * 60)
    
    # Gera IDs únicos para o teste
    user_id = f"test_user_{int(time.time())}"
    session_id = str(uuid.uuid4())
    
    print(f"👤 User ID: {user_id}")
    print(f"🔗 Session ID: {session_id}")
    
    # 1. Busca agentes disponíveis
    print("\n1️⃣ Buscando agentes disponíveis...")
    try:
        response = requests.get(f"{BASE_URL}/v1/agents", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            agents_data = response.json()
            agents = agents_data.get("agents", [])
            if agents:
                agent_id = agents[0]["id"]
                agent_name = agents[0]["name"]
                print(f"✅ Agente encontrado: {agent_name} (ID: {agent_id})")
            else:
                print("❌ Nenhum agente encontrado")
                return False
        else:
            print(f"❌ Erro ao buscar agentes: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 2. Envia primeira mensagem (informações pessoais)
    print("\n2️⃣ Enviando primeira mensagem com informações pessoais...")
    message_1 = {
        "mensagem": "Olá! Meu nome é Carlos e tenho 35 anos. Trabalho como engenheiro de software.",
        "agent_id": agent_id,
        "user_id": user_id,
        "session_id": session_id,
        "message_id": str(uuid.uuid4()),
        "debounce": 5000  # 5 segundos para teste rápido
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/messages", headers=HEADERS, json=message_1, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Primeira mensagem enviada com sucesso")
        else:
            print(f"❌ Erro: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 3. Aguarda processamento
    print("\n⏳ Aguardando processamento (8 segundos)...")
    time.sleep(8)
    
    # 4. Envia segunda mensagem (pergunta sobre informações anteriores)
    print("\n3️⃣ Enviando segunda mensagem perguntando sobre informações anteriores...")
    message_2 = {
        "mensagem": "Você lembra qual é meu nome e minha idade?",
        "agent_id": agent_id,
        "user_id": user_id,
        "session_id": session_id,
        "message_id": str(uuid.uuid4()),
        "debounce": 5000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/messages", headers=HEADERS, json=message_2, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Segunda mensagem enviada com sucesso")
        else:
            print(f"❌ Erro: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
    
    # 5. Aguarda processamento
    print("\n⏳ Aguardando processamento (8 segundos)...")
    time.sleep(8)
    
    # 6. Testa busca direta na memória
    print("\n4️⃣ Testando busca direta na memória...")
    try:
        response = requests.get(
            f"{BASE_URL}/v1/memory/search",
            headers=HEADERS,
            params={
                "user_id": user_id,
                "query": "nome idade Carlos",
                "limit": 5
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            memory_data = response.json()
            memories = memory_data.get("memories", [])
            print(f"✅ Memórias encontradas: {len(memories)}")
            
            if memories:
                print("📋 Memórias:")
                for i, memory in enumerate(memories, 1):
                    print(f"   {i}. {memory}")
            else:
                print("⚠️ Nenhuma memória encontrada")
        else:
            print(f"❌ Erro na busca: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # 7. Testa nova sessão com mesmo usuário
    print("\n5️⃣ Testando nova sessão com mesmo usuário...")
    new_session_id = str(uuid.uuid4())
    print(f"🔗 Nova Session ID: {new_session_id}")
    
    message_3 = {
        "mensagem": "Olá novamente! Você se lembra de mim?",
        "agent_id": agent_id,
        "user_id": user_id,
        "session_id": new_session_id,
        "message_id": str(uuid.uuid4()),
        "debounce": 5000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/messages", headers=HEADERS, json=message_3, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Mensagem em nova sessão enviada com sucesso")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n⏳ Aguardando processamento final (8 segundos)...")
    time.sleep(8)
    
    return True

def test_direct_memory_operations():
    """Testa operações diretas de memória"""
    print("\n" + "=" * 60)
    print("TESTE DE OPERAÇÕES DIRETAS DE MEMÓRIA")
    print("=" * 60)
    
    user_id = f"direct_test_{int(time.time())}"
    
    # 1. Adiciona memória diretamente
    print("\n1️⃣ Adicionando memória diretamente...")
    memory_data = {
        "user_id": user_id,
        "content": "O usuário se chama Roberto e tem 28 anos. Gosta de programação Python.",
        "metadata": {"test": "direct_add", "timestamp": datetime.now().isoformat()}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/memory/add", headers=HEADERS, json=memory_data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Memória adicionada diretamente")
            print(f"📊 Resposta: {response.json()}")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # 2. Busca a memória adicionada
    print("\n2️⃣ Buscando memória adicionada...")
    try:
        response = requests.get(
            f"{BASE_URL}/v1/memory/search",
            headers=HEADERS,
            params={
                "user_id": user_id,
                "query": "Roberto Python",
                "limit": 3
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            memory_data = response.json()
            memories = memory_data.get("memories", [])
            print(f"✅ Memórias encontradas: {len(memories)}")
            
            if memories:
                print("📋 Memórias:")
                for i, memory in enumerate(memories, 1):
                    print(f"   {i}. {memory}")
            else:
                print("⚠️ Nenhuma memória encontrada")
        else:
            print(f"❌ Erro na busca: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DO FLUXO DE MEMÓRIA")
    print("=" * 60)
    
    # Testa fluxo completo
    flow_success = test_memory_flow()
    
    # Testa operações diretas
    test_direct_memory_operations()
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Fluxo Completo: {'✅' if flow_success else '❌'}")
    print("\n💡 Dica: Verifique os logs do webhook para ver as respostas do agente")
    print("   Use: python -c \"import requests; print(requests.get('http://localhost:9000/logs').text)\"")