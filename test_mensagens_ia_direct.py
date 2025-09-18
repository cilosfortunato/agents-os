#!/usr/bin/env python3
"""
Teste direto para verificar se as mensagens estão sendo salvas na tabela mensagens_ia
"""

import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def test_mensagens_ia():
    """Testa inserção e consulta direta na tabela mensagens_ia"""
    print("🔍 TESTE DIRETO DA TABELA MENSAGENS_IA")
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
        
        # Dados de teste
        test_data = {
            "user_id": "test_user_123",
            "session_id": str(uuid.uuid4()),
            "agent_id": "test_agent_456",
            "user_message": "Teste de mensagem do usuário",
            "agent_response": "Teste de resposta do agente"
        }
        
        print(f"\n📝 Inserindo dados de teste:")
        print(f"   User ID: {test_data['user_id']}")
        print(f"   Session ID: {test_data['session_id']}")
        print(f"   Agent ID: {test_data['agent_id']}")
        
        # Tenta inserir na tabela mensagens_ia
        result = supabase.table("mensagens_ia").insert(test_data).execute()
        
        if result.data:
            print("✅ Inserção bem-sucedida!")
            print(f"   ID gerado: {result.data[0]['id']}")
        else:
            print("❌ Falha na inserção - sem dados retornados")
            
        # Tenta consultar os dados inseridos
        print(f"\n🔍 Consultando dados por user_id...")
        query_result = supabase.table("mensagens_ia")\
            .select("*")\
            .eq("user_id", test_data['user_id'])\
            .execute()
            
        if query_result.data:
            print(f"✅ Consulta bem-sucedida! Encontrados {len(query_result.data)} registros")
            for record in query_result.data:
                print(f"   - ID: {record['id']}")
                print(f"   - Mensagem: {record['user_message']}")
                print(f"   - Resposta: {record['agent_response']}")
                print(f"   - Criado em: {record['created_at']}")
        else:
            print("❌ Nenhum registro encontrado na consulta")
            
        # Tenta consultar todos os registros da tabela
        print(f"\n📊 Consultando todos os registros da tabela...")
        all_records = supabase.table("mensagens_ia")\
            .select("*")\
            .limit(10)\
            .execute()
            
        if all_records.data:
            print(f"✅ Total de registros na tabela: {len(all_records.data)}")
            for i, record in enumerate(all_records.data[:3]):  # Mostra apenas os 3 primeiros
                print(f"   {i+1}. User: {record['user_id']}, Mensagem: {record['user_message'][:50]}...")
        else:
            print("❌ Tabela está vazia")
            
        # Limpa o registro de teste
        print(f"\n🧹 Limpando registro de teste...")
        delete_result = supabase.table("mensagens_ia")\
            .delete()\
            .eq("user_id", test_data['user_id'])\
            .execute()
            
        if delete_result.data:
            print("✅ Registro de teste removido com sucesso")
        else:
            print("⚠️  Nenhum registro foi removido (pode já ter sido removido)")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mensagens_ia()