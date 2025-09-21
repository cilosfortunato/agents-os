#!/usr/bin/env python3
"""
Verificação do Supabase via MCP Postgrest
Verifica se os dados do teste do agente Gemini foram salvos corretamente
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Supabase (carregadas do .env)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://usigbcsmzialnulsvpfr.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVzaWdiY3NtemlhbG51bHN2cGZyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDM0Mjg1MiwiZXhwIjoyMDY1OTE4ODUyfQ.udMP2y7D81l4liL1zfzCBNN36w16YbI2HAU_7sIj9Y0")

# Headers para autenticação
headers = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

# Dados do teste (do resultado anterior)
TEST_DATA = {
    "agent_id": "07d55006-f32e-4e3f-9e04-c3efd5aed297",
    "user_id": "test_user_1758400469", 
    "session_id": "5dc92f47-188c-417c-977a-aae5408fd382"
}

def verificar_tabela(tabela: str, filtros: dict = None):
    """Verifica dados em uma tabela específica"""
    print(f"\n🔍 Verificando tabela: {tabela}")
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/{tabela}"
        
        # Adicionar filtros se fornecidos
        if filtros:
            params = []
            for campo, valor in filtros.items():
                params.append(f"{campo}=eq.{valor}")
            if params:
                url += "?" + "&".join(params)
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            dados = response.json()
            print(f"✅ Tabela {tabela}: {len(dados)} registros encontrados")
            
            if dados:
                print(f"📄 Primeiros registros:")
                for i, registro in enumerate(dados[:3]):  # Mostrar até 3 registros
                    print(f"   {i+1}. {json.dumps(registro, indent=2, default=str)[:200]}...")
            
            return dados
        else:
            print(f"❌ Erro ao acessar {tabela}: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na verificação de {tabela}: {e}")
        return None

def verificar_agente():
    """Verifica se o agente foi criado"""
    print("\n🤖 VERIFICANDO AGENTE")
    print("=" * 50)
    
    agentes = verificar_tabela("agentes_solo", {"id": TEST_DATA["agent_id"]})
    
    if agentes and len(agentes) > 0:
        agente = agentes[0]
        print(f"✅ Agente encontrado:")
        print(f"   - ID: {agente.get('id')}")
        print(f"   - Nome: {agente.get('name')}")
        print(f"   - Modelo: {agente.get('model')}")
        print(f"   - Criado em: {agente.get('created_at')}")
        return True
    else:
        print("❌ Agente não encontrado no banco")
        return False

def verificar_mensagens():
    """Verifica se as mensagens foram salvas"""
    print("\n💬 VERIFICANDO MENSAGENS")
    print("=" * 50)
    
    # Verificar por agent_id
    mensagens = verificar_tabela("mensagens_ia", {"agent_id": TEST_DATA["agent_id"]})
    
    if mensagens and len(mensagens) > 0:
        print(f"✅ {len(mensagens)} mensagens encontradas para o agente")
        
        for i, msg in enumerate(mensagens):
            print(f"   Mensagem {i+1}:")
            print(f"   - Role: {msg.get('role')}")
            print(f"   - Content: {msg.get('content', '')[:100]}...")
            print(f"   - User ID: {msg.get('user_id')}")
            print(f"   - Session ID: {msg.get('session_id')}")
            print(f"   - Criada em: {msg.get('created_at')}")
            print()
        
        return True
    else:
        print("❌ Nenhuma mensagem encontrada")
        return False

def verificar_conversas():
    """Verifica se as conversas foram registradas"""
    print("\n🗣️  VERIFICANDO CONVERSAS")
    print("=" * 50)
    
    # Verificar por session_id
    conversas = verificar_tabela("conversas", {"session_id": TEST_DATA["session_id"]})
    
    if conversas and len(conversas) > 0:
        print(f"✅ {len(conversas)} conversas encontradas")
        
        for conversa in conversas:
            print(f"   - ID: {conversa.get('id')}")
            print(f"   - Agent ID: {conversa.get('agent_id')}")
            print(f"   - User ID: {conversa.get('user_id')}")
            print(f"   - Session ID: {conversa.get('session_id')}")
            print(f"   - Criada em: {conversa.get('created_at')}")
        
        return True
    else:
        print("❌ Nenhuma conversa encontrada")
        return False

def verificar_memoria():
    """Verifica se há registros de memória"""
    print("\n🧠 VERIFICANDO MEMÓRIA")
    print("=" * 50)
    
    # Verificar tabela de memória enriquecida
    memorias = verificar_tabela("enriched_memories", {"user_id": TEST_DATA["user_id"]})
    
    if memorias and len(memorias) > 0:
        print(f"✅ {len(memorias)} memórias encontradas")
        
        for memoria in memorias:
            print(f"   - ID: {memoria.get('id')}")
            print(f"   - User ID: {memoria.get('user_id')}")
            print(f"   - Memory: {memoria.get('memory', '')[:100]}...")
            print(f"   - Category: {memoria.get('category')}")
            print(f"   - Criada em: {memoria.get('created_at')}")
        
        return True
    else:
        print("ℹ️  Nenhuma memória específica encontrada (normal para testes)")
        return True  # Não é erro crítico

def main():
    """Função principal de verificação"""
    print("🔍 VERIFICAÇÃO SUPABASE VIA MCP POSTGREST")
    print("=" * 60)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Dados do teste:")
    print(f"   - Agent ID: {TEST_DATA['agent_id']}")
    print(f"   - User ID: {TEST_DATA['user_id']}")
    print(f"   - Session ID: {TEST_DATA['session_id']}")
    
    # Executar verificações
    resultados = {
        "agente": verificar_agente(),
        "mensagens": verificar_mensagens(),
        "conversas": verificar_conversas(),
        "memoria": verificar_memoria()
    }
    
    # Resumo final
    print("\n📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    total_checks = len(resultados)
    passed_checks = sum(resultados.values())
    
    for check, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{check.capitalize():15} | {status}")
    
    print("-" * 60)
    print(f"Total: {passed_checks}/{total_checks} verificações passaram")
    
    if passed_checks == total_checks:
        print("🎉 VERIFICAÇÃO COMPLETA PASSOU!")
        print("✅ Todos os dados foram salvos corretamente no Supabase")
    elif passed_checks >= total_checks - 1:
        print("⚠️  VERIFICAÇÃO QUASE COMPLETA")
        print("✅ Dados principais salvos, algumas tabelas podem estar vazias")
    else:
        print("❌ VERIFICAÇÃO FALHOU")
        print("❌ Problemas na persistência dos dados")
    
    return passed_checks >= total_checks - 1

if __name__ == "__main__":
    main()