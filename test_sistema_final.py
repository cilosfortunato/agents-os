#!/usr/bin/env python3
"""
Teste final do sistema AgentOS com OpenAI direto
"""

from dotenv import load_dotenv
import os
load_dotenv()

def test_sistema_completo():
    """Teste completo do sistema"""
    try:
        from agents import create_custom_agent, get_agent_by_name
        
        print('=== Teste do Sistema Completo ===')
        
        # Criar agente
        print('1. Criando agente...')
        agent_info = create_custom_agent(
            name='teste-openai-final',
            role='Assistente de teste',
            instructions=['Você é um assistente útil que responde de forma concisa.'],
            user_id='test-user',
            model={
                'provider': 'openai',
                'name': 'gpt-4o-mini'
            }
        )
        print(f'Agente criado: {agent_info}')
        
        # Verificar se agente foi criado
        print('\n2. Verificando agente criado...')
        agent = get_agent_by_name('teste-openai-final', 'test-user')
        print(f'Agente encontrado: {agent is not None}')
        
        if agent:
            print(f'Tipo do agente: {type(agent)}')
            if hasattr(agent, 'model'):
                print(f'Modelo do agente: {agent.model}')
            
            # Testar execução direta
            print('\n3. Testando execução direta...')
            response = agent.run('Olá! Como você está?')
            print(f'Resposta: {response}')
            
            # Verificar se está usando OpenAI
            if hasattr(agent, 'model') and hasattr(agent.model, 'base_url'):
                print(f'Base URL: {agent.model.base_url}')
                using_openai = 'api.openai.com' in agent.model.base_url
                print(f'Usando OpenAI diretamente: {using_openai}')
                
                if using_openai:
                    print('✅ SUCESSO: Sistema configurado para usar OpenAI diretamente!')
                else:
                    print('⚠️  AVISO: Sistema ainda usando OpenRouter')
        
        print('\n✅ Teste concluído com sucesso!')
        return True
        
    except Exception as e:
        print(f'❌ Erro no teste: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sistema_completo()