#!/usr/bin/env python3
"""
Verificação do agente real específico no Supabase
Agente ID: da93fcc7-cf93-403e-aa99-9e295080d692
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

AGENT_ID = "da93fcc7-cf93-403e-aa99-9e295080d692"

def verificar_agente_especifico():
    """Verifica o agente específico no Supabase"""
    print("🤖 VERIFICANDO AGENTE ESPECÍFICO")
    print("=" * 50)
    print(f"🎯 Agent ID: {AGENT_ID}")
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/agentes_solo?id=eq.{AGENT_ID}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            agentes = response.json()
            if agentes:
                agente = agentes[0]
                print("✅ Agente encontrado!")
                print(f"   📋 Nome: {agente.get('name')}")
                print(f"   🎭 Role: {agente.get('role')}")
                print(f"   🤖 Model: {agente.get('model')}")
                print(f"   🏢 Provider: {agente.get('provider')}")
                print(f"   📝 Instructions: {agente.get('instructions', '')[:100]}...")
                print(f"   🌐 Webhook URL: {agente.get('webhook_url')}")
                print(f"   🔧 Config: {agente.get('config')}")
                print(f"   📅 Criado em: {agente.get('created_at')}")
                return agente
            else:
                print("❌ Agente não encontrado!")
                return None
        else:
            print(f"❌ Erro ao buscar agente: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        return None

def verificar_mensagens_do_agente():
    """Verifica mensagens específicas deste agente"""
    print("\n💬 VERIFICANDO MENSAGENS DO AGENTE")
    print("=" * 50)
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/mensagens_ia?agent_id=eq.{AGENT_ID}&order=created_at.desc&limit=10"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            mensagens = response.json()
            print(f"✅ Total de mensagens encontradas: {len(mensagens)}")
            
            if mensagens:
                for i, msg in enumerate(mensagens, 1):
                    print(f"\n📨 Mensagem {i}:")
                    print(f"   ID: {msg.get('id')}")
                    print(f"   User ID: {msg.get('user_id')}")
                    print(f"   Session ID: {msg.get('session_id')}")
                    print(f"   User Message: {msg.get('user_message', '')[:80]}...")
                    print(f"   Agent Response: {msg.get('agent_response', '')[:80]}...")
                    print(f"   Criada em: {msg.get('created_at')}")
                    
                    # Verificar se tem webhook_response
                    if 'webhook_response' in msg:
                        print(f"   🌐 Webhook Response: {msg.get('webhook_response')}")
                    
                return mensagens
            else:
                print("📭 Nenhuma mensagem encontrada para este agente")
                return []
                
        else:
            print(f"❌ Erro ao buscar mensagens: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        return []

def verificar_memorias_do_agente():
    """Verifica memórias relacionadas a este agente"""
    print("\n🧠 VERIFICANDO MEMÓRIAS DO AGENTE")
    print("=" * 50)
    
    try:
        # Verificar na tabela enriched_memories
        url = f"{SUPABASE_URL}/rest/v1/enriched_memories?agent_id=eq.{AGENT_ID}&order=created_at.desc&limit=5"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            memorias = response.json()
            print(f"✅ Total de memórias encontradas: {len(memorias)}")
            
            if memorias:
                for i, mem in enumerate(memorias, 1):
                    print(f"\n🧠 Memória {i}:")
                    print(f"   ID: {mem.get('id')}")
                    print(f"   User ID: {mem.get('user_id')}")
                    print(f"   Content: {mem.get('content', '')[:80]}...")
                    print(f"   Metadata: {mem.get('metadata')}")
                    print(f"   Criada em: {mem.get('created_at')}")
                    
                return memorias
            else:
                print("📭 Nenhuma memória encontrada para este agente")
                return []
                
        else:
            print(f"❌ Erro ao buscar memórias: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        return []

def verificar_webhook_config():
    """Verifica configuração do webhook"""
    print("\n🌐 VERIFICANDO CONFIGURAÇÃO DO WEBHOOK")
    print("=" * 50)
    
    # Verificar arquivo de configuração
    webhook_files = ['.env', 'config.py', 'webhook_server.py']
    
    for file in webhook_files:
        if os.path.exists(file):
            print(f"📄 Arquivo {file} encontrado")
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'webhook' in content.lower() or 'WEBHOOK' in content:
                        print(f"   ✅ Contém configurações de webhook")
                        # Procurar por URLs de webhook
                        lines = content.split('\n')
                        for line in lines:
                            if 'webhook' in line.lower() and ('http' in line or 'url' in line.lower()):
                                print(f"   🔗 {line.strip()}")
                    else:
                        print(f"   ❌ Não contém configurações de webhook")
            except Exception as e:
                print(f"   ❌ Erro ao ler arquivo: {e}")
        else:
            print(f"📄 Arquivo {file} não encontrado")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DO AGENTE REAL")
    print("=" * 60)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Supabase URL: {SUPABASE_URL}")
    
    # Verificar agente
    agente = verificar_agente_especifico()
    
    if agente:
        # Verificar mensagens
        mensagens = verificar_mensagens_do_agente()
        
        # Verificar memórias
        memorias = verificar_memorias_do_agente()
        
        # Verificar webhook
        verificar_webhook_config()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO:")
        print(f"✅ Agente: {'Encontrado' if agente else 'Não encontrado'}")
        print(f"💬 Mensagens: {len(mensagens) if 'mensagens' in locals() else 0}")
        print(f"🧠 Memórias: {len(memorias) if 'memorias' in locals() else 0}")
        
        if agente and agente.get('webhook_url'):
            print(f"🌐 Webhook configurado: {agente.get('webhook_url')}")
        else:
            print("🌐 Webhook: Não configurado")
    else:
        print("\n❌ Não foi possível verificar o agente")

if __name__ == "__main__":
    main()