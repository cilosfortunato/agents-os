#!/usr/bin/env python3
"""
Teste para verificar se o erro do OpenAI foi corrigido com a atualização do Mem0
"""

import requests
import json
import time

def test_message_with_memory():
    """Testa envio de mensagem com memória para verificar se o erro foi corrigido"""
    
    url = "http://localhost:8002/v1/messages"
    headers = {
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
        "Content-Type": "application/json"
    }
    
    # Payload igual ao que causou o erro
    payload = [
        {
            "sessionId": "session_123",
            "agent_id": "da93fcc7-cf93-403e-aa99-9e295080d692",
            "mensagem": "boa noite, meu nome é cilos, tenho 41 anos, o que vcs fazem?",
            "debounce": "10000",
            "user_id": "8196859149@s.whatsapp.net"
        }
    ]
    
    print("🧪 Testando mensagem com memória após atualização do Mem0...")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"⏱️ Tempo de resposta: {elapsed:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Resposta JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Verifica se não há erro de OpenAI
                if "erro" not in str(data).lower() and "openai.chatcompletion" not in str(data).lower():
                    print("\n🎉 SUCESSO! O erro do OpenAI foi corrigido!")
                    return True
                else:
                    print("\n❌ Ainda há erro relacionado ao OpenAI")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido:")
                print(response.text[:500])
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}:")
            print(response.text[:500])
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ Timeout após {elapsed:.2f}s")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Erro após {elapsed:.2f}s: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Teste de Correção do Erro OpenAI no Mem0")
    print("=" * 50)
    
    success = test_message_with_memory()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TESTE PASSOU - Erro do OpenAI foi corrigido!")
    else:
        print("❌ TESTE FALHOU - Erro ainda persiste")