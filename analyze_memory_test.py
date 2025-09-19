#!/usr/bin/env python3
"""
Analisa as respostas do teste de memória
Busca por user_id específico nos logs do webhook
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:80"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def test_memory_directly():
    """Testa a memória diretamente com perguntas específicas"""
    print("=" * 60)
    print("TESTE DIRETO DE MEMÓRIA")
    print("=" * 60)
    
    # Busca um agente
    try:
        response = requests.get(f"{BASE_URL}/v1/agents", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                agent_id = data[0]["id"]
            elif isinstance(data, dict) and "agents" in data and len(data["agents"]) > 0:
                agent_id = data["agents"][0]["id"]
            else:
                print("❌ Nenhum agente encontrado!")
                return
        else:
            print(f"❌ Erro ao buscar agentes: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    print(f"✅ Agente encontrado: {agent_id}")
    
    # Teste simples de memória
    user_id = "memory_test_direct"
    session_id = "session_direct_123"
    
    messages = [
        "Meu nome é Pedro e tenho 28 anos",
        "Qual é o meu nome?",
        "Quantos anos eu tenho?",
        "Faça um resumo do que sabe sobre mim"
    ]
    
    for i, message in enumerate(messages, 1):
        payload = {
            "mensagem": message,
            "agent_id": agent_id,
            "user_id": user_id,
            "session_id": session_id,
            "debounce": 3000,
            "message_id": f"test_msg_{i}",
            "cliente_id": "test_client",
            "id_conta": "test_account"
        }
        
        try:
            print(f"\n📤 Enviando: {message}")
            response = requests.post(f"{BASE_URL}/v1/messages", headers=HEADERS, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                # Aguarda um pouco para ver a resposta
                time.sleep(5)
            else:
                print(f"❌ Erro: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao enviar: {e}")
        
        time.sleep(2)  # Pausa entre mensagens

def test_memory_search():
    """Testa a busca de memória diretamente"""
    print("\n" + "=" * 60)
    print("TESTE DE BUSCA DE MEMÓRIA")
    print("=" * 60)
    
    try:
        # Testa o endpoint de busca de memória
        response = requests.get(
            f"{BASE_URL}/v1/memory/search",
            headers=HEADERS,
            params={
                "user_id": "memory_test_user_1758282969",
                "query": "nome idade",
                "limit": 5
            },
            timeout=10
        )
        
        print(f"Status da busca: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Memórias encontradas:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro na busca: {e}")

def check_agent_config():
    """Verifica a configuração do agente"""
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DE CONFIGURAÇÃO DO AGENTE")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/v1/agents", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("Agentes disponíveis:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    print("🔍 ANÁLISE COMPLETA DE MEMÓRIA")
    print("=" * 60)
    
    # 1. Verifica configuração dos agentes
    check_agent_config()
    
    # 2. Testa busca de memória
    test_memory_search()
    
    # 3. Teste direto de memória
    test_memory_directly()
    
    print("\n" + "=" * 60)
    print("ANÁLISE CONCLUÍDA!")
    print("=" * 60)