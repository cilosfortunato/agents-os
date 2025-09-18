#!/usr/bin/env python3
"""
Teste de múltiplas mensagens com debounce para verificar agrupamento e memória
"""

import requests
import json
import time
import uuid

def test_debounce_and_memory():
    """Testa múltiplas mensagens dentro da janela de debounce"""
    
    base_url = "http://localhost:80"
    headers = {
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
        "Content-Type": "application/json"
    }
    
    # IDs únicos para esta sessão de teste
    session_id = str(uuid.uuid4())
    user_id = "test_user_debounce_123"
    
    print("🧪 Testando debounce e memória...")
    print(f"Session ID: {session_id}")
    print(f"User ID: {user_id}")
    
    # Primeiro, vamos buscar um agente válido
    try:
        agents_response = requests.get(f"{base_url}/v1/agents", headers=headers)
        agents_response.raise_for_status()
        agents = agents_response.json()
        
        if not agents:
            print("❌ Nenhum agente encontrado")
            return
            
        # Verificar estrutura dos agentes
        if isinstance(agents, list) and len(agents) > 0:
            agent_id = agents[0]["id"]
            agent_name = agents[0]["name"]
        elif isinstance(agents, dict) and "agents" in agents:
            agent_id = agents["agents"][0]["id"]
            agent_name = agents["agents"][0]["name"]
        else:
            print(f"❌ Estrutura de agentes não reconhecida: {type(agents)}")
            return
            
        print(f"✅ Usando agente: {agent_name} (ID: {agent_id})")
        
        # Teste 1: Primeira mensagem com debounce de 10 segundos
        print("\n📤 Enviando primeira mensagem...")
        message1 = {
            "mensagem": "Olá! Meu nome é João e tenho 30 anos.",
            "agent_id": agent_id,
            "user_id": user_id,
            "session_id": session_id,
            "debounce": 10000,  # 10 segundos
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "id_conta": "test_account_123"
        }
        
        response1 = requests.post(f"{base_url}/v1/messages", headers=headers, json=message1)
        print(f"📥 Status: {response1.status_code}")
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Resposta: {result1['messages'][0]}")
        else:
            print(f"❌ Erro: {response1.text}")
            return
        
        # Aguardar 2 segundos e enviar segunda mensagem (dentro da janela)
        print("\n⏱️ Aguardando 2 segundos...")
        time.sleep(2)
        
        print("📤 Enviando segunda mensagem (dentro da janela de debounce)...")
        message2 = {
            "mensagem": "Trabalho como engenheiro de software e gosto de tecnologia.",
            "agent_id": agent_id,
            "user_id": user_id,
            "session_id": session_id,
            "debounce": 10000,  # 10 segundos
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "id_conta": "test_account_123"
        }
        
        response2 = requests.post(f"{base_url}/v1/messages", headers=headers, json=message2)
        print(f"📥 Status: {response2.status_code}")
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Resposta: {result2['messages'][0]}")
        else:
            print(f"❌ Erro: {response2.text}")
            return
        
        # Aguardar 3 segundos e enviar terceira mensagem (ainda dentro da janela)
        print("\n⏱️ Aguardando 3 segundos...")
        time.sleep(3)
        
        print("📤 Enviando terceira mensagem (ainda dentro da janela)...")
        message3 = {
            "mensagem": "Qual é o horário de funcionamento da clínica?",
            "agent_id": agent_id,
            "user_id": user_id,
            "session_id": session_id,
            "debounce": 10000,  # 10 segundos
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "id_conta": "test_account_123"
        }
        
        response3 = requests.post(f"{base_url}/v1/messages", headers=headers, json=message3)
        print(f"📥 Status: {response3.status_code}")
        if response3.status_code == 200:
            result3 = response3.json()
            print(f"✅ Resposta: {result3['messages'][0]}")
        else:
            print(f"❌ Erro: {response3.text}")
            return
        
        print("\n⏳ Aguardando processamento do debounce (12 segundos)...")
        time.sleep(12)
        
        # Teste de memória: nova mensagem após o debounce
        print("\n📤 Enviando mensagem para testar memória...")
        message4 = {
            "mensagem": "Você lembra qual é meu nome e minha profissão?",
            "agent_id": agent_id,
            "user_id": user_id,
            "session_id": session_id,
            "debounce": 0,  # Sem debounce para resposta imediata
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "id_conta": "test_account_123"
        }
        
        response4 = requests.post(f"{base_url}/v1/messages", headers=headers, json=message4)
        print(f"📥 Status: {response4.status_code}")
        if response4.status_code == 200:
            result4 = response4.json()
            print(f"✅ Resposta: {result4['messages'][0]}")
        else:
            print(f"❌ Erro: {response4.text}")
        
        print("\n⏳ Aguardando processamento da mensagem de memória (3 segundos)...")
        time.sleep(3)
        
        print("\n🎉 Teste concluído! Verifique os logs do webhook para ver as respostas agrupadas.")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debounce_and_memory()