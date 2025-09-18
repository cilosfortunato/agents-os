#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de memória dupla
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost:8002"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_chat_endpoint():
    """Testa o endpoint de chat com memória dupla"""
    print("🧪 Testando endpoint /v1/chat com memória dupla...")
    
    # Dados de teste
    user_id = "test_user_123"
    session_id = str(uuid.uuid4())
    
    # Primeira mensagem
    print("\n📝 Enviando primeira mensagem...")
    payload1 = {
        "message": "Olá! Meu nome é João e eu trabalho como desenvolvedor Python.",
        "user_id": user_id,
        "session_id": session_id,
        "agent_name": "Assistente Pessoal"
    }
    
    response1 = requests.post(
        f"{API_BASE_URL}/v1/chat",
        headers=headers,
        json=payload1
    )
    
    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"Resposta: {data1['response']}")
        print(f"Session ID: {data1['session_id']}")
    else:
        print(f"Erro: {response1.text}")
        return False
    
    # Aguarda um pouco
    time.sleep(2)
    
    # Segunda mensagem (deve lembrar do contexto)
    print("\n📝 Enviando segunda mensagem (teste de memória)...")
    payload2 = {
        "message": "Qual é o meu nome e profissão?",
        "user_id": user_id,
        "session_id": session_id,
        "agent_name": "Assistente Pessoal"
    }
    
    response2 = requests.post(
        f"{API_BASE_URL}/v1/chat",
        headers=headers,
        json=payload2
    )
    
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Resposta: {data2['response']}")
        
        # Verifica se lembrou do nome e profissão
        resposta = data2['response'].lower()
        if "joão" in resposta and ("desenvolvedor" in resposta or "python" in resposta):
            print("✅ SUCESSO: O agente lembrou das informações!")
            return True
        else:
            print("❌ FALHA: O agente não lembrou das informações.")
            return False
    else:
        print(f"Erro: {response2.text}")
        return False

def test_messages_endpoint():
    """Testa o endpoint /v1/messages com memória dupla"""
    print("\n🧪 Testando endpoint /v1/messages com memória dupla...")
    
    # Dados de teste
    user_id = "test_user_456"
    session_id = str(uuid.uuid4())
    agent_id = "1677dc47-20d0-442a-80a8-171f00d39d39"  # ID do agente de exemplo
    
    # Primeira mensagem
    print("\n📝 Enviando primeira mensagem...")
    payload1 = {
        "mensagem": "Oi! Eu sou Maria e adoro viajar. Meu destino favorito é Paris.",
        "agent_id": agent_id,
        "session_id": session_id,
        "user_id": user_id,
        "message_id": str(uuid.uuid4()),
        "cliente_id": "",
        "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
    }
    
    response1 = requests.post(
        f"{API_BASE_URL}/v1/messages",
        headers=headers,
        json=payload1
    )
    
    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"Resposta: {data1['messages'][0]}")
    else:
        print(f"Erro: {response1.text}")
        return False
    
    # Aguarda um pouco
    time.sleep(2)
    
    # Segunda mensagem (teste de memória)
    print("\n📝 Enviando segunda mensagem (teste de memória)...")
    payload2 = {
        "mensagem": "Qual é o meu nome e qual lugar eu mais gosto de visitar?",
        "agent_id": agent_id,
        "session_id": session_id,
        "user_id": user_id,
        "message_id": str(uuid.uuid4()),
        "cliente_id": "",
        "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
    }
    
    response2 = requests.post(
        f"{API_BASE_URL}/v1/messages",
        headers=headers,
        json=payload2
    )
    
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        data2 = response2.json()
        resposta = data2['messages'][0]
        print(f"Resposta: {resposta}")
        
        # Verifica se lembrou do nome e destino
        resposta_lower = resposta.lower()
        if "maria" in resposta_lower and "paris" in resposta_lower:
            print("✅ SUCESSO: O agente lembrou das informações!")
            return True
        else:
            print("❌ FALHA: O agente não lembrou das informações.")
            return False
    else:
        print(f"Erro: {response2.text}")
        return False

def test_api_status():
    """Testa se a API está online"""
    print("🔍 Verificando status da API...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Online - Status: {data['status']}")
            print(f"Versão: {data['version']}")
            return True
        else:
            print(f"❌ API com problema - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema de memória dupla")
    print("=" * 60)
    
    # Teste 1: Status da API
    if not test_api_status():
        print("❌ API não está funcionando. Abortando testes.")
        return
    
    print("\n" + "=" * 60)
    
    # Teste 2: Endpoint /v1/chat
    chat_success = test_chat_endpoint()
    
    print("\n" + "=" * 60)
    
    # Teste 3: Endpoint /v1/messages
    messages_success = test_messages_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"Chat endpoint: {'✅ PASSOU' if chat_success else '❌ FALHOU'}")
    print(f"Messages endpoint: {'✅ PASSOU' if messages_success else '❌ FALHOU'}")
    
    if chat_success and messages_success:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de memória dupla funcionando!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM. Verifique a implementação.")

if __name__ == "__main__":
    main()