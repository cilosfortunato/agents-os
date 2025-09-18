#!/usr/bin/env python3
"""
Teste específico para o endpoint /v1/messages
"""

import requests
import json

def test_messages_endpoint():
    """Testa o endpoint /v1/messages com dados válidos"""
    
    base_url = "http://localhost:8002"
    headers = {
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
        "Content-Type": "application/json"
    }
    
    print("🔍 Testando endpoint /v1/messages...")
    
    # Primeiro, vamos buscar um agente válido
    try:
        agents_response = requests.get(f"{base_url}/v1/agents", headers=headers)
        agents_response.raise_for_status()
        agents = agents_response.json()
        
        print(f"🔍 Estrutura dos agentes: {json.dumps(agents, indent=2)}")
        
        if not agents:
            print("❌ Nenhum agente encontrado")
            return
            
        # Verificar se agents é uma lista ou dict
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
        
        # Agora vamos testar o endpoint /v1/messages
        message_data = {
            "mensagem": "Olá, como você está?",
            "agent_id": agent_id,
            "user_id": "test_user_123",
            "session_id": "test_session_456"
        }
        
        print(f"\n📤 Enviando mensagem: {json.dumps(message_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/v1/messages",
            headers=headers,
            json=message_data
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resposta recebida: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erro na resposta:")
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            try:
                error_detail = response.json()
                print(f"Detalhes: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Texto da resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_messages_endpoint()