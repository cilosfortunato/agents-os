#!/usr/bin/env python3
"""
Debug do novo cliente Vertex AI
"""

import os
from vertex_ai_client_new import VertexAIClientNew

def test_vertex_client():
    """Testa o novo cliente Vertex AI diretamente"""
    print("=== Debug do Novo Cliente Vertex AI ===")
    
    try:
        # Inicializa o cliente
        client = VertexAIClientNew(
            api_key="AQ.Ab8RN6LDtoXn4cdQvG62dfzA2M6FozHfH6Tgb8EG4WaS78uc3g"
        )
        print("✓ Cliente inicializado com sucesso")
        
        # Testa geração de conteúdo
        messages = [
            {"role": "user", "content": "Qual é a capital do Brasil?"}
        ]
        
        print("\n1. Testando geração de conteúdo...")
        result = client.generate_content(
            messages=messages,
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=100,
            system_instruction="Você é um assistente útil."
        )
        
        print(f"Resultado: {result}")
        print(f"Texto: {result.get('text', 'N/A')}")
        print(f"Usage: {result.get('usage', 'N/A')}")
        
        if result.get('text'):
            print("✓ Geração de conteúdo funcionando!")
        else:
            print("❌ Problema na geração de conteúdo")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vertex_client()