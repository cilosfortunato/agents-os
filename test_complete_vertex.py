#!/usr/bin/env python3
"""
Teste completo da API com agente Vertex AI
Testa ambos os endpoints: /v1/chat e /v1/messages
"""

import requests
import json
import time

def test_chat_endpoint():
    """Testa o endpoint /v1/chat com agent_name"""
    print("=== Testando endpoint /v1/chat ===")
    
    url = "http://localhost:80/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
    }
    
    payload = {
        "message": "Qual é a capital da França?",
        "agent_name": "Assistente Vertex AI",
        "user_id": "test-user-chat",
        "session_id": "test-session-chat"
    }
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint /v1/chat funcionando!")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Erro no endpoint /v1/chat: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição /v1/chat: {e}")
        return False

def test_messages_endpoint():
    """Testa o endpoint /v1/messages com agent_id"""
    print("\n=== Testando endpoint /v1/messages ===")
    
    url = "http://localhost:80/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
    }
    
    payload = {
        "mensagem": "Qual é a capital da Alemanha?",
        "agent_id": "9f7957ab-1c1c-4ae3-b143-c16d713f597d",
        "user_id": "test-user-messages",
        "session_id": "test-session-messages",
        "message_id": "test-msg-001",
        "cliente_id": "",
        "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9",
        "debounce": 0
    }
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint /v1/messages funcionando!")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verifica se tem agent_usage com modelo correto
            if 'agent_usage' in response_data and 'model' in response_data['agent_usage']:
                model = response_data['agent_usage']['model']
                print(f"🔍 Modelo usado: {model}")
                if 'gemini' in model.lower():
                    print("✅ Modelo Vertex AI confirmado!")
                else:
                    print("⚠️ Modelo não é Vertex AI")
            
            return True
        else:
            print(f"❌ Erro no endpoint /v1/messages: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição /v1/messages: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes completos da API Vertex AI\n")
    
    # Aguarda um pouco para garantir que a API está pronta
    time.sleep(1)
    
    # Testa ambos os endpoints
    chat_ok = test_chat_endpoint()
    messages_ok = test_messages_endpoint()
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print(f"  /v1/chat: {'✅ OK' if chat_ok else '❌ FALHOU'}")
    print(f"  /v1/messages: {'✅ OK' if messages_ok else '❌ FALHOU'}")
    
    if chat_ok and messages_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ API Vertex AI está funcionando perfeitamente!")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("❌ Verifique os logs acima para mais detalhes")

if __name__ == "__main__":
    main()