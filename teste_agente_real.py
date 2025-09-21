#!/usr/bin/env python3
"""
Teste específico com o agente real da93fcc7-cf93-403e-aa99-9e295080d692
Simula exatamente a estrutura de input/output esperada
"""

import requests
import json
import uuid
from datetime import datetime

# Configurações
API_URL = "http://localhost:8000"
AGENT_ID = "da93fcc7-cf93-403e-aa99-9e295080d692"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

def criar_payload_real():
    """Cria payload exatamente como especificado nas instruções"""
    return [{
        "mensagem": "Boa noite! Gostaria de saber sobre os tratamentos disponíveis na clínica.",
        "agent_id": AGENT_ID,
        "debounce": 15000,
        "session_id": str(uuid.uuid4()),
        "message_id": str(uuid.uuid4()),
        "cliente_id": "",
        "user_id": "teste_real@bellaPele",
        "id_conta": str(uuid.uuid4())
    }]

def testar_agente_real():
    """Testa o agente real com payload correto"""
    print("🧪 TESTE COM AGENTE REAL")
    print("=" * 50)
    print(f"🤖 Agent ID: {AGENT_ID}")
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Criar payload
    payload = criar_payload_real()
    print(f"\n📤 Payload enviado:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        print(f"\n🚀 Enviando requisição para {API_URL}/chat...")
        response = requests.post(
            f"{API_URL}/chat",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RESPOSTA RECEBIDA:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Verificar estrutura esperada
            print(f"\n🔍 VERIFICAÇÃO DA ESTRUTURA:")
            expected_fields = ["messages", "transferir", "session_id", "user_id", "agent_id", "custom", "agent_usage"]
            
            for field in expected_fields:
                if field in result:
                    print(f"   ✅ {field}: {type(result[field])}")
                else:
                    print(f"   ❌ {field}: AUSENTE")
            
            # Verificar agent_usage
            if "agent_usage" in result:
                usage = result["agent_usage"]
                print(f"\n📈 USAGE DETAILS:")
                print(f"   Input Tokens: {usage.get('input_tokens')}")
                print(f"   Output Tokens: {usage.get('output_tokens')}")
                print(f"   Model: {usage.get('model')}")
            
            return result
            
        else:
            print(f"❌ ERRO: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERRO NA REQUISIÇÃO: {e}")
        return None

def verificar_mensagem_salva(session_id, user_id):
    """Verifica se a mensagem foi salva no Supabase"""
    print(f"\n🔍 VERIFICANDO MENSAGEM SALVA NO SUPABASE")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Buscar mensagem por session_id e user_id
        url = f"{SUPABASE_URL}/rest/v1/mensagens_ia?agent_id=eq.{AGENT_ID}&user_id=eq.{user_id}&order=created_at.desc&limit=1"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            mensagens = response.json()
            if mensagens:
                msg = mensagens[0]
                print("✅ MENSAGEM ENCONTRADA NO SUPABASE:")
                print(f"   ID: {msg.get('id')}")
                print(f"   Agent ID: {msg.get('agent_id')}")
                print(f"   User ID: {msg.get('user_id')}")
                print(f"   Session ID: {msg.get('session_id')}")
                print(f"   User Message: {msg.get('user_message')}")
                print(f"   Agent Response: {msg.get('agent_response', '')[:100]}...")
                print(f"   Criada em: {msg.get('created_at')}")
                return True
            else:
                print("❌ MENSAGEM NÃO ENCONTRADA NO SUPABASE")
                return False
        else:
            print(f"❌ ERRO AO VERIFICAR SUPABASE: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def main():
    """Função principal"""
    print("🎯 TESTE COMPLETO COM AGENTE REAL")
    print("=" * 60)
    
    # Testar agente
    result = testar_agente_real()
    
    if result:
        # Verificar se foi salvo no Supabase
        session_id = result.get("session_id")
        user_id = result.get("user_id")
        
        if session_id and user_id:
            mensagem_salva = verificar_mensagem_salva(session_id, user_id)
            
            print(f"\n" + "=" * 60)
            print("📊 RESUMO DO TESTE:")
            print(f"✅ API Response: {'OK' if result else 'FALHOU'}")
            print(f"✅ Estrutura Correta: {'OK' if result and 'messages' in result else 'FALHOU'}")
            print(f"✅ Mensagem Salva: {'OK' if mensagem_salva else 'FALHOU'}")
            print(f"🤖 Model Used: {result.get('agent_usage', {}).get('model', 'N/A')}")
            
            if result and mensagem_salva:
                print("\n🎉 TESTE COMPLETO: SUCESSO!")
            else:
                print("\n❌ TESTE COMPLETO: FALHOU")
        else:
            print("\n❌ Não foi possível verificar persistência - dados ausentes")
    else:
        print("\n❌ TESTE FALHOU - Sem resposta da API")

if __name__ == "__main__":
    main()