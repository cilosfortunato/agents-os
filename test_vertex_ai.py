#!/usr/bin/env python3
"""Teste direto do VertexAIClient para verificar se está funcionando"""

import os
from dotenv import load_dotenv
from vertex_ai_client import VertexAIClient

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da Google AI API
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ")

def test_vertex_ai_client():
    """Testa o VertexAIClient diretamente"""
    print("Iniciando teste do VertexAIClient...")
    
    try:
        # Inicializa o cliente
        client = VertexAIClient(
            api_key=GOOGLE_AI_API_KEY
        )
        print(f"Cliente inicializado com sucesso!")
        print(f"API Key configurada: {GOOGLE_AI_API_KEY[:20]}...")
        
        # Teste simples
        test_message = "Olá! Como você está?"
        print(f"\nTestando com mensagem: '{test_message}'")
        
        messages = [{"role": "user", "content": test_message}]
        result = client.generate_content(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        print("\n=== RESULTADO ===")
        print(f"Texto: {result.get('text', 'N/A')}")
        print(f"Modelo: {result.get('model', 'N/A')}")
        print(f"Usage: {result.get('usage', {})}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        print(f"Traceback completo:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_vertex_ai_client()
    if success:
        print("\n✅ Teste do VertexAIClient passou!")
    else:
        print("\n❌ Teste do VertexAIClient falhou!")