#!/usr/bin/env python3

# Teste de imports do Agno
print("Testando imports do Agno...")

try:
    from agno import Agent
    print("✅ Agent import OK")
except Exception as e:
    print(f"❌ Agent error: {e}")

try:
    from agno.models.openai import OpenAIChat
    print("✅ OpenAIChat import OK")
except Exception as e:
    print(f"❌ OpenAIChat error: {e}")

try:
    from agno.os import AgentOS
    print("✅ AgentOS import OK")
except Exception as e:
    print(f"❌ AgentOS error: {e}")

try:
    from agno.tools.duckduckgo import DuckDuckGoTools
    print("✅ DuckDuckGoTools import OK")
except Exception as e:
    print(f"❌ DuckDuckGoTools error: {e}")

try:
    from agno.models.openrouter import OpenRouterModel
    print("✅ OpenRouterModel import OK")
except Exception as e:
    print(f"❌ OpenRouterModel error: {e}")

print("\nVerificando estrutura do agno:")
import agno
print(f"Versão: {agno.__version__}")
print(f"Módulos disponíveis: {dir(agno)}")

print("\nVerificando agno.models:")
import agno.models
print(f"Modelos disponíveis: {dir(agno.models)}")