#!/usr/bin/env python3

# Teste de importação do Agno
print("Testando importação do Agno...")

try:
    from agno.agent import Agent
    from agno.models.openrouter import OpenRouterModel
    from agno.tools.duckduckgo import DuckDuckGoTools
    print("✅ Agno importado com sucesso!")
    print(f"Agent: {Agent}")
    print(f"OpenRouterModel: {OpenRouterModel}")
    print(f"DuckDuckGoTools: {DuckDuckGoTools}")
    
    # Teste de criação do modelo
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OpenAI API Key disponível: {'Sim' if api_key else 'Não'}")
    
    if api_key:
        try:
            model = OpenRouterModel(
                model_id="openai/gpt-4o-mini",
                api_key=api_key
            )
            print(f"✅ Modelo OpenAI via OpenRouter criado: {model}")
        except Exception as e:
            print(f"❌ Erro ao criar modelo OpenAI: {e}")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")