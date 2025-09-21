#!/usr/bin/env python3
"""
Teste dos endpoints da API com o sistema corrigido
"""

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Configurações da API
API_BASE_URL = "http://localhost:80"
API_KEY = os.getenv("X_API_KEY", "151fb361-f295-4a4f-84c9-ec1f42599a67")

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_health_endpoint():
    """Testa o endpoint de health"""
    print("1. Testando endpoint /health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {data}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return False

def test_create_agent():
    """Testa criação de agente via API"""
    print("\n2. Testando criação de agente...")
    
    agent_data = {
        "name": "teste-api-openai",
        "role": "Assistente de teste via API",
        "instructions": ["Você é um assistente útil que responde de forma concisa."],
        "model": "gpt-4o-mini",
        "provider": "openai"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/agents",
            headers=headers,
            json=agent_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Agente criado: {data}")
            return data.get("agent_id")
        else:
            print(f"Erro: {response.text}")
            return None
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def test_chat_endpoint(agent_name="teste-api-openai"):
    """Testa o endpoint de chat"""
    print(f"\n3. Testando chat com agente {agent_name}...")
    
    chat_data = {
        "message": "Olá! Como você está?",
        "agent_name": agent_name,
        "user_id": "test-user-api"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            headers=headers,
            json=chat_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta do chat: {data}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=== Teste dos Endpoints da API ===")
    
    # Teste 1: Health check
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("❌ API não está respondendo. Verifique se está rodando.")
        return
    
    # Teste 2: Criar agente
    agent_id = test_create_agent()
    
    # Teste 3: Chat
    chat_ok = test_chat_endpoint()
    
    # Resumo
    print("\n=== Resumo dos Testes ===")
    print(f"✅ Health check: {'OK' if health_ok else 'FALHOU'}")
    print(f"✅ Criação de agente: {'OK' if agent_id else 'FALHOU'}")
    print(f"✅ Chat: {'OK' if chat_ok else 'FALHOU'}")
    
    if health_ok and agent_id and chat_ok:
        print("\n🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()