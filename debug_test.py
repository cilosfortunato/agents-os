#!/usr/bin/env python3
"""
Script de debug para identificar problemas no sistema
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:8002"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def test_agents_endpoint():
    """Testa se conseguimos listar agentes"""
    print("🔍 Testando endpoint /v1/agents...")
    try:
        response = requests.get(f"{BASE_URL}/v1/agents", headers=HEADERS)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            agents = response.json()
            print(f"Agentes encontrados: {len(agents)}")
            if agents:
                print(f"Primeiro agente: {agents[0]}")
                return agents[0]
            else:
                print("Lista de agentes está vazia")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def test_simple_message(agent_id):
    """Testa uma mensagem simples"""
    print(f"\n📝 Testando mensagem simples com agent_id: {agent_id}")
    
    payload = {
        "mensagem": "Olá, qual é o seu nome?",
        "agent_id": agent_id,
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/messages", headers=HEADERS, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro na requisição: {e}")

def main():
    print("🚀 Iniciando debug do sistema")
    print("=" * 50)
    
    # Testa listagem de agentes
    agent = test_agents_endpoint()
    
    if agent and agent.get("id"):
        # Testa mensagem simples
        test_simple_message(agent["id"])
    else:
        print("❌ Não foi possível encontrar agentes para testar")

if __name__ == "__main__":
    main()