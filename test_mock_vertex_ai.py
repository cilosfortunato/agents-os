#!/usr/bin/env python3
"""
Teste do mock do VertexAIClient
"""
import os
from dotenv import load_dotenv
from vertex_ai_client_mock import VertexAIClientMock

# Carrega variáveis de ambiente
load_dotenv()

def test_vertex_ai_mock():
    """Testa o mock do VertexAIClient"""
    print("=== Teste do Mock VertexAIClient ===")
    
    # Obtém a API key do ambiente
    api_key = os.getenv("GOOGLE_AI_API_KEY", "mock_key")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    try:
        # Inicializa o cliente mock
        client = VertexAIClientMock(api_key=api_key)
        print("✅ Cliente mock inicializado com sucesso")
        
        # Testa diferentes tipos de perguntas
        test_prompts = [
            "Olá! Como você está?",
            "Qual é a garantia do produto?",
            "Como ativar o modo noturno?",
            "Quanto tempo dura a bateria?",
            "Como reiniciar o dispositivo?",
            "Pergunta genérica sobre o produto"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Teste {i}: {prompt} ---")
            
            # Gera conteúdo
            result = client.generate_content(prompt)
            
            # Verifica se a resposta tem a estrutura esperada
            if "candidates" in result and len(result["candidates"]) > 0:
                response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                usage = result.get("usageMetadata", {})
                
                print(f"✅ Resposta: {response_text}")
                print(f"📊 Tokens: {usage.get('totalTokenCount', 0)} total")
            else:
                print(f"❌ Resposta inválida: {result}")
                return False
        
        # Testa listagem de modelos
        print(f"\n--- Teste de Modelos ---")
        models = client.list_models()
        print(f"✅ Modelos disponíveis: {len(models)}")
        for model in models:
            print(f"  - {model['displayName']}: {model['description']}")
        
        print(f"\n✅ Todos os testes do mock passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do mock: {e}")
        return False

if __name__ == "__main__":
    success = test_vertex_ai_mock()
    
    if success:
        print("\n🎉 Mock do VertexAIClient está funcionando perfeitamente!")
    else:
        print("\n💥 Falha no teste do mock!")