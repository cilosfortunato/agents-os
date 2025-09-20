#!/usr/bin/env python3
"""
Debug do endpoint de chat
"""

import os
import sys
from supabase_service import SupabaseService
from dual_memory_service import DualMemoryService
from vertex_ai_client_new import VertexAIClientNew

# Configuração
supabase_service = SupabaseService()
dual_memory_service = DualMemoryService()

# Cliente Vertex AI
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

def execute_agent_with_memory(query: str, user_id: str, agent_data: dict, memory_context: dict):
    """Executa agente com contexto de memória dupla usando OpenAI ou Vertex AI"""
    try:
        print(f"[DEBUG] Executando agente com memória")
        print(f"[DEBUG] Agent data: {agent_data}")
        print(f"[DEBUG] Memory context: {memory_context}")
        
        system_prompt = f"""Você é {agent_data["role"]}.

INSTRUÇÕES:
{chr(10).join(agent_data["instructions"])}

CONTEXTO DA SESSÃO ATUAL:
{memory_context.get("session_context", "Nova sessão")}

CONTEXTO ENRIQUECIDO (MEMÓRIAS RELEVANTES):
{memory_context.get("enriched_context", "Nenhum contexto adicional")}

HISTÓRICO RELACIONADO:
{memory_context.get("search_context", "Nenhum histórico relacionado")}

Responda de forma natural, considerando todo o contexto acima. Se houver informações contraditórias, priorize o contexto da sessão atual."""
        
        model_id = (agent_data.get("model") or "gemini-2.5-flash").replace("openai/", "")
        
        print(f"[DEBUG] Modelo detectado: {model_id}")
        print(f"[DEBUG] É modelo Vertex AI? {_is_vertex_ai_model(model_id)}")
        
        # Detecta se deve usar Vertex AI
        if _is_vertex_ai_model(model_id):
            print("[DEBUG] Usando Vertex AI...")
            result = _complete_with_vertex_ai(
                system_prompt=system_prompt,
                user_query=query,
                model_id=model_id,
                temperature=0.7,
                max_tokens=1000,
            )
            return {
                "text": result["text"],
                "usage": result["usage"]
            }
        else:
            print("[DEBUG] Modelo não é Vertex AI - usando OpenAI")
            # Aqui deveria usar OpenAI, mas vamos simular um erro
            return {
                "text": "Modelo não é Vertex AI",
                "usage": {"input_tokens": 0, "output_tokens": 0, "model": model_id}
            }
            
    except Exception as e:
        print(f"[DEBUG] Erro em execute_agent_with_memory: {e}")
        import traceback
        traceback.print_exc()
        return {
            "text": f"Desculpe, ocorreu um erro ao processar sua solicitação com memória. Erro: {str(e)}",
            "usage": {"input_tokens": 0, "output_tokens": 0, "model": "error"}
        }

def test_chat_endpoint():
    """Testa o fluxo do endpoint de chat"""
    print("=== Debug do Endpoint de Chat ===")
    
    # Simula dados da requisição
    message = "Qual é a capital do Brasil?"
    user_id = "test-user-123"
    agent_name = "Especialista em Produtos"
    session_id = "test-session-chat"
    
    try:
        # 1. Busca agentes no Supabase
        print("\n1. Buscando agentes no Supabase...")
        agents = supabase_service.list_all_agents()
        print(f"[DEBUG] Encontrados {len(agents)} agentes")
        
        # 2. Procura por um agente com nome similar ou usa o primeiro disponível
        agent_data = None
        for agent in agents:
            if agent_name.lower() in agent.get("name", "").lower():
                agent_data = agent
                break
        
        # Se não encontrou, usa o primeiro agente disponível
        if not agent_data and agents:
            agent_data = agents[0]
            
        if not agent_data:
            print("❌ Nenhum agente encontrado")
            return
            
        print(f"[DEBUG] Agente selecionado: {agent_data.get('name')} (ID: {agent_data.get('id')})")
        print(f"[DEBUG] Modelo do agente: {agent_data.get('model')}")
        
        # 3. Busca contexto de memória
        print("\n2. Buscando contexto de memória...")
        try:
            memory_context = dual_memory_service.get_complete_context(
                user_id=user_id,
                session_id=session_id,
                query=message
            )
            print(f"[DEBUG] Contexto de memória obtido")
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar memória: {e}")
            memory_context = {
                "session_context": "",
                "enriched_context": "",
                "search_context": ""
            }
        
        # 4. Executa agente com contexto
        print("\n3. Executando agente...")
        agent_result = execute_agent_with_memory(message, user_id, agent_data, memory_context)
        
        print(f"\n=== Resultado Final ===")
        print(f"Texto: {agent_result['text']}")
        print(f"Usage: {agent_result['usage']}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_endpoint()