#!/usr/bin/env python3
"""
Debug da conexão do SupabaseService
Verifica se o sistema está usando Supabase real ou modo de memória
"""

import os
from dotenv import load_dotenv
from supabase_service import SupabaseService

# Carrega variáveis de ambiente
load_dotenv()

def debug_supabase_service():
    """Debuga a configuração do SupabaseService"""
    print("🔍 DEBUG SUPABASE SERVICE")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    print("📋 VARIÁVEIS DE AMBIENTE:")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"   SUPABASE_URL: {'✅ Definida' if supabase_url else '❌ Não definida'}")
    if supabase_url:
        print(f"   URL: {supabase_url}")
    
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Definida' if supabase_key else '❌ Não definida'}")
    if supabase_key:
        print(f"   Key: {supabase_key[:20]}...")
    
    # Verificar importação do Supabase
    print("\n📦 IMPORTAÇÃO SUPABASE:")
    try:
        from supabase import create_client, Client
        print("   ✅ Biblioteca supabase importada com sucesso")
        supabase_available = True
    except Exception as e:
        print(f"   ❌ Erro ao importar supabase: {e}")
        supabase_available = False
    
    # Testar SupabaseService
    print("\n🔧 TESTE SUPABASE SERVICE:")
    try:
        service = SupabaseService()
        print(f"   Modo memória: {'✅ SIM' if service._use_memory else '❌ NÃO'}")
        print(f"   Cliente Supabase: {'❌ None' if service.supabase is None else '✅ Ativo'}")
        
        if service._use_memory:
            print("   ⚠️  SISTEMA ESTÁ USANDO MODO DE MEMÓRIA LOCAL!")
            print("   📝 Dados não serão persistidos no Supabase")
        else:
            print("   ✅ SISTEMA ESTÁ USANDO SUPABASE REAL!")
            print("   📝 Dados serão persistidos no banco")
            
        # Testar conexão real se não estiver em modo memória
        if not service._use_memory and service.supabase:
            print("\n🌐 TESTE DE CONEXÃO:")
            try:
                # Tentar uma consulta simples
                result = service.supabase.table("agentes_solo").select("id").limit(1).execute()
                print("   ✅ Conexão com Supabase funcionando!")
                print(f"   📊 Tabela agentes_solo acessível")
            except Exception as e:
                print(f"   ❌ Erro na conexão: {e}")
                
    except Exception as e:
        print(f"   ❌ Erro ao criar SupabaseService: {e}")
    
    # Testar criação de agente
    print("\n🤖 TESTE DE CRIAÇÃO DE AGENTE:")
    try:
        service = SupabaseService()
        agent = service.create_agent(
            name="Agente Debug",
            role="Teste",
            instructions=["Teste de debug"],
            model="gemini-2.5-flash",
            provider="gemini"
        )
        
        print(f"   ✅ Agente criado com sucesso!")
        print(f"   ID: {agent.get('id')}")
        print(f"   Nome: {agent.get('name')}")
        
        if '_warning' in agent:
            print(f"   ⚠️  Warning: {agent['_warning']}")
            
        # Verificar se foi salvo no Supabase ou memória
        if service._use_memory:
            print("   📝 Agente salvo em MEMÓRIA LOCAL")
        else:
            print("   📝 Agente salvo no SUPABASE")
            
    except Exception as e:
        print(f"   ❌ Erro ao criar agente: {e}")

def main():
    """Função principal"""
    debug_supabase_service()
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSÃO:")
    print("Se o sistema está em modo memória, os dados não são")
    print("persistidos no Supabase, explicando por que as tabelas")
    print("estão vazias na verificação MCP Postgrest.")

if __name__ == "__main__":
    main()