#!/usr/bin/env python3
"""
Script de teste para a API Completa com Memórias Enriquecidas
"""

import requests
import json

def test_chat_endpoint():
    """Testa o endpoint de chat"""
    url = "http://localhost:8000/v1/chat"
    
    payload = [{
        "mensagem": "Olá, como você está?",
        "user_id": "test-user-123",
        "session_id": "test-session-456",
        "agent_id": "test-agent-789",
        "message_id": "test-msg-001",
        "id_conta": "test-account-001"
    }]
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testando endpoint de chat...")
        print(f"📤 Enviando: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📥 Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Teste do chat passou!")
        else:
            print("❌ Teste do chat falhou!")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def test_memory_endpoints():
    """Testa os endpoints de memória"""
    base_url = "http://localhost:8000"
    user_id = "test-user-123"
    
    # Teste de listagem de memórias
    try:
        print("\n🧪 Testando endpoint de listagem de memórias...")
        url = f"{base_url}/v1/memory/list/{user_id}"
        response = requests.get(url)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📥 Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Teste de listagem de memórias passou!")
        else:
            print("❌ Teste de listagem de memórias falhou!")
            
    except Exception as e:
        print(f"❌ Erro no teste de memórias: {e}")

def test_health_endpoint():
    """Testa o endpoint de saúde"""
    try:
        print("\n🧪 Testando endpoint de saúde...")
        url = "http://localhost:8000/health"
        response = requests.get(url)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📥 Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Teste de saúde passou!")
        else:
            print("❌ Teste de saúde falhou!")
            
    except Exception as e:
        print(f"❌ Erro no teste de saúde: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes da API...")
    
    # Testa endpoint de saúde primeiro
    test_health_endpoint()
    
    # Testa endpoint de chat
    test_chat_endpoint()
    
    # Testa endpoints de memória
    test_memory_endpoints()
    
    print("\n🏁 Testes concluídos!")