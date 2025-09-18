import requests
import json

# Configuração da API
API_BASE = "http://localhost:7777"
HEADERS = {"Content-Type": "application/json"}

def debug_time_workflow():
    """Debug completo do workflow de criação e uso de time"""
    
    print("🔍 DEBUG: WORKFLOW COMPLETO DE TIME")
    print("=" * 50)
    
    # 1. Criar agente
    print("\n1. Criando agente...")
    agent_data = {
        "name": "Agente Debug",
        "role": "Assistente",
        "instructions": ["Você é um assistente que lembra de tudo sobre o usuário"],
        "user_id": "debug_user"
    }
    response = requests.post(f"{API_BASE}/agents", json=agent_data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        agent_result = response.json()
        agent_name = agent_result['agent']['name']
        print(f"✅ Agente criado: {agent_name}")
    else:
        print(f"❌ Erro: {response.text}")
        return
    
    # 2. Criar time
    print("\n2. Criando time...")
    team_data = {
        "name": "Time Debug",
        "description": "Time para debug",
        "agent_names": [agent_name],
        "user_id": "debug_user"
    }
    response = requests.post(f"{API_BASE}/teams", json=team_data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        team_result = response.json()
        team_name = team_result['team']['name']
        print(f"✅ Time criado: {team_name}")
        print(f"Dados completos do time: {json.dumps(team_result, indent=2)}")
    else:
        print(f"❌ Erro: {response.text}")
        return
    
    # 3. Listar times para verificar se foi criado
    print("\n3. Listando times após criação...")
    response = requests.get(f"{API_BASE}/teams", headers=HEADERS)
    if response.status_code == 200:
        teams_data = response.json()
        print(f"Times disponíveis: {json.dumps(teams_data, indent=2)}")
    else:
        print(f"❌ Erro ao listar: {response.text}")
    
    # 4. Tentar conversar usando diferentes formatos de ID
    print("\n4. Testando conversa com diferentes IDs...")
    
    # Teste 1: Nome do time
    print("\n4.1. Testando com nome do time:")
    chat_data = {
        "message": "Meu nome é João e sou engenheiro",
        "user_id": "debug_user",
        "team_id": team_name
    }
    response = requests.post(f"{API_BASE}/teams/run", json=chat_data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result}")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 2: Sem team_id (talvez use o agente diretamente)
    print("\n4.2. Testando sem team_id:")
    chat_data = {
        "message": "Meu nome é João e sou engenheiro",
        "user_id": "debug_user"
    }
    response = requests.post(f"{API_BASE}/teams/run", json=chat_data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result}")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Teste 3: Endpoint de agente direto
    print("\n4.3. Testando endpoint de agente direto:")
    chat_data = {
        "message": "Meu nome é João e sou engenheiro",
        "user_id": "debug_user",
        "agent_id": agent_name
    }
    response = requests.post(f"{API_BASE}/agents/run", json=chat_data, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result}")
    else:
        print(f"❌ Erro: {response.text}")

if __name__ == "__main__":
    debug_time_workflow()