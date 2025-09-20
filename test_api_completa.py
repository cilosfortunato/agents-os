#!/usr/bin/env python3
"""
Teste da API Completa com mock do VertexAI
"""
import requests
import json
import time

def test_api_completa():
    """Testa a API completa com diferentes endpoints"""
    base_url = "http://localhost:80"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
    }
    
    print("=== Teste da API Completa ===")
    
    # Teste 1: Health Check
    print("\n--- Teste 1: Health Check ---")
    try:
        response = requests.get(f"{base_url}/v1/health", headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Health: {response.json()}")
        else:
            print(f"❌ Health falhou: {response.text}")
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
    
    # Teste 2: Endpoint de Mensagens (formato esperado)
    print("\n--- Teste 2: Endpoint de Mensagens ---")
    try:
        payload = [
            {
                "mensagem": "Qual é a garantia do meu produto?",
                "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
                "debounce": 15000,
                "session_id": "645d4334-8660-49b0-813b-872662cd2b7c",
                "message_id": "ef46e048-6c42-4f04-9262-2cae02a3d4d5",
                "cliente_id": "",
                "user_id": "116883357474955@lid",
                "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
            }
        ]
        
        response = requests.post(
            f"{base_url}/v1/messages", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Mensagens falhou: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste de mensagens: {e}")
    
    # Teste 3: Chat simples
    print("\n--- Teste 3: Chat Simples ---")
    try:
        payload = {
            "message": "Como ativar o modo noturno?",
            "user_id": "test_user_123",
            "session_id": "test_session_456"
        }
        
        response = requests.post(
            f"{base_url}/v1/chat", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Chat falhou: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste de chat: {e}")
    
    # Teste 4: Busca na base de conhecimento
    print("\n--- Teste 4: Knowledge Search ---")
    try:
        response = requests.get(
            f"{base_url}/v1/knowledge/search", 
            headers=headers,
            params={"query": "garantia produto", "limit": 3},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Knowledge: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Knowledge falhou: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste de knowledge: {e}")



if __name__ == "__main__":
    print("🚀 Iniciando testes da API...")
    time.sleep(2)  # Aguarda a API estar pronta
    test_api_completa()
    print("\n🏁 Testes concluídos!")