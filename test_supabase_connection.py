#!/usr/bin/env python3
"""
Teste simples para verificar a conexão com o Supabase
"""

from supabase_service import supabase_service

def test_supabase_connection():
    """Testa a conexão básica com o Supabase"""
    print("🔍 Testando conexão com Supabase...")
    
    try:
        # Testa listagem de agentes
        agents = supabase_service.list_all_agents()
        print(f"✅ Agentes encontrados: {len(agents)}")
        
        if agents:
            agent = agents[0]
            print(f"Primeiro agente: {agent['name']} (ID: {agent['id']})")
            
            # Testa salvamento de mensagem na nova tabela
            print("\n📝 Testando salvamento de mensagem...")
            message_data = supabase_service.save_message(
                user_id="test_user_123",
                session_id="test_session_456", 
                agent_id=agent['id'],
                message="Teste de mensagem",
                response="Resposta de teste"
            )
            
            if message_data:
                print(f"✅ Mensagem salva com sucesso: {message_data['id']}")
                
                # Testa recuperação de mensagens da sessão
                print("\n🔍 Testando recuperação de mensagens...")
                messages = supabase_service.get_session_messages("test_session_456", 5)
                print(f"✅ Mensagens recuperadas: {len(messages)}")
                
            else:
                print("❌ Falha ao salvar mensagem")
                
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supabase_connection()