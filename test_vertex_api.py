#!/usr/bin/env python3
"""
Testa a API com o agente Vertex AI
"""

import requests
import json

def test_vertex_api():
    """Testa a API com o agente configurado para Vertex AI"""
    
    # URL da API local
    url = "http://localhost:80/v1/chat"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
    }
    
    # Payload com o nome do agente Vertex AI
    payload = {
        "message": "Qual é a capital do Brasil?",
        "agent_name": "Assistente Vertex AI",
        "user_id": "test-user-vertex",
        "session_id": "test-session-vertex"
    }
    
    print("=== Testando API com Agente Vertex AI ===")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Faz a requisição
        print("\nEnviando requisição...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Sucesso!")
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Verifica se o modelo está correto no agent_usage
            if "agent_usage" in result and "model" in result["agent_usage"]:
                model = result["agent_usage"]["model"]
                print(f"\n🔍 Modelo usado: {model}")
                if "gemini" in model.lower():
                    print("✅ Vertex AI funcionando corretamente!")
                else:
                    print("⚠️ Modelo não é Vertex AI")
            
        else:
            print(f"\n❌ Erro na requisição")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - verifique se a API está rodando")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_vertex_api()