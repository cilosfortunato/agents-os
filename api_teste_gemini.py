#!/usr/bin/env python3
"""
API simplificada para teste do agente Gemini
Roda na porta 8000 especificamente para testes
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json

# Configurar variáveis de ambiente
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

# Importar Agno
try:
    from agno.agent import Agent
    from agno.models.openrouter import OpenRouterModel
    print("✅ Agno importado com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar Agno: {e}")
    exit(1)

app = FastAPI(
    title="API Teste Gemini",
    description="API simplificada para testar agentes Gemini",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chave de API
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

# Storage em memória para agentes
agents_storage = {}

# Modelos de dados
class AgentCreate(BaseModel):
    name: str
    description: str = ""
    instructions: str = ""
    model: str = "google/gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 1000

class ChatMessage(BaseModel):
    mensagem: str
    agent_id: str
    user_id: str = ""
    session_id: str = ""
    message_id: str = ""
    debounce: int = 1000
    cliente_id: str = ""
    id_conta: str = ""

# Autenticação
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")
    return x_api_key

def create_model(model_name: str = "google/gemini-pro"):
    """Cria um modelo usando OpenRouterModel"""
    try:
        return OpenRouterModel(
            model_id=model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1"
        )
    except Exception as e:
        print(f"Erro ao criar modelo {model_name}: {e}")
        return OpenRouterModel(
            model_id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1"
        )

@app.get("/health")
async def health_check():
    """Health check da API - sem autenticação para facilitar testes"""
    return {
        "status": "healthy",
        "agents": len(agents_storage),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agents")
async def create_agent(agent_data: AgentCreate, api_key: str = Depends(verify_api_key)):
    """Cria um novo agente"""
    try:
        agent_id = str(uuid.uuid4())
        
        # Criar modelo
        model = create_model(agent_data.model)
        
        # Criar agente
        agent = Agent(
            model=model,
            instructions=agent_data.instructions or "Você é um assistente útil."
        )
        
        # Salvar no storage
        agent_info = {
            "id": agent_id,
            "name": agent_data.name,
            "description": agent_data.description,
            "model": agent_data.model,
            "instructions": agent_data.instructions,
            "temperature": agent_data.temperature,
            "max_tokens": agent_data.max_tokens,
            "created_at": datetime.now().isoformat(),
            "agent_instance": agent
        }
        
        agents_storage[agent_id] = agent_info
        
        # Retornar info sem a instância do agente
        response = agent_info.copy()
        del response["agent_instance"]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(e)}")

@app.get("/agents")
async def list_agents(api_key: str = Depends(verify_api_key)):
    """Lista todos os agentes"""
    agents_list = []
    for agent_id, agent_info in agents_storage.items():
        agent_copy = agent_info.copy()
        if "agent_instance" in agent_copy:
            del agent_copy["agent_instance"]
        agents_list.append(agent_copy)
    
    return {"agents": agents_list}

@app.post("/chat")
async def chat_endpoint(messages: List[ChatMessage], api_key: str = Depends(verify_api_key)):
    """Endpoint de chat com agentes"""
    try:
        if not messages:
            raise HTTPException(status_code=400, detail="Nenhuma mensagem fornecida")
        
        message = messages[0]  # Pegar primeira mensagem
        
        # Verificar se agente existe
        if message.agent_id not in agents_storage:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        agent_info = agents_storage[message.agent_id]
        agent = agent_info["agent_instance"]
        
        # Executar chat
        response = agent.run(message.mensagem)
        
        # Simular usage (já que não temos acesso aos tokens reais)
        usage = {
            "input_tokens": len(message.mensagem.split()),
            "output_tokens": len(str(response).split()),
            "model": agent_info["model"]
        }
        
        return {
            "messages": [str(response)],
            "transferir": False,
            "session_id": message.session_id,
            "user_id": message.user_id,
            "agent_id": message.agent_id,
            "custom": [],
            "agent_usage": usage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando API de Teste Gemini na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)