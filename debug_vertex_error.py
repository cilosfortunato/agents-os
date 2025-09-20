#!/usr/bin/env python3
"""
Script para debugar o erro específico do Vertex AI
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vertex_ai_client_new import VertexAIClientNew

def test_vertex_ai_direct():
    """Testa o cliente Vertex AI diretamente"""
    try:
        print("=== Teste Direto do Cliente Vertex AI ===")
        
        # Verifica se a chave está configurada
        api_key = os.getenv("GOOGLE_CLOUD_API_KEY")
        if not api_key:
            print("❌ GOOGLE_CLOUD_API_KEY não encontrada no ambiente")
            return
        
        print(f"✅ GOOGLE_CLOUD_API_KEY encontrada: {api_key[:20]}...")
        
        # Instancia o cliente
        client = VertexAIClientNew()
        print("✅ Cliente Vertex AI instanciado com sucesso")
        
        # Testa geração de conteúdo
        messages = [
            {"role": "user", "content": "Qual é a capital do Brasil?"}
        ]
        
        print("Enviando mensagem para o Vertex AI...")
        result = client.generate_content(
            messages=messages,
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=1000,
            system_instruction="Você é um assistente útil."
        )
        
        print("✅ Resposta recebida:")
        print(f"Texto: {result['text']}")
        print(f"Usage: {result['usage']}")
        
    except Exception as e:
        print(f"❌ Erro no teste direto: {str(e)}")
        import traceback
        traceback.print_exc()

def test_model_detection():
    """Testa a detecção de modelo"""
    try:
        print("\n=== Teste de Detecção de Modelo ===")
        
        # Importa a função de detecção
        from api_completa import _is_vertex_ai_model
        
        test_models = [
            "gemini-2.5-flash",
            "gemini-pro", 
            "gpt-4",
            "openai/gpt-3.5-turbo"
        ]
        
        for model in test_models:
            is_vertex = _is_vertex_ai_model(model)
            print(f"Modelo: {model} -> Vertex AI: {is_vertex}")
            
    except Exception as e:
        print(f"❌ Erro no teste de detecção: {str(e)}")

def test_complete_with_vertex():
    """Testa a função _complete_with_vertex_ai"""
    try:
        print("\n=== Teste da Função _complete_with_vertex_ai ===")
        
        # Importa a função
        from api_completa import _complete_with_vertex_ai
        
        result = _complete_with_vertex_ai(
            system_prompt="Você é um assistente útil.",
            user_query="Qual é a capital do Brasil?",
            model_id="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=1000
        )
        
        print("✅ Resultado da função:")
        print(f"Texto: {result['text']}")
        print(f"Usage: {result['usage']}")
        
    except Exception as e:
        print(f"❌ Erro na função _complete_with_vertex_ai: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vertex_ai_direct()
    test_model_detection()
    test_complete_with_vertex()