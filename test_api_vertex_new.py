"""
Teste da API com o novo cliente Vertex AI integrado
"""

import requests
import json
import time

def test_api_with_vertex_new():
    """Testa a API com o novo cliente Vertex AI"""
    print("=== Teste da API com Novo Cliente Vertex AI ===")
    
    base_url = "http://localhost:80"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
    }
    
    # Teste 1: Endpoint de chat com modelo Gemini
    print("\n1. Testando endpoint /v1/chat com modelo gemini-2.5-flash...")
    
    chat_payload = {
        "message": "Qual é a capital do Brasil?",
        "user_id": "test-user-123",
        "agent_name": "Especialista em Produtos",
        "session_id": "test-session-chat"
    }
    
    try:
        response = requests.post(f"{base_url}/v1/chat", headers=headers, json=chat_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta: {data.get('response', '')[:200]}...")
            print(f"Agent Usage: {data.get('agent_usage', {})}")
            
            # Verificar se o modelo está correto
            usage = data.get('agent_usage', {})
            if usage.get('model') == 'gemini-2.5-flash':
                print("✓ Modelo gemini-2.5-flash detectado corretamente")
            else:
                print(f"⚠ Modelo inesperado: {usage.get('model')}")
        else:
            print(f"Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return False
    
    # Teste 2: Endpoint de mensagens com modelo Gemini
    print("\n2. Testando endpoint /v1/messages com modelo gemini-2.5-flash...")
    
    messages_payload = [
        {
            "mensagem": "Conte uma curiosidade sobre o Brasil",
            "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
            "debounce": 5000,
            "session_id": "test-session-456",
            "message_id": "test-msg-789",
            "cliente_id": "",
            "user_id": "test-user-123",
            "id_conta": "test-account-999"
        }
    ]
    
    try:
        response = requests.post(f"{base_url}/v1/messages", headers=headers, json=messages_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Mensagem enviada com sucesso")
            print("Aguardando processamento do debounce...")
            time.sleep(6)  # Aguarda o debounce processar
        else:
            print(f"Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return False
    
    # Teste 3: Verificar se o agente está usando o modelo correto
    print("\n3. Verificando configuração do agente...")
    
    try:
        response = requests.get(f"{base_url}/v1/agents/1677dc47-20d0-442a-80a8-171f00d39d39", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            agent_data = response.json()
            model = agent_data.get('model', 'N/A')
            print(f"Modelo do agente: {model}")
            
            if 'gemini' in model.lower():
                print("✓ Agente configurado para usar modelo Gemini")
            else:
                print(f"⚠ Agente usando modelo: {model}")
        else:
            print(f"Erro ao buscar agente: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 4: Health check
    print("\n4. Testando health check...")
    
    try:
        response = requests.get(f"{base_url}/v1/health")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"Status da API: {health_data.get('status')}")
            print(f"Timestamp: {health_data.get('timestamp')}")
            print("✓ API funcionando corretamente")
        else:
            print(f"Erro no health check: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    print("\n=== Teste Concluído ===")
    return True

if __name__ == "__main__":
    success = test_api_with_vertex_new()
    if success:
        print("\n🎉 Integração do novo cliente Vertex AI funcionando!")
    else:
        print("\n❌ Há problemas na integração do novo cliente Vertex AI.")