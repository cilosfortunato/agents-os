import requests
import json
import time

BASE_URL = "http://localhost:7777"
USER_ID = "teste_memoria_integrada"
HEADERS = {"Content-Type": "application/json"}

def print_response(title, response):
    """Imprime a resposta de forma formatada"""
    print(f"\n=== {title} ===")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None

def main():
    print("🚀 TESTE DE INTEGRAÇÃO DE MEMÓRIA COM TIMES")
    print("=" * 50)
    
    # 1. Criar agentes
    print("\n📝 CRIANDO AGENTES...")
    
    agente1_payload = {
        "name": "Assistente Memória",
        "role": "Assistente com memória contextual",
        "instructions": ["Você é um assistente que lembra de conversas anteriores e usa esse contexto para personalizar suas respostas."],
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/agents", json=agente1_payload, headers=HEADERS)
    agente1_data = print_response("Criar Agente 1", response)
    
    if not agente1_data:
        print("❌ Falha ao criar agente")
        return
    
    # 2. Criar time
    print("\n👥 CRIANDO TIME...")
    
    time_payload = {
        "name": "Time com Memória",
        "description": "Time que utiliza memória contextual",
        "agent_names": ["Assistente Memória"],
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams", json=time_payload, headers=HEADERS)
    time_response = print_response("Criar Time", response)
    
    if not time_response:
        print("❌ Erro: Não foi possível criar o time")
        return
    
    # Listar times para obter o ID
    print("\n📋 OBTENDO ID DO TIME...")
    response = requests.get(f"{BASE_URL}/teams", params={"user_id": USER_ID}, headers=HEADERS)
    teams_data = print_response("Listar Times", response)
    
    if not teams_data or not teams_data.get('teams'):
        print("❌ Erro: Nenhum time encontrado")
        return
    
    team_id = teams_data['teams'][-1]['id']
    team_user_id = f"{USER_ID}_team_{team_id}"
    print(f"\n🆔 Team ID: {team_id}")
    print(f"🆔 Team User ID: {team_user_id}")
    
    # 3. Primeira conversa - estabelecer contexto
    print("\n💬 PRIMEIRA CONVERSA - ESTABELECENDO CONTEXTO...")
    
    mensagem1 = "Olá! Meu nome é João e eu trabalho como desenvolvedor Python. Gosto muito de IA e machine learning."
    
    payload = {
        "team_id": team_id,
        "message": mensagem1,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams/run", json=payload, headers=HEADERS)
    resposta1 = print_response("Primeira Mensagem", response)
    
    time.sleep(2)  # Aguarda processamento da memória
    
    # 4. Segunda conversa - testando memória
    print("\n🧠 SEGUNDA CONVERSA - TESTANDO MEMÓRIA...")
    
    mensagem2 = "Você se lembra do meu nome e da minha profissão?"
    
    payload = {
        "team_id": team_id,
        "message": mensagem2,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams/run", json=payload, headers=HEADERS)
    resposta2 = print_response("Segunda Mensagem", response)
    
    time.sleep(2)  # Aguarda processamento da memória
    
    # 5. Terceira conversa - contexto mais específico
    print("\n🎯 TERCEIRA CONVERSA - CONTEXTO ESPECÍFICO...")
    
    mensagem3 = "Que linguagens de programação você recomendaria para alguém com meu perfil?"
    
    payload = {
        "team_id": team_id,
        "message": mensagem3,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams/run", json=payload, headers=HEADERS)
    resposta3 = print_response("Terceira Mensagem", response)
    
    # 6. Verificar memórias salvas
    print("\n🔍 VERIFICANDO MEMÓRIAS SALVAS...")
    
    response = requests.get(f"{BASE_URL}/memory/all", params={"user_id": team_user_id}, headers=HEADERS)
    memorias = print_response("Memórias do Time", response)
    
    # 7. Buscar memórias específicas
    print("\n🔎 BUSCANDO MEMÓRIAS ESPECÍFICAS...")
    
    search_params = {
        "query": "nome João desenvolvedor",
        "user_id": team_user_id
    }
    
    response = requests.get(f"{BASE_URL}/memory/search", params=search_params, headers=HEADERS)
    busca_memorias = print_response("Busca de Memórias", response)
    
    # 8. Relatório final
    print("\n📊 RELATÓRIO FINAL")
    print("=" * 30)
    
    if memorias and memorias.get('total', 0) > 0:
        print(f"✅ Memórias salvas: {memorias['total']}")
        print("✅ Sistema de memória funcionando")
    else:
        print("❌ Nenhuma memória encontrada")
    
    if resposta2 and 'João' in str(resposta2).lower():
        print("✅ Agente lembrou do nome")
    else:
        print("❌ Agente não lembrou do nome")
    
    if resposta2 and ('desenvolvedor' in str(resposta2).lower() or 'python' in str(resposta2).lower()):
        print("✅ Agente lembrou da profissão")
    else:
        print("❌ Agente não lembrou da profissão")
    
    print("\n🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()