#!/usr/bin/env python3
"""
Teste direto da conexão com Supabase e tabela messages
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão direta com o Supabase"""
    print("🔍 TESTE DIRETO DO SUPABASE")
    print("=" * 50)
    
    # Configuração do Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"📡 URL: {url}")
    print(f"🔑 Key: {key[:20]}..." if key else "❌ Key não encontrada")
    
    if not url or not key:
        print("❌ Credenciais do Supabase não encontradas no .env")
        return False
    
    try:
        # Cria cliente Supabase
        supabase: Client = create_client(url, key)
        print("✅ Cliente Supabase criado com sucesso")
        
        # Testa inserção na tabela messages
        print("\n📝 TESTANDO INSERÇÃO NA TABELA MESSAGES")
        test_data = {
            "user_id": "test-user-123",
            "session_id": "test-session-456", 
            "agent_id": "test-agent-789",
            "user_message": "Teste de mensagem",
            "agent_response": "Resposta de teste"
        }
        
        result = supabase.table("messages").insert(test_data).execute()
        
        if result.data:
            print("✅ Inserção bem-sucedida!")
            print(f"📊 Dados inseridos: {result.data[0]}")
            
            # Testa busca
            print("\n🔍 TESTANDO BUSCA NA TABELA MESSAGES")
            search_result = supabase.table("messages").select("*").eq("user_id", "test-user-123").execute()
            
            if search_result.data:
                print(f"✅ Busca bem-sucedida! Encontradas {len(search_result.data)} mensagens")
                for msg in search_result.data:
                    print(f"  - ID: {msg['id']}")
                    print(f"  - Mensagem: {msg['user_message']}")
                    print(f"  - Resposta: {msg['agent_response']}")
            else:
                print("❌ Nenhuma mensagem encontrada na busca")
                
            # Limpa dados de teste
            print("\n🧹 LIMPANDO DADOS DE TESTE")
            delete_result = supabase.table("messages").delete().eq("user_id", "test-user-123").execute()
            print("✅ Dados de teste removidos")
            
        else:
            print("❌ Falha na inserção")
            print(f"Erro: {result}")
            
    except Exception as e:
        print(f"❌ Erro na conexão com Supabase: {e}")
        print(f"Tipo do erro: {type(e)}")
        import traceback
        print(f"Traceback completo: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    test_supabase_connection()