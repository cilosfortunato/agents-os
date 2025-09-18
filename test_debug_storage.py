#!/usr/bin/env python3
"""
Teste de debug para verificar o storage de agentes customizados
"""

import requests
import json
import time

BASE_URL = "http://localhost:80"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

def fazer_requisicao(method, endpoint, dados=None):
    """Faz uma requisição para a API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=dados)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=dados)
        else:
            raise ValueError(f"Método {method} não suportado")
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro: {response.text}")
            return None
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def main():
    print("🔍 TESTE DE DEBUG DO STORAGE")
    print("=" * 50)
    
    # 1. Listar agentes antes da criação
    print("\n1️⃣ Listando agentes ANTES da criação...")
    agentes_antes = fazer_requisicao("GET", "/agents")
    if agentes_antes:
        print(f"Total antes: {agentes_antes.get('total', 0)}")
        print(f"Agentes padrão: {len(agentes_antes.get('default_agents', []))}")
        print(f"Agentes customizados: {len(agentes_antes.get('custom_agents', []))}")
    
    # 2. Criar agente
    print("\n2️⃣ Criando agente...")
    dados_agente = {
        "name": "Debug Test Agent",
        "role": "assistente de debug",
        "instructions": ["Você é um agente de teste para debug"],
        "user_id": "debug_user"
    }
    
    resultado_criacao = fazer_requisicao("POST", "/agents", dados_agente)
    if not resultado_criacao:
        print("❌ Falha na criação do agente")
        return
    
    agent_id = resultado_criacao.get("agent", {}).get("id")
    print(f"✅ Agente criado: {agent_id}")
    
    # 3. Aguardar um pouco
    print("\n3️⃣ Aguardando 3 segundos...")
    time.sleep(3)
    
    # 4. Listar agentes depois da criação
    print("\n4️⃣ Listando agentes DEPOIS da criação...")
    agentes_depois = fazer_requisicao("GET", "/agents")
    if agentes_depois:
        print(f"Total depois: {agentes_depois.get('total', 0)}")
        print(f"Agentes padrão: {len(agentes_depois.get('default_agents', []))}")
        print(f"Agentes customizados: {len(agentes_depois.get('custom_agents', []))}")
        
        # Verificar se o agente está na lista
        custom_agents = agentes_depois.get('custom_agents', [])
        agente_encontrado = False
        for agent in custom_agents:
            if agent.get('id') == agent_id:
                agente_encontrado = True
                print(f"✅ Agente encontrado na lista: {agent}")
                break
        
        if not agente_encontrado:
            print(f"❌ Agente {agent_id} NÃO encontrado na lista")
            print("📋 Agentes customizados encontrados:")
            for i, agent in enumerate(custom_agents):
                print(f"  {i+1}. ID: {agent.get('id')}, Nome: {agent.get('name')}")
    
    # 5. Tentar buscar o agente específico
    print(f"\n5️⃣ Buscando agente específico {agent_id}...")
    agente_especifico = fazer_requisicao("GET", f"/agents/{agent_id}")
    if agente_especifico:
        print(f"✅ Agente encontrado: {agente_especifico}")
    else:
        print(f"❌ Agente {agent_id} não encontrado")
    
    # 6. Tentar executar o agente
    print(f"\n6️⃣ Tentando executar agente Debug Test Agent...")
    dados_execucao = {
        "message": "Olá, você pode me ajudar?",
        "agent_name": "Debug Test Agent",
        "user_id": "test_user"
    }
    
    resultado_execucao = fazer_requisicao("POST", "/chat", dados_execucao)
    if resultado_execucao:
        print(f"✅ Execução bem-sucedida: {resultado_execucao}")
    else:
        print(f"❌ Falha na execução")

if __name__ == "__main__":
    main()