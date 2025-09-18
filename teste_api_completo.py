import requests
import json

# Configuração da API
API_BASE = "http://localhost:7777"
HEADERS = {"Content-Type": "application/json"}

def testar_endpoints():
    """Testa todos os endpoints disponíveis"""
    
    print("🔍 TESTANDO ENDPOINTS DA API")
    print("=" * 40)
    
    # 1. Testar endpoint de agentes
    print("\n1. Testando GET /agents")
    response = requests.get(f"{API_BASE}/agents", headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2)}")
    else:
        print(f"Erro: {response.text}")
    
    # 2. Testar endpoint de times
    print("\n2. Testando GET /teams")
    response = requests.get(f"{API_BASE}/teams", headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2)}")
    else:
        print(f"Erro: {response.text}")
    
    # 3. Testar criação de agente
    print("\n3. Testando POST /agents")
    agent_data = {
        "name": "Agente Teste API",
        "role": "Assistente",
        "instructions": ["Você é um assistente útil"],
        "user_id": "teste_api"
    }
    response = requests.post(f"{API_BASE}/agents", json=agent_data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2)}")
        agent_id = data.get('agent', {}).get('name', 'agente_teste_api')
        print(f"Agent ID criado: {agent_id}")
        
        # 4. Testar criação de time com o agente criado
        print("\n4. Testando POST /teams")
        team_data = {
            "name": "Time Teste API",
            "description": "Time para testar API",
            "agent_names": [agent_id],
            "user_id": "teste_api"
        }
        response = requests.post(f"{API_BASE}/teams", json=team_data, headers=HEADERS)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {json.dumps(data, indent=2)}")
            team_id = data.get('team', {}).get('name', 'time_teste_api')
            
            # 5. Testar conversa com o time
            print("\n5. Testando POST /teams/run")
            chat_data = {
                "message": "Olá, como você está?",
                "user_id": "teste_api",
                "team_id": team_id
            }
            response = requests.post(f"{API_BASE}/teams/run", json=chat_data, headers=HEADERS)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Resposta: {json.dumps(data, indent=2)}")
            else:
                print(f"Erro: {response.text}")
        else:
            print(f"Erro ao criar time: {response.text}")
    else:
        print(f"Erro ao criar agente: {response.text}")
    
    # 6. Testar endpoint de documentação
    print("\n6. Testando GET /docs (Swagger)")
    response = requests.get(f"{API_BASE}/docs", headers=HEADERS)
    print(f"Status: {response.status_code}")
    
    # 7. Testar endpoint de memória
    print("\n7. Testando GET /memory/all")
    response = requests.get(f"{API_BASE}/memory/all?user_id=teste_api", headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2)}")
    else:
        print(f"Erro: {response.text}")

if __name__ == "__main__":
    testar_endpoints()