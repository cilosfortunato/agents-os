#!/usr/bin/env python3
"""
Teste simples para verificar criação e execução de agente
"""

import requests
import json
import time

# Configurações da API
BASE_URL = "http://localhost:80"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def main():
    print("🧪 TESTE SIMPLES DE AGENTE")
    print("="*50)
    
    # 1. Criar agente
    print("\n1️⃣ Criando agente...")
    agent_data = {
        "name": "Teste Simples",
        "role": "assistente",
        "instructions": ["Você é um assistente útil"],
        "user_id": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/agents", headers=HEADERS, json=agent_data)
    print(f"Status criação: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Erro na criação: {response.text}")
        return
    
    agent_result = response.json()
    agent_id = agent_result.get("agent", {}).get("id")
    print(f"✅ Agente criado: {agent_id}")
    print(f"Resposta completa: {json.dumps(agent_result, indent=2)}")
    
    # 2. Aguardar um pouco
    print("\n2️⃣ Aguardando 2 segundos...")
    time.sleep(2)
    
    # 3. Listar agentes para verificar se existe
    print("\n3️⃣ Listando agentes...")
    response = requests.get(f"{BASE_URL}/agents", headers=HEADERS)
    print(f"Status listagem: {response.status_code}")
    
    if response.status_code == 200:
        agents = response.json()
        print(f"Total de agentes: {agents.get('total', 0)}")
        
        # Verificar se nosso agente está na lista
        found = False
        for agent in agents.get('custom_agents', []):
            if agent.get('id') == agent_id:
                found = True
                print(f"✅ Agente encontrado na lista: {agent.get('name')}")
                break
        
        if not found:
            print(f"❌ Agente {agent_id} NÃO encontrado na lista")
    
    # 4. Tentar executar
    print(f"\n4️⃣ Executando agente {agent_id}...")
    run_data = {
        "message": "Olá, teste simples",
        "user_id": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/agents/{agent_id}/run", headers=HEADERS, json=run_data)
    print(f"Status execução: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Execução bem-sucedida!")
        print(f"Resposta: {result.get('messages', ['Sem mensagem'])[0][:100]}...")
    else:
        print(f"❌ Erro na execução: {response.text}")

if __name__ == "__main__":
    main()