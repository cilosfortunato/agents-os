#!/usr/bin/env python3
"""
Debug da detecção de modelo
"""

def _is_vertex_ai_model(model_id: str) -> bool:
    """Detecta se o modelo especificado é do Vertex AI (Gemini)"""
    vertex_models = ["gemini-2.5-flash", "gemini-pro", "gemini-flash", "google/gemini"]
    return any(vertex_model in model_id.lower() for vertex_model in vertex_models)

def test_model_detection():
    """Testa a detecção de modelos"""
    print("=== Debug da Detecção de Modelo ===")
    
    test_models = [
        "gemini-2.5-flash",
        "gemini-pro",
        "gemini-flash",
        "google/gemini",
        "gpt-4",
        "gpt-3.5-turbo",
        "openai/gpt-4"
    ]
    
    for model in test_models:
        is_vertex = _is_vertex_ai_model(model)
        print(f"Modelo: {model} -> Vertex AI: {is_vertex}")
    
    # Teste específico com dados do agente
    agent_data = {
        "model": "gemini-2.5-flash"
    }
    
    model_id = (agent_data.get("model") or "gemini-2.5-flash").replace("openai/", "")
    is_vertex = _is_vertex_ai_model(model_id)
    
    print(f"\nTeste com dados do agente:")
    print(f"Modelo original: {agent_data.get('model')}")
    print(f"Modelo processado: {model_id}")
    print(f"É Vertex AI: {is_vertex}")

if __name__ == "__main__":
    test_model_detection()