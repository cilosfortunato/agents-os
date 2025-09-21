#!/usr/bin/env python3
"""
Script para verificar e criar a tabela message_history no Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def verificar_criar_message_history():
    """Verifica e cria a tabela message_history no Supabase"""
    
    # Configuração do Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Erro: SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não encontradas no .env")
        return False
    
    try:
        # Conecta ao Supabase
        supabase: Client = create_client(url, key)
        print("✅ Conectado ao Supabase com sucesso!")
        
        # SQL para criar a tabela message_history
        sql_message_history = """
        -- Criar tabela message_history para memória enriquecida
        CREATE TABLE IF NOT EXISTS public.message_history (
            id SERIAL NOT NULL,
            session_id CHARACTER VARYING(255) NOT NULL,
            user_id CHARACTER VARYING(255) NOT NULL,
            role CHARACTER VARYING(50) NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITHOUT TIME ZONE NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT message_history_pkey PRIMARY KEY (id),
            CONSTRAINT message_history_role_check CHECK (
                (role)::text = ANY (
                    (ARRAY[
                        'user'::character varying,
                        'assistant'::character varying,
                        'system'::character varying
                    ])::text[]
                )
            )
        );
        
        -- Criar índices para performance
        CREATE INDEX IF NOT EXISTS idx_session_messages ON public.message_history 
        USING btree (session_id);
        
        CREATE INDEX IF NOT EXISTS idx_user_messages ON public.message_history 
        USING btree (user_id);
        
        CREATE INDEX IF NOT EXISTS idx_created_at ON public.message_history 
        USING btree (created_at);
        
        -- Comentários para documentação
        COMMENT ON TABLE public.message_history IS 'Tabela para memória enriquecida - histórico detalhado de mensagens';
        COMMENT ON COLUMN public.message_history.id IS 'ID sequencial da mensagem';
        COMMENT ON COLUMN public.message_history.session_id IS 'ID da sessão de conversa';
        COMMENT ON COLUMN public.message_history.user_id IS 'ID do usuário';
        COMMENT ON COLUMN public.message_history.role IS 'Papel: user, assistant ou system';
        COMMENT ON COLUMN public.message_history.content IS 'Conteúdo da mensagem';
        COMMENT ON COLUMN public.message_history.metadata IS 'Metadados adicionais em JSON';
        """
        
        print(f"\n🔍 Verificando tabela 'message_history'...")
        
        try:
            # Tenta fazer uma consulta simples para verificar se a tabela existe
            result = supabase.table("message_history").select("*").limit(1).execute()
            print(f"✅ Tabela 'message_history' já existe e está acessível")
            
            # Mostra algumas estatísticas
            count_result = supabase.table("message_history").select("*", count="exact").execute()
            total_registros = count_result.count if hasattr(count_result, 'count') else 0
            print(f"📊 Total de registros: {total_registros}")
            
        except Exception as e:
            print(f"⚠️ Tabela 'message_history' não encontrada: {e}")
            print(f"🔧 Criando tabela 'message_history'...")
            
            try:
                # Executa o SQL de criação usando RPC
                result = supabase.rpc('exec_sql', {'sql': sql_message_history}).execute()
                print(f"✅ Tabela 'message_history' criada com sucesso!")
                
                # Verifica se foi criada
                test_result = supabase.table("message_history").select("*").limit(1).execute()
                print(f"✅ Verificação: Tabela acessível após criação")
                
            except Exception as create_error:
                print(f"❌ Erro ao criar tabela 'message_history': {create_error}")
                print("💡 Execute este SQL manualmente no Supabase Dashboard:")
                print(f"```sql\n{sql_message_history}\n```")
                return False
        
        # Teste de inserção e consulta
        print(f"\n🧪 Testando operações na tabela...")
        
        try:
            # Testa inserção
            test_data = {
                "session_id": "test-session-123",
                "user_id": "test-user-456",
                "role": "user",
                "content": "Mensagem de teste",
                "metadata": {"test": True}
            }
            
            insert_result = supabase.table("message_history").insert(test_data).execute()
            print(f"✅ Inserção de teste: OK")
            
            # Testa consulta
            query_result = supabase.table("message_history").select("*").eq("session_id", "test-session-123").execute()
            print(f"✅ Consulta de teste: {len(query_result.data)} registros encontrados")
            
            # Remove o registro de teste
            delete_result = supabase.table("message_history").delete().eq("session_id", "test-session-123").execute()
            print(f"✅ Limpeza de teste: OK")
            
        except Exception as test_error:
            print(f"⚠️ Erro nos testes: {test_error}")
        
        print(f"\n🎉 Verificação da tabela message_history concluída!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return False

def mostrar_estrutura_message_history():
    """Mostra a estrutura da tabela message_history"""
    print("📋 ESTRUTURA DA TABELA MESSAGE_HISTORY")
    print("=" * 50)
    
    print("\n🗂️ CAMPOS:")
    print("  - id: SERIAL (chave primária)")
    print("  - session_id: VARCHAR(255) - ID da sessão")
    print("  - user_id: VARCHAR(255) - ID do usuário")
    print("  - role: VARCHAR(50) - user/assistant/system")
    print("  - content: TEXT - conteúdo da mensagem")
    print("  - metadata: JSONB - metadados extras")
    print("  - created_at: TIMESTAMP - data de criação")
    
    print("\n🔍 ÍNDICES:")
    print("  - idx_session_messages: session_id")
    print("  - idx_user_messages: user_id")
    print("  - idx_created_at: created_at")
    
    print("\n✅ CONSTRAINTS:")
    print("  - role deve ser: 'user', 'assistant' ou 'system'")
    
    print("\n💡 DIFERENÇA DAS OUTRAS TABELAS:")
    print("  - mensagens_ia: Conversas completas (pergunta + resposta)")
    print("  - message_history: Mensagens individuais enriquecidas")
    print("  - Permite rastreamento detalhado de cada interação")

if __name__ == "__main__":
    print("🚀 VERIFICAÇÃO DA TABELA MESSAGE_HISTORY")
    print("=" * 50)
    
    mostrar_estrutura_message_history()
    
    print(f"\n🔧 Iniciando verificação...")
    sucesso = verificar_criar_message_history()
    
    if sucesso:
        print(f"\n✅ Tabela message_history está pronta!")
        print(f"💡 Agora podemos implementar a memória enriquecida.")
    else:
        print(f"\n❌ Falha na verificação. Verifique as configurações.")