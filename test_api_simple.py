import requests
import json

# Dados para criar um agente com a nova estrutura
agent_data = {
    "name": "Assistente de Vendas",
    "role": "assistente especializado em vendas",
    "instructions": [
        "Seja sempre prestativo e profissional",
        "Ajude com informações sobre produtos",
        "Forneça suporte ao cliente"
    ],
    "user_id": "default_user"
}

headers = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

try:
    # Teste de criação de agente
    print("Testando criação de agente com nova estrutura...")
    response = requests.post("http://localhost:80/agents", 
                           headers=headers, 
                           json=agent_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        agent_response = response.json()
        print("✅ Agente criado com sucesso!")
        print(f"ID do agente: {agent_response['agent']['id']}")
        
        # Teste de execução do agente
        agent_id = agent_response['agent']['id']
        run_data = {
            "message": "Olá, preciso de ajuda com produtos",
            "user_id": "default_user"
        }
        
        print(f"\nTestando execução do agente {agent_id}...")
        run_response = requests.post(f"http://localhost:80/agents/{agent_id}/run",
                                   headers=headers,
                                   json=run_data)
        
        print(f"Status Code: {run_response.status_code}")
        print(f"Response: {run_response.text}")
        
    else:
        print("❌ Erro na criação do agente")
        
except Exception as e:
    print(f"Erro: {e}")