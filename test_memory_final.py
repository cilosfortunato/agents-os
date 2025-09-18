#!/usr/bin/env python3
"""
Teste final do sistema de memória com dados reais
"""

import requests
import json
import time

def test_memory_with_real_data():
    """Testa o sistema de memória com dados reais existentes no banco"""
    print("🎯 TESTE FINAL DO SISTEMA DE MEMÓRIA")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    headers = {
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
        "Content-Type": "application/json"
    }
    
    # Usando o user_id que sabemos que tem dados
    user_id = "test_user_memory"
    session_id = "session_memory_test"
    agent_id = "test_agent_123"
    
    print(f"📋 Configuração do teste:")
    print(f"   User ID: {user_id}")
    print(f"   Session ID: {session_id}")
    print(f"   Agent ID: {agent_id}")
    print()
    
    try:
        # 1. Verificar memórias existentes
        print("🔍 VERIFICANDO MEMÓRIAS EXISTENTES")
        print("-" * 40)
        
        params = {
            "user_id": user_id,
            "query": "João",
            "limit": 3
        }
        
        response = requests.get(f"{base_url}/v1/memory/search", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Memórias encontradas sobre 'João': {data['total']}")
            for i, memory in enumerate(data['memories'], 1):
                print(f"   {i}. {memory['content'][:80]}...")
        print()
        
        # 2. Enviar nova mensagem que deveria usar a memória
        print("📤 ENVIANDO NOVA MENSAGEM COM CONTEXTO")
        print("-" * 40)
        
        message_data = {
            "user_id": user_id,
            "session_id": session_id,
            "agent_id": agent_id,
            "mensagem": "Você se lembra do meu nome e do que eu gosto de comer?",
            "use_memory": True
        }
        
        response = requests.post(f"{base_url}/v1/messages", json=message_data, headers=headers)
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # A resposta vem no campo 'messages' como uma lista
            messages = data.get('messages', [])
            response_text = messages[0] if messages else ''
            print(f"🤖 Resposta do agente:")
            print(f"   {response_text}")
            print()
            
            # Análise da resposta
            print("📊 ANÁLISE DA RESPOSTA:")
            print("-" * 30)
            lembrou_nome = "joão" in response_text.lower()
            lembrou_comida = "pizza" in response_text.lower()
            
            print(f"  🏷️  Lembrou do nome (João): {'✅' if lembrou_nome else '❌'}")
            print(f"  🍕 Lembrou da comida (pizza): {'✅' if lembrou_comida else '❌'}")
            
            if lembrou_nome and lembrou_comida:
                print("🎉 SUCESSO: O sistema de memória está funcionando!")
            elif lembrou_nome or lembrou_comida:
                print("⚠️  PARCIAL: O sistema lembrou parcialmente")
            else:
                print("❌ FALHA: O sistema não usou a memória")
        else:
            print(f"❌ Erro na requisição: {response.text}")
        
        print()
        
        # 3. Verificar se a nova interação foi salva
        print("💾 VERIFICANDO SALVAMENTO DA NOVA INTERAÇÃO")
        print("-" * 40)
        
        time.sleep(2)  # Aguarda salvamento
        
        params = {
            "user_id": user_id,
            "query": "lembra",
            "limit": 2
        }
        
        response = requests.get(f"{base_url}/v1/memory/search", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Novas memórias encontradas: {data['total']}")
            for i, memory in enumerate(data['memories'], 1):
                print(f"   {i}. {memory['content'][:80]}...")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_with_real_data()