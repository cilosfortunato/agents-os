#!/usr/bin/env python3
"""
Teste de Debug da Memória - AgentOS
Verifica se a memória está sendo salva corretamente
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:7777"
USER_ID = "teste_memoria_user"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def print_response(action, response):
    """Imprime resposta formatada"""
    print(f"\n=== {action} ===")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None

def criar_agente(nome, role, instructions):
    """Cria um agente"""
    payload = {
        "name": nome,
        "role": role,
        "instructions": [instructions],  # Deve ser uma lista
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/agents", json=payload, headers=HEADERS)
    return print_response(f"Criar Agente: {nome}", response)

def criar_time(nome, descricao, agent_names):
    """Cria um time de agentes"""
    payload = {
        "name": nome,
        "description": descricao,
        "agent_names": agent_names,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams", json=payload, headers=HEADERS)
    return print_response(f"Criar Time: {nome}", response)

def executar_time(team_id, message):
    """Executa um time com uma mensagem"""
    payload = {
        "team_id": team_id,
        "message": message,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams/run", json=payload, headers=HEADERS)
    return print_response(f"Executar Time - Mensagem: {message[:50]}...", response)

def verificar_memoria(user_id):
    """Verifica memórias salvas"""
    response = requests.get(f"{BASE_URL}/memory/all", params={"user_id": user_id}, headers=HEADERS)
    return print_response(f"Verificar Memória para: {user_id}", response)

def main():
    print("🚀 TESTE DE DEBUG DA MEMÓRIA - AgentOS")
    print("=" * 50)
    
    # 1. Criar agentes
    print("\n📝 CRIANDO AGENTES...")
    agente1 = criar_agente(
        "Assistente Geral",
        "assistant", 
        "Você é um assistente útil e amigável que responde perguntas gerais."
    )
    
    agente2 = criar_agente(
        "Especialista Técnico",
        "specialist",
        "Você é um especialista técnico que fornece informações detalhadas sobre tecnologia."
    )
    
    # 2. Criar time
    print("\n👥 CRIANDO TIME...")
    time_response = criar_time(
        "Time de Suporte",
        "Time especializado em atendimento e suporte técnico",
        ["Assistente Geral", "Especialista Técnico"]
    )
    
    if not time_response:
        print("❌ Erro: Não foi possível criar o time")
        return
    
    # Listar times para obter o ID do time criado
    print("\n📋 LISTANDO TIMES PARA OBTER ID...")
    response = requests.get(f"{BASE_URL}/teams", params={"user_id": USER_ID}, headers=HEADERS)
    teams_data = print_response("Listar Times", response)
    
    if not teams_data or not teams_data.get('teams'):
        print("❌ Erro: Nenhum time encontrado")
        return
    
    # Pegar o último time criado (mais recente)
    team_id = teams_data['teams'][-1]['id']
    team_user_id = f"{USER_ID}_team_{team_id}"
    
    print(f"\n✅ Time criado com ID: {team_id}")
    print(f"✅ User ID da memória será: {team_user_id}")
    
    # 3. Executar algumas mensagens
    print("\n💬 EXECUTANDO MENSAGENS...")
    
    mensagens = [
        "Olá, qual é o seu nome?",
        "Você pode me ajudar com problemas técnicos?",
        "Qual é a diferença entre RAM e armazenamento?"
    ]
    
    for i, mensagem in enumerate(mensagens, 1):
        print(f"\n--- Mensagem {i} ---")
        executar_time(team_id, mensagem)
        time.sleep(1)  # Pequena pausa entre mensagens
    
    # 4. Verificar memórias
    print("\n🧠 VERIFICANDO MEMÓRIAS...")
    
    # Verifica memória do usuário original
    print("\n--- Memória do usuário original ---")
    verificar_memoria(USER_ID)
    
    # Verifica memória do time
    print("\n--- Memória do time ---")
    verificar_memoria(team_user_id)
    
    # 5. Executar mais uma mensagem para testar contexto
    print("\n🔄 TESTANDO CONTEXTO...")
    executar_time(team_id, "Você se lembra do que conversamos antes?")
    
    # 6. Verificar memórias novamente
    print("\n🧠 VERIFICANDO MEMÓRIAS FINAIS...")
    verificar_memoria(team_user_id)
    
    print("\n✅ TESTE DE DEBUG CONCLUÍDO!")

if __name__ == "__main__":
    main()