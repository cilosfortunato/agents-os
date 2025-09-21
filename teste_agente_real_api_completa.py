#!/usr/bin/env python3
"""
Teste específico com o agente real da93fcc7-cf93-403e-aa99-9e295080d692
usando a API completa que conecta ao Supabase
"""

import requests
import json
import time
import uuid
from datetime import datetime
from supabase_service import SupabaseService

# Configurações
API_BASE_URL = "http://localhost:8000"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
AGENT_ID = "da93fcc7-cf93-403e-aa99-9e295080d692"

# Headers para requisições
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Instância do Supabase para verificações
supabase_service = SupabaseService()

def test_health_check():
    """Testa se a API está funcionando"""
    print("1. Testando health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health: {data}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return False

def verify_agent_exists():
    """Verifica se o agente existe no Supabase"""
    print(f"\n2. Verificando se agente {AGENT_ID} existe...")
    try:
        agent = supabase_service.get_agent(AGENT_ID)
        if agent:
            print(f"✅ Agente encontrado: {agent.get('name')}")
            print(f"   Modelo: {agent.get('model')}")
            print(f"   Provider: {agent.get('provider')}")
            return True
        else:
            print(f"❌ Agente {AGENT_ID} não encontrado")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar agente: {e}")
        return False

def test_chat_with_real_agent():
    """Testa chat com o agente real"""
    print(f"\n3. Testando chat com agente real {AGENT_ID}...")
    
    # Gera IDs únicos para o teste
    user_id = f"test-user-{int(time.time())}"
    session_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    
    # Payload no formato correto da API completa
    payload = {
        "mensagem": "Olá! Você pode me ajudar com informações sobre produtos?",
        "agent_id": AGENT_ID,
        "user_id": user_id,
        "session_id": session_id,
        "message_id": message_id,
        "cliente_id": "",
        "id_conta": "test-account-123",
        "debounce": 0  # Sem debounce para teste imediato
    }
    
    print(f"📤 Enviando mensagem:")
    print(f"   User ID: {user_id}")
    print(f"   Session ID: {session_id}")
    print(f"   Message: {payload['mensagem']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/messages",
            headers=headers,
            json=payload
        )
        
        print(f"📥 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida:")
            print(f"   Messages: {data.get('messages', [])}")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Agent Usage: {data.get('agent_usage', {})}")
            
            return {
                "success": True,
                "response": data,
                "user_id": user_id,
                "session_id": session_id,
                "message_id": message_id
            }
        else:
            print(f"❌ Erro na resposta: {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return {"success": False, "error": str(e)}

def verify_message_saved(user_id, session_id, message_id):
    """Verifica se a mensagem foi salva no Supabase"""
    print(f"\n4. Verificando se mensagem foi salva no Supabase...")
    
    try:
        # Busca mensagens por session_id
        from supabase import create_client
        import os
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        # Busca na tabela mensagens_ia
        result = supabase.table("mensagens_ia").select("*").eq("session_id", session_id).execute()
        
        if result.data:
            print(f"✅ Encontradas {len(result.data)} mensagens salvas:")
            for msg in result.data:
                print(f"   ID: {msg.get('id')}")
                print(f"   Agent ID: {msg.get('agent_id')}")
                print(f"   User ID: {msg.get('user_id')}")
                print(f"   Mensagem: {msg.get('mensagem_usuario')[:50]}...")
                print(f"   Resposta: {msg.get('resposta_agente')[:50]}...")
                print(f"   Data: {msg.get('created_at')}")
                print("   ---")
            return True
        else:
            print(f"❌ Nenhuma mensagem encontrada para session_id: {session_id}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar mensagens: {e}")
        return False

def verify_memory_saved(user_id, session_id):
    """Verifica se a memória foi salva"""
    print(f"\n5. Verificando memórias salvas...")
    
    try:
        # Verifica na tabela enriched_memories
        from supabase import create_client
        import os
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase = create_client(supabase_url, supabase_key)
        
        # Busca memórias por user_id
        result = supabase.table("enriched_memories").select("*").eq("user_id", user_id).execute()
        
        if result.data:
            print(f"✅ Encontradas {len(result.data)} memórias salvas:")
            for mem in result.data:
                print(f"   ID: {mem.get('id')}")
                print(f"   User ID: {mem.get('user_id')}")
                print(f"   Memory: {mem.get('memory')[:100]}...")
                print(f"   Data: {mem.get('created_at')}")
                print("   ---")
            return True
        else:
            print(f"❌ Nenhuma memória encontrada para user_id: {user_id}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar memórias: {e}")
        return False

def main():
    """Função principal do teste"""
    print("🎯 TESTE COMPLETO COM AGENTE REAL - API COMPLETA")
    print("=" * 70)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Agent ID: {AGENT_ID}")
    print(f"🌐 API URL: {API_BASE_URL}")
    
    # Executa os testes
    results = {
        "health_check": test_health_check(),
        "agent_exists": verify_agent_exists(),
        "chat_test": None,
        "message_saved": False,
        "memory_saved": False
    }
    
    if results["health_check"] and results["agent_exists"]:
        chat_result = test_chat_with_real_agent()
        results["chat_test"] = chat_result
        
        if chat_result and chat_result.get("success"):
            # Aguarda um pouco para garantir que os dados foram salvos
            print("\n⏳ Aguardando 3 segundos para verificar persistência...")
            time.sleep(3)
            
            results["message_saved"] = verify_message_saved(
                chat_result["user_id"], 
                chat_result["session_id"], 
                chat_result["message_id"]
            )
            
            results["memory_saved"] = verify_memory_saved(
                chat_result["user_id"], 
                chat_result["session_id"]
            )
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO DO TESTE COMPLETO")
    print("=" * 70)
    print(f"Health Check      | {'✅ PASSOU' if results['health_check'] else '❌ FALHOU'}")
    print(f"Agente Existe     | {'✅ PASSOU' if results['agent_exists'] else '❌ FALHOU'}")
    print(f"Chat Funcionou    | {'✅ PASSOU' if results['chat_test'] and results['chat_test'].get('success') else '❌ FALHOU'}")
    print(f"Mensagem Salva    | {'✅ PASSOU' if results['message_saved'] else '❌ FALHOU'}")
    print(f"Memória Salva     | {'✅ PASSOU' if results['memory_saved'] else '❌ FALHOU'}")
    print("-" * 70)
    
    # Verifica se tudo passou
    all_passed = all([
        results["health_check"],
        results["agent_exists"],
        results["chat_test"] and results["chat_test"].get("success"),
        results["message_saved"]
    ])
    
    if all_passed:
        print("🎉 TESTE COMPLETO: SUCESSO TOTAL!")
        print("✅ Agente real está funcionando perfeitamente")
        print("✅ Mensagens estão sendo salvas no Supabase")
        print("✅ Sistema completo operacional")
    else:
        print("⚠️  TESTE PARCIAL OU FALHOU")
        print("❓ Verifique os itens que falharam acima")
    
    print("\n🔍 Para investigar webhook, verifique os logs da API")

if __name__ == "__main__":
    main()