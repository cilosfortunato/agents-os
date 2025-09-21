#!/usr/bin/env python3
"""
Script para verificar e criar as tabelas necessárias no Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def verificar_criar_tabelas():
    """Verifica e cria as tabelas necessárias no Supabase"""
    
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
        
        # Lista de tabelas necessárias
        tabelas_necessarias = {
            "agentes_solo": """
                CREATE TABLE IF NOT EXISTS agentes_solo (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    instructions TEXT[] NOT NULL DEFAULT '{}',
                    model TEXT NOT NULL DEFAULT 'gemini-2.5-flash',
                    provider TEXT NOT NULL DEFAULT 'gemini',
                    account_id UUID NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                -- Índices
                CREATE INDEX IF NOT EXISTS idx_agentes_solo_account_id ON agentes_solo(account_id);
                CREATE INDEX IF NOT EXISTS idx_agentes_solo_created_at ON agentes_solo(created_at);
                
                -- Trigger para updated_at
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
                
                DROP TRIGGER IF EXISTS update_agentes_solo_updated_at ON agentes_solo;
                CREATE TRIGGER update_agentes_solo_updated_at 
                    BEFORE UPDATE ON agentes_solo 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column();
            """,
            
            "mensagens_ia": """
                CREATE TABLE IF NOT EXISTS mensagens_ia (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    agent_name TEXT,
                    message_id TEXT,
                    timestamp TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                -- Índices para performance
                CREATE INDEX IF NOT EXISTS idx_mensagens_ia_user_id ON mensagens_ia(user_id);
                CREATE INDEX IF NOT EXISTS idx_mensagens_ia_session_id ON mensagens_ia(session_id);
                CREATE INDEX IF NOT EXISTS idx_mensagens_ia_agent_id ON mensagens_ia(agent_id);
                CREATE INDEX IF NOT EXISTS idx_mensagens_ia_created_at ON mensagens_ia(created_at);
                CREATE INDEX IF NOT EXISTS idx_mensagens_ia_user_session ON mensagens_ia(user_id, session_id);
                
                -- Trigger para updated_at
                DROP TRIGGER IF EXISTS update_mensagens_ia_updated_at ON mensagens_ia;
                CREATE TRIGGER update_mensagens_ia_updated_at 
                    BEFORE UPDATE ON mensagens_ia 
                    FOR EACH ROW 
                    EXECUTE FUNCTION update_updated_at_column();
            """
        }
        
        # Verifica e cria cada tabela
        for nome_tabela, sql_criacao in tabelas_necessarias.items():
            print(f"\n🔍 Verificando tabela '{nome_tabela}'...")
            
            try:
                # Tenta fazer uma consulta simples para verificar se a tabela existe
                result = supabase.table(nome_tabela).select("*").limit(1).execute()
                print(f"✅ Tabela '{nome_tabela}' já existe e está acessível")
                
                # Mostra algumas estatísticas
                count_result = supabase.table(nome_tabela).select("*", count="exact").execute()
                total_registros = count_result.count if hasattr(count_result, 'count') else 0
                print(f"📊 Total de registros: {total_registros}")
                
            except Exception as e:
                print(f"⚠️ Tabela '{nome_tabela}' não encontrada ou inacessível: {e}")
                print(f"🔧 Criando tabela '{nome_tabela}'...")
                
                try:
                    # Executa o SQL de criação
                    supabase.rpc('exec_sql', {'sql': sql_criacao}).execute()
                    print(f"✅ Tabela '{nome_tabela}' criada com sucesso!")
                except Exception as create_error:
                    print(f"❌ Erro ao criar tabela '{nome_tabela}': {create_error}")
                    print("💡 Você pode executar o SQL manualmente no Supabase Dashboard:")
                    print(f"```sql\n{sql_criacao}\n```")
        
        # Teste final de conectividade
        print(f"\n🧪 Testando conectividade final...")
        
        # Testa agentes_solo
        try:
            agentes = supabase.table("agentes_solo").select("id, name").limit(5).execute()
            print(f"✅ agentes_solo: {len(agentes.data)} agentes encontrados")
        except Exception as e:
            print(f"❌ Erro ao acessar agentes_solo: {e}")
        
        # Testa mensagens_ia
        try:
            mensagens = supabase.table("mensagens_ia").select("id, user_id").limit(5).execute()
            print(f"✅ mensagens_ia: {len(mensagens.data)} mensagens encontradas")
        except Exception as e:
            print(f"❌ Erro ao acessar mensagens_ia: {e}")
        
        print(f"\n🎉 Verificação concluída!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        return False

def mostrar_informacoes_tabelas():
    """Mostra informações sobre as tabelas usadas"""
    print("📋 INFORMAÇÕES SOBRE AS TABELAS DO SUPABASE")
    print("=" * 50)
    
    print("\n🤖 TABELA: agentes_solo")
    print("Descrição: Armazena os agentes de IA configurados")
    print("Campos principais:")
    print("  - id: UUID único do agente")
    print("  - name: Nome do agente")
    print("  - role: Função/papel do agente")
    print("  - instructions: Array de instruções")
    print("  - model: Modelo de IA usado")
    print("  - provider: Provedor (gemini, openai, etc)")
    print("  - account_id: ID da conta proprietária")
    
    print("\n💬 TABELA: mensagens_ia")
    print("Descrição: Armazena histórico de conversas")
    print("Campos principais:")
    print("  - id: UUID único da mensagem")
    print("  - user_id: ID do usuário")
    print("  - session_id: ID da sessão de conversa")
    print("  - agent_id: ID do agente que respondeu")
    print("  - user_message: Mensagem do usuário")
    print("  - agent_response: Resposta do agente")
    print("  - agent_name: Nome do agente")
    print("  - message_id: ID da mensagem (opcional)")
    print("  - timestamp: Timestamp personalizado (opcional)")
    
    print("\n🔍 COMO VERIFICAR NO SUPABASE DASHBOARD:")
    print("1. Acesse https://supabase.com/dashboard")
    print("2. Selecione seu projeto")
    print("3. Vá em 'Table Editor' no menu lateral")
    print("4. Procure pelas tabelas: 'agentes_solo' e 'mensagens_ia'")

if __name__ == "__main__":
    print("🚀 VERIFICAÇÃO E CRIAÇÃO DE TABELAS SUPABASE")
    print("=" * 50)
    
    mostrar_informacoes_tabelas()
    
    print(f"\n🔧 Iniciando verificação...")
    sucesso = verificar_criar_tabelas()
    
    if sucesso:
        print(f"\n✅ Processo concluído com sucesso!")
        print(f"💡 As tabelas estão prontas para uso na API.")
    else:
        print(f"\n❌ Processo falhou. Verifique as configurações do Supabase.")