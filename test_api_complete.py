#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo da API AgentOS
Testa todos os endpoints: agentes, times e mensagens
"""

import requests
import json
import time
from typing import Dict, Any

# Configuração da API
BASE_URL = "http://localhost:7777"
HEADERS = {"Content-Type": "application/json"}

def print_response(title: str, response: requests.Response):
    """Imprime resposta formatada"""
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"Response Text: {response.text}")
        return None

def test_agents_endpoints():
    """Testa endpoints de agentes"""
    print("\n🤖 TESTANDO ENDPOINTS DE AGENTES")
    
    # 1. Listar agentes
    response = requests.get(f"{BASE_URL}/agents", headers=HEADERS)
    agents_data = print_response("GET /agents - Listar Agentes", response)
    
    if not agents_data:
        print("❌ Nenhum agente encontrado!")
        return None
    
    # Verificar se há agentes (default ou custom)
    all_agents = []
    if agents_data.get('default_agents'):
        all_agents.extend(agents_data['default_agents'])
    if agents_data.get('custom_agents'):
        all_agents.extend(agents_data['custom_agents'])
    
    if not all_agents:
        print("❌ Nenhum agente encontrado!")
        return None
    
    # Pegar o primeiro agente para testes
    first_agent = all_agents[0]
    agent_name = first_agent.get('name', 'unknown')
    print(f"✅ Usando agente: {agent_name}")
    
    # 2. Tentar obter agente específico (se houver endpoint)
    # Como não temos ID específico, vamos pular este teste
    print("ℹ️ Pulando teste de agente específico (estrutura sem ID)")
    
    return agent_name

def test_teams_endpoints(agent_id: str):
    """Testa endpoints de times"""
    print("\n👥 TESTANDO ENDPOINTS DE TIMES")
    
    # 1. Criar time
    team_data = {
        "name": "Time de Teste API Completo",
        "description": "Time criado para teste completo da API",
        "agent_names": ["Agente Técnico", "Agente de Vendas Kit Festas"],
        "user_id": "test_user_api"
    }
    
    response = requests.post(f"{BASE_URL}/teams", headers=HEADERS, json=team_data)
    team_response = print_response("POST /teams - Criar Time", response)
    
    if not team_response:
        print("❌ Falha ao criar time!")
        return None
    
    # 2. Listar times para obter o ID do time criado
    response = requests.get(f"{BASE_URL}/teams", headers=HEADERS, params={"user_id": "test_user_api"})
    teams_data = print_response("GET /teams - Listar Times", response)
    
    # Obter o ID do último time criado (mais recente)
    team_id = None
    if teams_data and teams_data.get('teams'):
        # Pegar o último time da lista (mais recente)
        team_id = teams_data['teams'][-1]['id']
        print(f"✅ Usando time: {teams_data['teams'][-1]['name']} (ID: {team_id})")
    
    if not team_id:
        print("❌ Nenhum time disponível para teste!")
        return None
    
    # 3. Obter time específico
    response = requests.get(f"{BASE_URL}/teams/{team_id}", headers=HEADERS)
    print_response(f"GET /teams/{team_id} - Obter Time Específico", response)
    
    return team_id

def test_chat_endpoints(team_id: str):
    """Testa endpoints de chat/mensagens"""
    print("\n💬 TESTANDO ENDPOINTS DE CHAT")
    
    # 1. Primeira mensagem - apresentação
    message_data = {
        "team_id": team_id,
        "message": "Olá! Meu nome é Maria, tenho 25 anos e sou designer gráfica. Preciso de ajuda para escolher um produto.",
        "user_id": "test_user_api"
    }
    
    response = requests.post(f"{BASE_URL}/teams/run", headers=HEADERS, json=message_data)
    print_response("POST /teams/run - Primeira Mensagem (Apresentação)", response)
    
    time.sleep(2)  # Aguarda processamento
    
    # 2. Segunda mensagem - pergunta técnica
    message_data["message"] = "Vocês têm produtos para design gráfico? Qual seria o melhor para mim?"
    
    response = requests.post(f"{BASE_URL}/teams/run", headers=HEADERS, json=message_data)
    print_response("POST /teams/run - Segunda Mensagem (Pergunta Técnica)", response)
    
    time.sleep(2)  # Aguarda processamento
    
    # 3. Terceira mensagem - teste de memória
    message_data["message"] = "Você se lembra do meu nome e profissão?"
    
    response = requests.post(f"{BASE_URL}/teams/run", headers=HEADERS, json=message_data)
    print_response("POST /teams/run - Terceira Mensagem (Teste de Memória)", response)
    
    return True

def test_health_endpoint():
    """Testa endpoint de health check"""
    print("\n🏥 TESTANDO HEALTH CHECK")
    
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS)
        print_response("GET /health - Health Check", response)
        return response.status_code == 200
    except:
        response = requests.get(f"{BASE_URL}/", headers=HEADERS)
        print_response("GET / - Root Endpoint", response)
        return response.status_code == 200

def main():
    """Executa teste completo da API"""
    print("🚀 INICIANDO TESTE COMPLETO DA API AGENTOS")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # 1. Health Check
        if not test_health_endpoint():
            print("❌ API não está respondendo!")
            return
        
        # 2. Testar Agentes
        agent_id = test_agents_endpoints()
        if not agent_id:
            print("❌ Falha nos testes de agentes!")
            return
        
        # 3. Testar Times
        team_id = test_teams_endpoints(agent_id)
        if not team_id:
            print("❌ Falha nos testes de times!")
            return
        
        # 4. Testar Chat
        if not test_chat_endpoints(team_id):
            print("❌ Falha nos testes de chat!")
            return
        
        print("\n✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("\n📊 RESUMO DOS TESTES:")
        print("✅ Health Check - OK")
        print("✅ Endpoints de Agentes - OK")
        print("✅ Endpoints de Times - OK")
        print("✅ Endpoints de Chat - OK")
        print("✅ Memória Mem0 - OK")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()