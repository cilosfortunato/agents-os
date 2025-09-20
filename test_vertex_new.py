"""
Teste do novo cliente Vertex AI usando google-genai
"""

import os
from vertex_ai_client_new import VertexAIClientNew, get_vertex_ai_client_new

def test_vertex_ai_client_new():
    """Testa o novo cliente Vertex AI"""
    print("=== Teste do Novo Cliente Vertex AI (google-genai) ===")
    
    # Configurar API Key
    api_key = "AQ.Ab8RN6LDtoXn4cdQvG62dfzA2M6FozHfH6Tgb8EG4WaS78uc3g"
    os.environ["GOOGLE_CLOUD_API_KEY"] = api_key
    
    try:
        # Teste 1: Inicialização
        print("\n1. Testando inicialização...")
        client = VertexAIClientNew(api_key=api_key)
        print(f"✓ Cliente inicializado com modelo padrão: {client.default_model}")
        
        # Teste 2: Teste de conexão
        print("\n2. Testando conexão...")
        connection_result = client.test_connection()
        print(f"Status: {connection_result['status']}")
        print(f"Mensagem: {connection_result['message']}")
        
        if connection_result['status'] == 'success':
            print("✓ Conexão estabelecida com sucesso")
        else:
            print("✗ Falha na conexão")
            return False
        
        # Teste 3: Geração de conteúdo simples
        print("\n3. Testando geração de conteúdo...")
        result = client.generate_content(
            prompt="Olá! Como você está?",
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"Resposta: {result['text'][:200]}...")
        print(f"Usage: {result['usage']}")
        
        if result['text'] and "Erro" not in result['text']:
            print("✓ Geração de conteúdo funcionando")
        else:
            print("✗ Erro na geração de conteúdo")
            return False
        
        # Teste 4: Geração com mensagens
        print("\n4. Testando geração com formato de mensagens...")
        messages = [
            {"role": "user", "content": "Qual é a capital do Brasil?"}
        ]
        
        result = client.generate_content(
            messages=messages,
            temperature=0.3,
            max_tokens=50
        )
        
        print(f"Resposta: {result['text']}")
        print(f"Usage: {result['usage']}")
        
        if result['text'] and "Erro" not in result['text']:
            print("✓ Geração com mensagens funcionando")
        else:
            print("✗ Erro na geração com mensagens")
            return False
        
        # Teste 5: Geração com system instruction
        print("\n5. Testando geração com system instruction...")
        result = client.generate_content(
            prompt="Conte uma piada",
            system_instruction="Você é um comediante profissional. Seja engraçado mas respeitoso.",
            temperature=0.8,
            max_tokens=100
        )
        
        print(f"Resposta: {result['text']}")
        print(f"Usage: {result['usage']}")
        
        if result['text'] and "Erro" not in result['text']:
            print("✓ Geração com system instruction funcionando")
        else:
            print("✗ Erro na geração com system instruction")
            return False
        
        # Teste 6: Streaming (teste básico)
        print("\n6. Testando geração em streaming...")
        try:
            stream_text = ""
            for chunk in client.generate_content_stream(
                prompt="Conte até 5",
                max_tokens=50
            ):
                stream_text += chunk
                print(chunk, end="", flush=True)
            
            print(f"\n✓ Streaming funcionando - Texto completo: {stream_text}")
        except Exception as e:
            print(f"\n✗ Erro no streaming: {e}")
            return False
        
        # Teste 7: Singleton
        print("\n7. Testando função singleton...")
        client2 = get_vertex_ai_client_new()
        if client2 is not None:
            print("✓ Função singleton funcionando")
        else:
            print("✗ Erro na função singleton")
            return False
        
        print("\n=== TODOS OS TESTES PASSARAM! ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Erro geral nos testes: {e}")
        return False

if __name__ == "__main__":
    success = test_vertex_ai_client_new()
    if success:
        print("\n🎉 Novo cliente Vertex AI está funcionando perfeitamente!")
    else:
        print("\n❌ Há problemas com o novo cliente Vertex AI.")