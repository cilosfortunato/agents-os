#!/usr/bin/env python3
"""
Debug da integração do novo cliente Vertex AI na API
"""

import os
from vertex_ai_client_new import VertexAIClientNew

# Simula exatamente o que a API faz
vertex_ai_client_new = VertexAIClientNew(
    api_key="AQ.Ab8RN6LDtoXn4cdQvG62dfzA2M6FozHfH6Tgb8EG4WaS78uc3g"
)

def _is_vertex_ai_model(model_id: str) -> bool:
    """Detecta se o modelo especificado é do Vertex AI (Gemini)"""
    vertex_models = ["gemini-2.5-flash", "gemini-pro", "gemini-flash", "google/gemini"]
    return any(vertex_model in model_id.lower() for vertex_model in vertex_models)

def _complete_with_vertex_ai(system_prompt: str, user_query: str, model_id: str, temperature: float = 0.7, max_tokens: int = 1000):
    """Completa usando Vertex AI e retorna resposta com metadados"""
    try:
        print(f"[DEBUG] Chamando Vertex AI com modelo: {model_id}")
        print(f"[DEBUG] System prompt: {system_prompt[:100]}...")
        print(f"[DEBUG] User query: {user_query}")
        
        # Prepara mensagens no formato correto
        messages = [
            {"role": "user", "content": f"{system_prompt}\n\nPERGUNTA DO USUÁRIO:\n{user_query}"}
        ]
        
        # Usa o novo cliente Vertex AI
        result = vertex_ai_client_new.generate_content(
            messages=messages,
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
            system_instruction=system_prompt
        )
        
        print(f"[DEBUG] Resultado do cliente: {result}")
        
        # O novo cliente já retorna no formato correto
        return {
            "text": result["text"],
            "usage": result["usage"]
        }
        
    except Exception as e:
        print(f"[DEBUG] Erro na função _complete_with_vertex_ai: {e}")
        import traceback
        traceback.print_exc()
        return {
            "text": f"Erro ao processar com Vertex AI: {str(e)}",
            "usage": {"input_tokens": 0, "output_tokens": 0, "model": model_id}
        }

def test_api_integration():
    """Testa a integração exatamente como a API faz"""
    print("=== Debug da Integração API ===")
    
    # Simula dados do agente
    agent_data = {
        "role": "Especialista em Produtos",
        "instructions": ["Responda de forma clara e objetiva", "Use informações precisas"],
        "model": "gemini-2.5-flash"
    }
    
    query = "Qual é a capital do Brasil?"
    user_id = "test-user-123"
    
    # Template de prompt para o agente (igual ao da API)
    prompt = (
        f"Você é um {agent_data['role']}.\n"
        f"Siga estas instruções:\n"
        f"{chr(10).join(agent_data['instructions'])}\n\n"
        f"Responda à pergunta do usuário de forma precisa e profissional."
    )
    
    # Modelo (remove prefixo openai/ se existir)
    model_id = (agent_data.get("model") or "gemini-2.5-flash").replace("openai/", "")
    
    print(f"[DEBUG] Modelo detectado: {model_id}")
    print(f"[DEBUG] É modelo Vertex AI? {_is_vertex_ai_model(model_id)}")
    
    # Detecta se deve usar Vertex AI
    if _is_vertex_ai_model(model_id):
        print("[DEBUG] Usando Vertex AI...")
        result = _complete_with_vertex_ai(
            system_prompt=prompt,
            user_query=query,
            model_id=model_id,
            temperature=0.7,
            max_tokens=1000,
        )
        print(f"[DEBUG] Resultado final: {result}")
        return {
            "text": result["text"],
            "usage": result["usage"]
        }
    else:
        print("[DEBUG] Modelo não é Vertex AI")
        return {
            "text": "Modelo não é Vertex AI",
            "usage": {"input_tokens": 0, "output_tokens": 0, "model": model_id}
        }

if __name__ == "__main__":
    test_api_integration()