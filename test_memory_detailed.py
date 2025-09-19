#!/usr/bin/env python3
"""
Teste detalhado de memória do agente
Verifica se o agente consegue lembrar informações entre mensagens
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:80"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def get_agent():
    """Busca um agente disponível"""
    try:
        response = requests.get(f"{BASE_URL}/v1/agents", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]["id"]
            elif isinstance(data, dict) and "agents" in data and len(data["agents"]) > 0:
                return data["agents"][0]["id"]
        return None
    except Exception as e:
        print(f"Erro ao buscar agente: {e}")
        return None

def send_message(agent_id, user_id, session_id, message, debounce=5000):
    """Envia uma mensagem para o agente"""
    payload = {
        "mensagem": message,
        "agent_id": agent_id,
        "user_id": user_id,
        "session_id": session_id,
        "debounce": debounce,
        "message_id": str(uuid.uuid4()),
        "cliente_id": "test_client",
        "id_conta": str(uuid.uuid4())
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/messages", headers=HEADERS, json=payload, timeout=30)
        print(f"Mensagem enviada: '{message}' -> Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Erro: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False

def test_memory_persistence():
    """Testa a persistência da memória do agente"""
    print("=" * 60)
    print("TESTE DETALHADO DE MEMÓRIA DO AGENTE")
    print("=" * 60)
    
    # Busca um agente
    agent_id = get_agent()
    if not agent_id:
        print("❌ Erro: Nenhum agente encontrado!")
        return False
    
    print(f"✅ Agente encontrado: {agent_id}")
    
    # IDs únicos para este teste
    user_id = f"memory_test_user_{int(time.time())}"
    session_id = str(uuid.uuid4())
    
    print(f"📝 User ID: {user_id}")
    print(f"📝 Session ID: {session_id}")
    print()
    
    # Sequência de mensagens para testar memória
    messages = [
        "Olá! Meu nome é Carlos e eu tenho 35 anos. Por favor, lembre-se dessas informações.",
        "Qual é o meu nome?",
        "Quantos anos eu tenho?",
        "Eu trabalho como engenheiro de software na empresa TechCorp. Lembre-se disso também.",
        "Onde eu trabalho e qual é a minha profissão?",
        "Você pode me fazer um resumo de tudo que sabe sobre mim?"
    ]
    
    print("🚀 Iniciando sequência de mensagens...")
    print()
    
    for i, message in enumerate(messages, 1):
        print(f"📤 Mensagem {i}: {message}")
        
        success = send_message(agent_id, user_id, session_id, message)
        
        if not success:
            print(f"❌ Falha ao enviar mensagem {i}")
            return False
        
        # Aguarda um pouco entre mensagens para evitar rate limiting
        time.sleep(3)
        print()
    
    print("✅ Todas as mensagens foram enviadas com sucesso!")
    print()
    print("🔍 Aguarde alguns segundos e verifique os logs do webhook para ver as respostas...")
    print("📋 O agente deve:")
    print("   1. Lembrar do nome 'Carlos'")
    print("   2. Lembrar da idade '35 anos'")
    print("   3. Lembrar da profissão 'engenheiro de software'")
    print("   4. Lembrar da empresa 'TechCorp'")
    print("   5. Fazer um resumo completo no final")
    print()
    print(f"🔗 User ID usado: {user_id}")
    print(f"🔗 Session ID usado: {session_id}")
    
    return True

def test_memory_across_sessions():
    """Testa memória entre sessões diferentes"""
    print("\n" + "=" * 60)
    print("TESTE DE MEMÓRIA ENTRE SESSÕES")
    print("=" * 60)
    
    agent_id = get_agent()
    if not agent_id:
        print("❌ Erro: Nenhum agente encontrado!")
        return False
    
    user_id = f"cross_session_test_{int(time.time())}"
    
    # Primeira sessão
    session_1 = str(uuid.uuid4())
    print(f"📝 Primeira sessão: {session_1}")
    
    send_message(agent_id, user_id, session_1, "Meu nome é Ana e eu gosto de pizza.")
    time.sleep(5)
    
    # Segunda sessão (diferente)
    session_2 = str(uuid.uuid4())
    print(f"📝 Segunda sessão: {session_2}")
    
    send_message(agent_id, user_id, session_2, "Você lembra qual é o meu nome e do que eu gosto?")
    
    print("✅ Teste de sessões cruzadas enviado!")
    print("🔍 Verifique se o agente lembra informações da sessão anterior")
    
    return True

if __name__ == "__main__":
    print(f"🕐 Iniciando teste em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Teste 1: Memória dentro da mesma sessão
    success1 = test_memory_persistence()
    
    if success1:
        time.sleep(10)  # Aguarda processamento
        
        # Teste 2: Memória entre sessões diferentes
        success2 = test_memory_across_sessions()
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO!")
    print("=" * 60)
    print("📊 Verifique os logs do webhook para analisar as respostas do agente.")
    print("🔍 Procure por evidências de que o agente lembrou das informações fornecidas.")