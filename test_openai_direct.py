#!/usr/bin/env python3
"""
Teste para usar OpenAI diretamente com OpenRouterModel
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from agno.models.openrouter import OpenRouterModel
    
    # Teste 1: Usando OpenRouter com modelo OpenAI
    print("🧪 Teste 1: OpenRouterModel com modelo OpenAI")
    model1 = OpenRouterModel(
        model_id="openai/gpt-4o-mini",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    print(f"✅ Modelo 1 criado: {model1}")
    
    # Teste 2: Verificando se podemos usar API OpenAI diretamente
    print("\n🧪 Teste 2: Verificando parâmetros do OpenRouterModel")
    print(f"Parâmetros disponíveis: {dir(model1)}")
    
    # Teste 3: Tentando usar com API OpenAI
    print("\n🧪 Teste 3: Tentando usar OpenAI API Key")
    try:
        model2 = OpenRouterModel(
            model_id="gpt-4o-mini",  # Sem prefixo openai/
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1"  # URL da OpenAI
        )
        print(f"✅ Modelo 2 criado: {model2}")
    except Exception as e:
        print(f"❌ Erro no modelo 2: {e}")
        
    # Teste 4: Verificando assinatura do construtor
    print("\n🧪 Teste 4: Verificando assinatura do construtor")
    import inspect
    sig = inspect.signature(OpenRouterModel.__init__)
    print(f"Assinatura: {sig}")
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()