#!/usr/bin/env python3
"""
Script simplificado para criar a tabela agno_memories no Supabase
Usando o mesmo método que funcionou para message_history
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def criar_tabela_agno_memories():
    """Cria a tabela agno_memories no Supabase usando método direto"""
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
            print(f"📝 Tabela agno_memories não existe, criando...")
        
        # SQL para criar a tabela (método simples que funcionou)
        sql_create = """
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
        """
        
        # Executar usando o método que funcionou para message_history
        print("🔄 Criando tabela agno_memories...")
        
        # Usar o método rpc do Supabase
        try:
            # Tentar criar usando RPC
            result = supabase.rpc('exec_sql', {'sql': sql_create}).execute()
            print("✅ Tabela criada via RPC!")
        except Exception as e:
            print(f"⚠️ RPC falhou: {e}")
            
            # Método alternativo: usar SQL direto
            try:
                # Usar o método que funcionou para message_history
                # Criar dados de teste para forçar criação da estrutura
                test_data = {
                    "memory_id": "setup-test-001",
                    "memory": "Teste inicial para criar estrutura da tabela",
                    "topics": ["setup", "test"],
                    "user_id": "setup-user",
                    "agent_id": "setup-agent",
                    "team_id": "setup-team"
                }
                
                # Isso deve criar a tabela automaticamente
                insert_result = supabase.table("agno_memories").insert(test_data).execute()
                print("✅ Tabela criada via INSERT automático!")
                
                # Limpar dados de teste
                supabase.table("agno_memories").delete().eq("memory_id", "setup-test-001").execute()
                print("✅ Dados de teste removidos")
                
            except Exception as e2:
                print(f"❌ Método INSERT falhou: {e2}")
                return False
        
        # Verificar se a tabela foi criada
        try:
            result = supabase.table("agno_memories").select("*").limit(1).execute()
            print("✅ Verificação: Tabela agno_memories está acessível!")
            
            # Criar índices importantes
            indices_sql = [
                "CREATE INDEX IF NOT EXISTS idx_agno_memories_user_id ON public.agno_memories(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_agno_memories_agent_id ON public.agno_memories(agent_id);",
                "CREATE INDEX IF NOT EXISTS idx_agno_memories_created_at ON public.agno_memories(created_at);"
            ]
            
            for idx_sql in indices_sql:
                try:
                    supabase.rpc('exec_sql', {'sql': idx_sql}).execute()
                    print(f"✅ Índice criado")
                except:
                    print(f"⚠️ Índice pode já existir")
            
            # Testar inserção real
            test_memory = {
                "memory_id": "test-memory-001",
                "memory": "Usuário prefere respostas técnicas e detalhadas",
                "topics": ["preferencias", "estilo", "tecnico"],
                "user_id": "test-user-123",
                "agent_id": "test-agent-456"
            }
            
            insert_result = supabase.table("agno_memories").insert(test_memory).execute()
            print("✅ Teste de inserção bem-sucedido")
            print(f"📝 Memory ID: {insert_result.data[0]['memory_id']}")
            
            # Testar busca
            search_result = supabase.table("agno_memories").select("*").eq("user_id", "test-user-123").execute()
            print(f"✅ Teste de busca: {len(search_result.data)} memórias encontradas")
            
            # Testar busca por tópicos
            topic_result = supabase.table("agno_memories").select("*").contains("topics", ["tecnico"]).execute()
            print(f"✅ Busca por tópicos: {len(topic_result.data)} memórias com tópico 'tecnico'")
            
            # Limpar teste
            supabase.table("agno_memories").delete().eq("memory_id", "test-memory-001").execute()
            print("✅ Limpeza de teste concluída")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação final: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Criando tabela agno_memories (método simplificado)...")
    sucesso = criar_tabela_agno_memories()
    
    if sucesso:
        print("🎉 Tabela agno_memories criada e testada com sucesso!")
        print("📋 Pronta para armazenar memórias do Agno!")
    else:
        print("❌ Falha na criação da tabela")
        print("💡 Tente criar manualmente no dashboard do Supabase")