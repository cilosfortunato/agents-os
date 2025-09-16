#!/usr/bin/env python3
"""
Teste de importações do Agno
"""

try:
    from agno import Agent
    print("✅ Agent import OK")
except Exception as e:
    print(f"❌ Agent error: {e}")

try:
    from agno.models import OpenRouterModel
    print("✅ OpenRouterModel import OK")
except Exception as e:
    print(f"❌ OpenRouterModel error: {e}")

try:
    from agno.os import AgentOS
    print("✅ AgentOS import OK")
except Exception as e:
    print(f"❌ AgentOS error: {e}")

try:
    from agno.tools import DuckDuckGoTools
    print("✅ DuckDuckGoTools import OK")
except Exception as e:
    print(f"❌ DuckDuckGoTools error: {e}")

print("\n--- Estrutura do agno ---")
import agno
print(f"Agno version: {getattr(agno, '__version__', 'unknown')}")
print(f"Agno modules: {dir(agno)}")

print("\n--- Estrutura do agno.models ---")
import agno.models
print(f"Models: {dir(agno.models)}")