#!/usr/bin/env python3
"""
Script para verificar e atualizar a estrutura da tabela agentes_solo
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def check_table_structure():
    """Verifica a estrutura atual da tabela agentes_solo"""
    
    print("🔍 Verificando estrutura da tabela agentes_solo...")
    
    # Inicializa cliente Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem estar definidas no .env")
        return
    
    supabase: Client = create_client(url, key)
    
    try:
        # Busca um agente existente para ver a estrutura
        result = supabase.table("agentes_solo").select("*").limit(1).execute()
        
        if result.data:
            agent = result.data[0]
            print("✅ Estrutura atual da tabela agentes_solo:")
            for key, value in agent.items():
                print(f"   - {key}: {type(value).__name__}")
            
            # Verifica se a coluna provider existe
            if 'provider' in agent:
                print("✅ Coluna 'provider' já existe!")
            else:
                print("❌ Coluna 'provider' NÃO existe!")
                print("💡 Será necessário adicionar a coluna via SQL no Supabase Dashboard")
                print_sql_command()
        else:
            print("⚠️ Nenhum agente encontrado na tabela")
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")

def print_sql_command():
    """Imprime o comando SQL para adicionar a coluna provider"""
    
    print("\n📝 COMANDO SQL PARA EXECUTAR NO SUPABASE:")
    print("=" * 50)
    print("ALTER TABLE agentes_solo ADD COLUMN provider TEXT DEFAULT 'gemini';")
    print("=" * 50)
    print("\n📋 INSTRUÇÕES:")
    print("1. Acesse o Supabase Dashboard")
    print("2. Vá para SQL Editor")
    print("3. Execute o comando SQL acima")
    print("4. Execute este script novamente para verificar")

def test_provider_column():
    """Testa se consegue inserir um agente com a coluna provider"""
    
    print("\n🧪 Testando inserção com coluna provider...")
    
    # Inicializa cliente Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Tenta inserir um agente de teste
        test_agent = {
            "name": "Teste Provider Column",
            "role": "Teste",
            "instructions": ["Teste"],
            "model": "gemini-2.5-flash",
            "provider": "gemini",
            "account_id": "test-account-id"
        }
        
        result = supabase.table("agentes_solo").insert(test_agent).execute()
        
        if result.data:
            print("✅ Teste de inserção com provider: SUCESSO!")
            
            # Remove o agente de teste
            agent_id = result.data[0]['id']
            supabase.table("agentes_solo").delete().eq("id", agent_id).execute()
            print("🗑️ Agente de teste removido")
        else:
            print("❌ Teste de inserção com provider: FALHOU!")
            
    except Exception as e:
        print(f"❌ Erro no teste de inserção: {e}")

def main():
    """Função principal"""
    print("🔧 VERIFICAÇÃO E ATUALIZAÇÃO DA TABELA AGENTES_SOLO")
    print("=" * 60)
    
    # Verifica estrutura atual
    check_table_structure()
    
    # Pergunta se deve testar a inserção
    print("\n" + "=" * 60)
    response = input("Deseja testar a inserção com provider? (s/n): ").lower()
    
    if response == 's':
        test_provider_column()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Se a coluna provider não existe, execute o SQL no Supabase")
    print("2. Execute novamente o teste de criação de agente")
    print("3. Verifique se o agente foi criado com sucesso")

if __name__ == "__main__":
    main()