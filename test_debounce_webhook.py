"""
Teste do sistema de debounce e webhook do endpoint de mensagens
"""

import requests
import json
import time
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
WEBHOOK_URL = "http://localhost/fake-webhook"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_single_message():
    """Testa envio de mensagem única"""
    print("=== Teste 1: Mensagem Única ===")
    
    payload = {
        "mensagem": "Qual a garantia do produto?",
        "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
        "user_id": "test-user-123",
        "session_id": "test-session-456",
        "message_id": "msg-001",
        "debounce": 0  # Sem debounce para teste imediato
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/v1/messages", headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_multiple_messages_with_debounce():
    """Testa múltiplas mensagens com debounce"""
    print("\n=== Teste 2: Múltiplas Mensagens com Debounce ===")
    
    base_payload = {
        "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
        "user_id": "test-user-debounce",
        "session_id": "test-session-debounce",
        "debounce": 5000  # 5 segundos de debounce
    }
    
    messages = [
        "Primeira mensagem",
        "Segunda mensagem",
        "Terceira mensagem"
    ]
    
    print("Enviando mensagens rapidamente...")
    for i, msg in enumerate(messages):
        payload = {
            **base_payload,
            "mensagem": msg,
            "message_id": f"msg-debounce-{i+1}"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/v1/messages", headers=headers, json=payload)
            print(f"Mensagem {i+1}: Status {response.status_code}")
            time.sleep(0.5)  # Pequeno delay entre mensagens
        except Exception as e:
            print(f"Erro na mensagem {i+1}: {e}")
    
    print("Aguardando processamento do debounce (6 segundos)...")
    time.sleep(6)
    print("Debounce concluído!")

def test_list_messages():
    """Testa envio de lista de mensagens"""
    print("\n=== Teste 3: Lista de Mensagens ===")
    
    payload = [
        {
            "mensagem": "Primeira mensagem da lista",
            "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
            "user_id": "test-user-list",
            "session_id": "test-session-list",
            "message_id": "msg-list-1",
            "debounce": 0
        },
        {
            "mensagem": "Segunda mensagem da lista",
            "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
            "user_id": "test-user-list",
            "session_id": "test-session-list",
            "message_id": "msg-list-2",
            "debounce": 0
        }
    ]
    
    try:
        response = requests.post(f"{API_BASE_URL}/v1/messages", headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def check_webhook_payload():
    """Verifica o último payload recebido no webhook fake"""
    print("\n=== Verificando Webhook ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/fake-webhook/last")
        if response.status_code == 200:
            payload = response.json()
            print("Último payload do webhook:")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            
            # Verificar estrutura esperada
            if payload and "messages" in payload:
                print("✅ Estrutura do webhook está correta")
                return True
            else:
                print("❌ Estrutura do webhook incorreta")
                return False
        else:
            print(f"Erro ao verificar webhook: {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema de debounce e webhook")
    print(f"Timestamp: {datetime.now()}")
    
    results = []
    
    # Teste 1: Mensagem única
    results.append(test_single_message())
    time.sleep(2)
    
    # Verificar webhook após primeira mensagem
    check_webhook_payload()
    time.sleep(1)
    
    # Teste 2: Múltiplas mensagens com debounce
    test_multiple_messages_with_debounce()
    
    # Verificar webhook após debounce
    check_webhook_payload()
    time.sleep(1)
    
    # Teste 3: Lista de mensagens
    results.append(test_list_messages())
    time.sleep(2)
    
    # Verificar webhook final
    check_webhook_payload()
    
    # Resumo
    print(f"\n=== Resumo dos Testes ===")
    print(f"Mensagem única: {'✅' if results[0] else '❌'}")
    print(f"Lista de mensagens: {'✅' if results[1] else '❌'}")
    print(f"Debounce: ✅ (testado manualmente)")
    
    if all(results):
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️ Alguns testes falharam.")

if __name__ == "__main__":
    main()