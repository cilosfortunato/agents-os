#!/usr/bin/env python3
"""
Teste para verificar os parâmetros corretos do agente AgentOS
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

try:
    from agno.agent import Agent
    from agno.models.openrouter import OpenRouterModel
    
    print("✅ Imports do AgentOS carregados com sucesso")
    
    # Cria modelo
    modelo = OpenRouterModel(
        model_id="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1"
    )
    
    # Cria agente simples
    agente = Agent(
        id="teste-params",
        name="Agente de Teste",
        model=modelo,
        prompt_template="Você é um assistente útil. Responda: {query}",
        role="Assistente"
    )
    
    print("✅ Agente criado com sucesso")
    
    # Testa diferentes parâmetros
    test_query = "Olá, como você está?"
    
    print("\n🔍 Testando parâmetros do agente.run()...")
    
    # Verifica assinatura do método run
    import inspect
    sig = inspect.signature(agente.run)
    print(f"📋 Assinatura do método run: {sig}")
    print(f"📋 Parâmetros aceitos: {list(sig.parameters.keys())}")
    
    # Testa com diferentes parâmetros
    try:
        print("\n🧪 Testando com 'query'...")
        resposta = agente.run(query=test_query)
        print(f"✅ Sucesso com 'query': {resposta}")
    except Exception as e:
        print(f"❌ Erro com 'query': {e}")
    
    try:
        print("\n🧪 Testando com 'input'...")
        resposta = agente.run(input=test_query)
        print(f"✅ Sucesso com 'input': {resposta}")
    except Exception as e:
        print(f"❌ Erro com 'input': {e}")
    
    try:
        print("\n🧪 Testando com 'message'...")
        resposta = agente.run(message=test_query)
        print(f"✅ Sucesso com 'message': {resposta}")
    except Exception as e:
        print(f"❌ Erro com 'message': {e}")
    
    try:
        print("\n🧪 Testando sem parâmetro nomeado...")
        resposta = agente.run(test_query)
        print(f"✅ Sucesso sem nome: {resposta}")
    except Exception as e:
        print(f"❌ Erro sem nome: {e}")

except ImportError as e:
    print(f"❌ Erro de import: {e}")
    print("🔄 Usando mock para teste...")
    
    class MockAgent:
        def run(self, **kwargs):
            return f"Mock response for: {kwargs}"
    
    agente = MockAgent()
    print(f"Mock test: {agente.run(query='test')}")

except Exception as e:
    print(f"❌ Erro geral: {e}")