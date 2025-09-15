import requests
import json

# Configuração da API
API_BASE = "http://localhost:7777"
HEADERS = {"Content-Type": "application/json"}

def listar_times():
    """Lista todos os times disponíveis"""
    response = requests.get(f"{API_BASE}/teams", headers=HEADERS)
    if response.status_code == 200:
        teams = response.json()
        print("📋 TIMES DISPONÍVEIS:")
        print("=" * 30)
        if isinstance(teams, list):
            for team in teams:
                print(f"- Nome: {team.get('name', 'N/A')}")
                print(f"  ID: {team.get('id', 'N/A')}")
                print(f"  Descrição: {team.get('description', 'N/A')}")
                print("-" * 20)
        else:
            print(f"Resposta: {teams}")
    else:
        print(f"❌ Erro ao listar times: {response.text}")

def listar_agentes():
    """Lista todos os agentes disponíveis"""
    response = requests.get(f"{API_BASE}/agents", headers=HEADERS)
    if response.status_code == 200:
        agents = response.json()
        print("\n👥 AGENTES DISPONÍVEIS:")
        print("=" * 30)
        if isinstance(agents, list):
            for agent in agents:
                print(f"- Nome: {agent.get('name', 'N/A')}")
                print(f"  Role: {agent.get('role', 'N/A')}")
                print(f"  Descrição: {agent.get('description', 'N/A')}")
                print("-" * 20)
        else:
            print(f"Resposta: {agents}")
    else:
        print(f"❌ Erro ao listar agentes: {response.text}")

if __name__ == "__main__":
    listar_agentes()
    listar_times()