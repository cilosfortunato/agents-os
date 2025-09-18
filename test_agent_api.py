#!/usr/bin/env python3
"""
Teste simples para verificar a API correta do agente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agno.agent import Agent
from agno.models.openai import OpenAIChat

def test_agent_api():
    """Testa diferentes formas de chamar o agente"""
    print("🤖 TESTE DA API DO AGENTE")
    print("=" * 40)
    
    # Configura o modelo
    modelo_llm = OpenAIChat(
        id="gpt-4o-mini",
        temperature=0.7
    )
    
    # Template simples
    prompt_template = """Você é um assistente útil.
    
Pergunta: {message}

Responda de forma clara e concisa."""
    
    # Cria o agente
    agente = Agent(
        name="Assistente Teste",
        model=modelo_llm,
        prompt_template=prompt_template,
        role="Assistente útil"
    )
    
    print("✅ Agente criado com sucesso")
    
    # Testa diferentes formas de executar
    test_message = "Olá, como você está?"
    
    print(f"\n🔍 Testando com message='{test_message}'")
    try:
        resposta1 = agente.run(message=test_message)
        print(f"✅ Sucesso com message: {resposta1}")
    except Exception as e:
        print(f"❌ Erro com message: {e}")
    
    print(f"\n🔍 Testando com input='{test_message}'")
    try:
        resposta2 = agente.run(input=test_message)
        print(f"✅ Sucesso com input: {resposta2}")
    except Exception as e:
        print(f"❌ Erro com input: {e}")
    
    print(f"\n🔍 Testando sem parâmetros nomeados")
    try:
        resposta3 = agente.run(test_message)
        print(f"✅ Sucesso sem nome: {resposta3}")
    except Exception as e:
        print(f"❌ Erro sem nome: {e}")

if __name__ == "__main__":
    test_agent_api()