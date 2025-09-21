#!/usr/bin/env python3
"""
Teste específico para o agente real carregado do Supabase
Agente ID: da93fcc7-cf93-403e-aa99-9e295080d692
"""

import requests
import json
import uuid
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost:8000"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
AGENT_ID = "da93fcc7-cf93-403e-aa99-9e295080d692"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health_check():
    """Testa o health check da API"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK - {data['agents']} agentes disponíveis")
            print(f"   Supabase conectado: {data.get('supabase_connected', False)}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_list_agents():
    """Lista todos os agentes disponíveis"""
    print("\n📋 Listando agentes disponíveis...")
    try:
        response = requests.get(f"{API_BASE_URL}/agents", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['total']} agentes encontrados:")
            for agent in data['agents']:
                print(f"   - ID: {agent.get('id', 'N/A')}")
                print(f"     Nome: {agent.get('name', 'N/A')}")
                print(f"     Modelo: {agent.get('model', 'N/A')}")
            return data['agents']
        else:
            print(f"❌ Erro ao listar agentes: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar agentes: {e}")
        return []

def test_get_specific_agent():
    """Testa busca do agente específico"""
    print(f"\n🎯 Buscando agente específico: {AGENT_ID}")
    try:
        response = requests.get(f"{API_BASE_URL}/agents/{AGENT_ID}", headers=headers)
        if response.status_code == 200:
            agent = response.json()
            print(f"✅ Agente encontrado:")
            print(f"   Nome: {agent.get('name', 'N/A')}")
            print(f"   Role: {agent.get('role', 'N/A')}")
            print(f"   Modelo: {agent.get('model', 'N/A')}")
            print(f"   Provider: {agent.get('provider', 'N/A')}")
            return agent
        else:
            print(f"❌ Agente não encontrado: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao buscar agente: {e}")
        return None

def test_chat_with_agent():
    """Testa chat com o agente específico"""
    print(f"\n💬 Testando chat com agente {AGENT_ID}...")
    
    chat_data = {
        "message": "Olá! Como você pode me ajudar?",
        "agent_id": AGENT_ID,
        "user_id": "test_user_123",
        "session_id": str(uuid.uuid4())
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/chat", headers=headers, json=chat_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat realizado com sucesso!")
            print(f"   Resposta: {data.get('response', 'N/A')}")
            print(f"   Agente: {data.get('agent_name', 'N/A')}")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Usage: {data.get('usage', {})}")
            return data
        else:
            print(f"❌ Erro no chat: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        return None

def test_v1_messages_endpoint():
    """Testa o endpoint /v1/messages (formato da API completa)"""
    print(f"\n📨 Testando endpoint /v1/messages...")
    
    message_data = {
        "mensagem": "Qual é o horário de funcionamento?",
        "agent_id": AGENT_ID,
        "user_id": "test_user_456",
        "session_id": str(uuid.uuid4()),
        "message_id": str(uuid.uuid4()),
        "cliente_id": "cliente_teste",
        "id_conta": "conta_teste",
        "debounce": 0
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/v1/messages", headers=headers, json=message_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mensagem enviada com sucesso!")
            print(f"   Resposta: {data.get('messages', ['N/A'])[0]}")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Agent Usage: {data.get('agent_usage', {})}")
            return data
        else:
            print(f"❌ Erro no endpoint /v1/messages: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro no endpoint /v1/messages: {e}")
        return None

def main():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES COM AGENTE REAL DO SUPABASE")
    print("=" * 60)
    
    # Testa health check
    health_ok = test_health_check()
    
    # Lista agentes
    agents = test_list_agents()
    
    # Busca agente específico
    agent = test_get_specific_agent()
    
    # Testa chat
    chat_result = test_chat_with_agent()
    
    # Testa endpoint v1/messages
    v1_result = test_v1_messages_endpoint()
    
    # Resumo dos testes
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"   Health Check: {'✅ OK' if health_ok else '❌ FALHOU'}")
    print(f"   Agentes listados: {'✅ OK' if agents else '❌ FALHOU'}")
    print(f"   Agente específico: {'✅ OK' if agent else '❌ FALHOU'}")
    print(f"   Chat: {'✅ OK' if chat_result else '❌ FALHOU'}")
    print(f"   Endpoint /v1/messages: {'✅ OK' if v1_result else '❌ FALHOU'}")
    
    if all([health_ok, agents, agent, chat_result, v1_result]):
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM!")

if __name__ == "__main__":
    main()