#!/usr/bin/env python3
"""
Teste simples do endpoint /v1/messages
"""

import requests
import json

def test_messages_endpoint():
    """Testa o endpoint /v1/messages de forma simples"""
    print("📤 TESTE SIMPLES DO ENDPOINT /v1/messages")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    headers = {
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
        "Content-Type": "application/json"
    }
    
    # Dados da mensagem
    message_data = {
        "user_id": "test_user_memory",
        "session_id": "session_test_simple",
        "agent_id": "test_agent_123",
        "mensagem": "Olá, como você está?"
    }
    
    try:
        print(f"📋 Enviando mensagem: {message_data['mensagem']}")
        print(f"👤 User ID: {message_data['user_id']}")
        print(f"🔧 Agent ID: {message_data['agent_id']}")
        print()
        
        response = requests.post(f"{base_url}/v1/messages", json=message_data, headers=headers)
        
        print(f"📊 Status da resposta: {response.status_code}")
        print(f"📄 Headers da resposta: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Resposta JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Verificar se há resposta
                response_text = data.get('response', '')
                if response_text:
                    print(f"\n🤖 Resposta do agente: {response_text}")
                else:
                    print("\n⚠️  Resposta vazia do agente")
                    
            except json.JSONDecodeError:
                print("❌ Erro ao decodificar JSON")
                print(f"📄 Resposta raw: {response.text}")
        else:
            print(f"❌ Erro na requisição: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_messages_endpoint()