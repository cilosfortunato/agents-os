#!/usr/bin/env python3
"""
Verificação de todos os agentes no Supabase
Lista todos os agentes para entender o que está sendo salvo
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

def listar_todos_agentes():
    """Lista todos os agentes na tabela agentes_solo"""
    print("🤖 LISTANDO TODOS OS AGENTES")
    print("=" * 50)
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/agentes_solo"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            agentes = response.json()
            print(f"✅ Total de agentes encontrados: {len(agentes)}")
            
            if agentes:
                for i, agente in enumerate(agentes, 1):
                    print(f"\n📋 Agente {i}:")
                    print(f"   ID: {agente.get('id')}")
                    print(f"   Nome: {agente.get('name')}")
                    print(f"   Role: {agente.get('role')}")
                    print(f"   Model: {agente.get('model')}")
                    print(f"   Provider: {agente.get('provider')}")
                    print(f"   Criado em: {agente.get('created_at')}")
                    
                    # Verificar se é o agente do teste
                    if agente.get('id') == '07d55006-f32e-4e3f-9e04-c3efd5aed297':
                        print("   🎯 ESTE É O AGENTE DO TESTE!")
                    
                    # Verificar se é o agente do debug
                    if agente.get('name') == 'Agente Debug':
                        print("   🔧 ESTE É O AGENTE DO DEBUG!")
            else:
                print("📭 Nenhum agente encontrado na tabela")
                
        else:
            print(f"❌ Erro ao listar agentes: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")

def listar_todas_mensagens():
    """Lista todas as mensagens na tabela mensagens_ia"""
    print("\n💬 LISTANDO TODAS AS MENSAGENS")
    print("=" * 50)
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/mensagens_ia"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            mensagens = response.json()
            print(f"✅ Total de mensagens encontradas: {len(mensagens)}")
            
            if mensagens:
                for i, msg in enumerate(mensagens, 1):
                    print(f"\n📨 Mensagem {i}:")
                    print(f"   ID: {msg.get('id')}")
                    print(f"   Agent ID: {msg.get('agent_id')}")
                    print(f"   User ID: {msg.get('user_id')}")
                    print(f"   Session ID: {msg.get('session_id')}")
                    print(f"   User Message: {msg.get('user_message', '')[:50]}...")
                    print(f"   Agent Response: {msg.get('agent_response', '')[:50]}...")
                    print(f"   Criada em: {msg.get('created_at')}")
                    
                    # Verificar se é do teste
                    if msg.get('agent_id') == '07d55006-f32e-4e3f-9e04-c3efd5aed297':
                        print("   🎯 ESTA É UMA MENSAGEM DO TESTE!")
            else:
                print("📭 Nenhuma mensagem encontrada na tabela")
                
        else:
            print(f"❌ Erro ao listar mensagens: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")

def verificar_estrutura_tabelas():
    """Verifica a estrutura das tabelas"""
    print("\n🏗️  VERIFICANDO ESTRUTURA DAS TABELAS")
    print("=" * 50)
    
    tabelas = ["agentes_solo", "mensagens_ia"]
    
    for tabela in tabelas:
        print(f"\n📋 Tabela: {tabela}")
        try:
            url = f"{SUPABASE_URL}/rest/v1/{tabela}?limit=1"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                dados = response.json()
                if dados:
                    print("   Colunas encontradas:")
                    for coluna in dados[0].keys():
                        print(f"   - {coluna}")
                else:
                    print("   ✅ Tabela existe mas está vazia")
            else:
                print(f"   ❌ Erro: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO COMPLETA DO SUPABASE")
    print("=" * 60)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: {SUPABASE_URL}")
    
    verificar_estrutura_tabelas()
    listar_todos_agentes()
    listar_todas_mensagens()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSÃO:")
    print("Esta verificação mostra exatamente o que está")
    print("salvo no Supabase e ajuda a entender por que")
    print("o teste original não encontrou dados.")

if __name__ == "__main__":
    main()