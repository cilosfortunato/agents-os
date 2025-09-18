#!/usr/bin/env python3
"""
Teste para verificar se a memória está funcionando corretamente
"""

import requests
import json
import time

def test_memory_functionality():
    """Testa se o sistema lembra de conversas anteriores"""
    
    base_url = "http://localhost:8002"
    headers = {
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
        "Content-Type": "application/json"
    }
    
    print("🧠 Testando funcionalidade de memória...")
    
    # Buscar agente
    try:
        agents_response = requests.get(f"{base_url}/v1/agents", headers=headers)
        agents_response.raise_for_status()
        agents = agents_response.json()
        
        agent_id = agents["agents"][0]["id"]
        agent_name = agents["agents"][0]["name"]
        print(f"✅ Usando agente: {agent_name}")
        
        # Primeira mensagem - estabelecer contexto
        print("\n📤 Primeira mensagem - estabelecendo contexto...")
        message1 = {
            "mensagem": "Meu nome é João e eu gosto de pizza",
            "agent_id": agent_id,
            "user_id": "test_user_memory",
            "session_id": "test_session_memory"
        }
        
        response1 = requests.post(f"{base_url}/v1/messages", headers=headers, json=message1)
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Resposta 1: {result1['messages'][0]}")
        else:
            print(f"❌ Erro na primeira mensagem: {response1.status_code}")
            return
            
        # Aguardar um pouco para garantir que a memória seja salva
        time.sleep(2)
        
        # Segunda mensagem - testar se lembra do contexto
        print("\n📤 Segunda mensagem - testando memória...")
        message2 = {
            "mensagem": "Qual é o meu nome e o que eu gosto de comer?",
            "agent_id": agent_id,
            "user_id": "test_user_memory",
            "session_id": "test_session_memory"
        }
        
        response2 = requests.post(f"{base_url}/v1/messages", headers=headers, json=message2)
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Resposta 2: {result2['messages'][0]}")
            
            # Verificar se a resposta contém as informações da primeira mensagem
            resposta = result2['messages'][0].lower()
            if "joão" in resposta and "pizza" in resposta:
                print("🎉 SUCESSO! O sistema lembrou do contexto anterior!")
            else:
                print("⚠️  ATENÇÃO: O sistema não parece ter lembrado do contexto anterior")
                print(f"   Procurando por 'joão' e 'pizza' na resposta: {resposta}")
        else:
            print(f"❌ Erro na segunda mensagem: {response2.status_code}")
            
        # Terceira mensagem - testar memória mais específica
        print("\n📤 Terceira mensagem - teste específico...")
        message3 = {
            "mensagem": "Você se lembra de mim?",
            "agent_id": agent_id,
            "user_id": "test_user_memory",
            "session_id": "test_session_memory"
        }
        
        response3 = requests.post(f"{base_url}/v1/messages", headers=headers, json=message3)
        if response3.status_code == 200:
            result3 = response3.json()
            print(f"✅ Resposta 3: {result3['messages'][0]}")
        else:
            print(f"❌ Erro na terceira mensagem: {response3.status_code}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_functionality()