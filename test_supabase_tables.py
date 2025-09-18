#!/usr/bin/env python3
"""
Teste para verificar quais tabelas existem no Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def list_tables():
    """Lista as tabelas disponíveis no Supabase"""
    print("🔍 VERIFICANDO TABELAS NO SUPABASE")
    print("=" * 50)
    
    # Configuração do Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Credenciais do Supabase não encontradas")
        return
    
    try:
        # Cria cliente Supabase
        supabase: Client = create_client(url, key)
        print("✅ Cliente Supabase criado com sucesso")
        
        # Tenta acessar algumas tabelas comuns
        tables_to_test = ["messages", "mensagens_ia", "agents", "agentes"]
        
        for table_name in tables_to_test:
            try:
                print(f"\n🔍 Testando tabela: {table_name}")
                result = supabase.table(table_name).select("*").limit(1).execute()
                print(f"✅ Tabela '{table_name}' existe e é acessível")
                print(f"   Colunas encontradas: {list(result.data[0].keys()) if result.data else 'Tabela vazia'}")
            except Exception as e:
                print(f"❌ Tabela '{table_name}' não existe ou não é acessível: {e}")
        
        # Tenta criar a tabela messages se não existir
        print(f"\n📝 TENTANDO CRIAR TABELA MESSAGES")
        try:
            # Executa o SQL para criar a tabela
            sql_create = """
            CREATE TABLE IF NOT EXISTS messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            """
            
            # Nota: O Supabase Python client não suporta execução direta de SQL DDL
            # Precisamos usar o SQL Editor do Supabase ou a API REST
            print("⚠️  Para criar a tabela, execute o script create_messages_table.sql no SQL Editor do Supabase")
            print("   URL: https://usigbcsmzialnulsvpfr.supabase.co/project/default/sql")
            
        except Exception as e:
            print(f"❌ Erro ao tentar criar tabela: {e}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    list_tables()