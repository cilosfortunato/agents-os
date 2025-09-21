#!/usr/bin/env python3
"""
Script para criar a tabela agno_memories no Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def criar_tabela_agno_memories():
    """Cria a tabela agno_memories no Supabase"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Credenciais do Supabase não encontradas")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Primeiro, verificar se a tabela já existe
        try:
            result = supabase.table("agno_memories").select("*").limit(1).execute()
            print("✅ Tabela agno_memories já existe!")
            print(f"📊 Registros existentes: {len(result.data)}")
            return True
        except Exception as e:
            print(f"📝 Tabela agno_memories não existe: {e}")
        
        # Ler o arquivo SQL
        try:
            with open("create_agno_memories_table.sql", "r", encoding="utf-8") as f:
                sql_content = f.read()
            print("✅ Arquivo SQL carregado")
        except Exception as e:
            print(f"❌ Erro ao ler arquivo SQL: {e}")
            return False
        
        # Dividir o SQL em comandos individuais
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        print(f"🔄 Executando {len(sql_commands)} comandos SQL...")
        
        # Executar cada comando
        for i, sql_cmd in enumerate(sql_commands):
            if not sql_cmd:
                continue
                
            try:
                # Usar o método raw SQL do Supabase
                supabase.postgrest.session.post(
                    f"{supabase_url}/rest/v1/rpc/exec_sql",
                    json={"sql": sql_cmd},
                    headers={
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                        "Content-Type": "application/json"
                    }
                )
                print(f"✅ Comando {i+1}/{len(sql_commands)} executado")
            except Exception as e:
                print(f"⚠️ Erro no comando {i+1}: {e}")
                # Continuar com próximo comando
                continue
        
        # Verificar se a tabela foi criada
        try:
            result = supabase.table("agno_memories").select("*").limit(1).execute()
            print("✅ Tabela agno_memories criada com sucesso!")
            
            # Testar inserção
            test_data = {
                "memory_id": "test-memory-001",
                "memory": "Teste de memória do Agno - usuário prefere respostas técnicas",
                "topics": ["teste", "agno", "preferencias"],
                "user_id": "test-user-123",
                "agent_id": "test-agent-456"
            }
            
            insert_result = supabase.table("agno_memories").insert(test_data).execute()
            print("✅ Teste de inserção bem-sucedido")
            print(f"📝 Dados inseridos: {insert_result.data[0]['memory_id']}")
            
            # Testar busca
            search_result = supabase.table("agno_memories").select("*").eq("user_id", "test-user-123").execute()
            print(f"✅ Teste de busca: {len(search_result.data)} registros encontrados")
            
            # Limpar teste
            supabase.table("agno_memories").delete().eq("memory_id", "test-memory-001").execute()
            print("✅ Limpeza de teste concluída")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar tabela criada: {e}")
            
            # Tentar criar manualmente usando INSERT
            print("🔄 Tentando criar tabela via INSERT...")
            try:
                # Forçar criação da tabela tentando inserir dados
                test_insert = {
                    "memory_id": "force-create-001",
                    "memory": "Forçando criação da tabela",
                    "topics": ["setup"],
                    "user_id": "setup-user"
                }
                
                # Isso deve falhar, mas pode criar a tabela
                try:
                    supabase.table("agno_memories").insert(test_insert).execute()
                    print("✅ Tabela criada via INSERT!")
                    
                    # Limpar
                    supabase.table("agno_memories").delete().eq("memory_id", "force-create-001").execute()
                    return True
                except Exception as insert_error:
                    print(f"❌ INSERT também falhou: {insert_error}")
                    
                    # Instruções manuais
                    print("\n" + "="*60)
                    print("📋 INSTRUÇÕES MANUAIS PARA CRIAR A TABELA:")
                    print("1. Acesse: https://supabase.com/dashboard")
                    print("2. Selecione seu projeto")
                    print("3. Vá para 'SQL Editor'")
                    print("4. Execute o conteúdo do arquivo 'create_agno_memories_table.sql'")
                    print("5. Ou execute este SQL básico:")
                    print("""
CREATE TABLE public.agno_memories (
    memory_id VARCHAR(255) PRIMARY KEY,
    memory TEXT NOT NULL,
    topics TEXT[] DEFAULT '{}',
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    team_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
                    """)
                    print("="*60)
                    return False
                    
            except Exception as e3:
                print(f"❌ Erro final: {e3}")
                return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Criando tabela agno_memories...")
    sucesso = criar_tabela_agno_memories()
    
    if sucesso:
        print("🎉 Processo concluído com sucesso!")
        print("📋 A tabela agno_memories está pronta para uso!")
    else:
        print("❌ Processo falhou - veja instruções manuais acima")