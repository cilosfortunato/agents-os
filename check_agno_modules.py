#!/usr/bin/env python3
"""
Verifica quais módulos estão disponíveis no Agno
"""

print("=== Verificando módulos do Agno ===")

# Teste 1: Módulos base
try:
    import agno.models
    print("✅ agno.models disponível")
    print(f"   Conteúdo: {dir(agno.models)}")
except Exception as e:
    print(f"❌ agno.models: {e}")

# Teste 2: OpenRouter
try:
    from agno.models.openrouter import OpenAIChat
    print("✅ agno.models.openrouter.OpenAIChat disponível")
except Exception as e:
    print(f"❌ agno.models.openrouter.OpenAIChat: {e}")

# Teste 3: OpenAI nativo
try:
    from agno.models.openai import OpenAIChat
    print("✅ agno.models.openai.OpenAIChat disponível")
except Exception as e:
    print(f"❌ agno.models.openai.OpenAIChat: {e}")

# Teste 4: Google/Gemini
try:
    from agno.models.google import Gemini
    print("✅ agno.models.google.Gemini disponível")
except Exception as e:
    print(f"❌ agno.models.google.Gemini: {e}")

# Teste 5: Verificar se OpenRouterModel pode ser usado para OpenAI
try:
    from agno.models.openrouter import OpenRouterModel
    print("✅ agno.models.openrouter.OpenRouterModel disponível")
except Exception as e:
    print(f"❌ agno.models.openrouter.OpenRouterModel: {e}")

print("\n=== Conclusão ===")
print("Parece que o Agno só tem OpenRouter disponível.")
print("Vamos usar OpenRouterModel para ambos OpenAI e Gemini.")