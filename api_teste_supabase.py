#!/usr/bin/env python3
"""
API de teste modificada para carregar agentes do Supabase
Baseada na api_teste_gemini.py mas conecta ao Supabase real
"""

import os
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Importa o serviço do Supabase
from supabase_service import SupabaseService

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Instância do Supabase
supabase_service = SupabaseService()

# Configuração do FastAPI
app = FastAPI(
    title="API de Teste com Supabase",
    description="API para testar agentes carregados do Supabase",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de dados
class AgentCreate(BaseModel):
    name: str
    role: str = "Assistente"
    instructions: List[str] = []
    model: str = "gemini-2.5-flash"
    provider: str = "gemini"
    account_id: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    agent_id: str
    user_id: str = "default_user"
    session_id: Optional[str] = None

class MessageRequest(BaseModel):
    mensagem: str
    agent_id: str
    user_id: str
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    cliente_id: str = ""
    id_conta: str = ""
    debounce: int = 0

# Função de autenticação
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")
    return x_api_key

# Função para criar modelo (mock)
def create_model(model_name: str = "gemini-2.5-flash"):
    """Cria um modelo mock para testes"""
    class MockModel:
        def __init__(self, name):
            self.name = name
        
        def run(self, input_text: str) -> str:
            # Simula resposta do modelo
            responses = [
                f"Olá! Sou o assistente {self.name}. Como posso ajudar você hoje?",
                f"Entendi sua pergunta: '{input_text}'. Vou fazer o meu melhor para ajudar!",
                f"Baseado na sua mensagem, posso fornecer informações sobre nossos produtos e serviços.",
                f"Obrigado por entrar em contato! Estou aqui para esclarecer suas dúvidas."
            ]
            import random
            return random.choice(responses)
    
    return MockModel(model_name)

# Endpoints

@app.get("/health")
async def health_check():
    """Verifica o status da API e quantos agentes estão disponíveis no Supabase"""
    try:
        agents = supabase_service.list_all_agents()
        agent_count = len(agents) if agents else 0
        
        return {
            "status": "healthy",
            "agents": agent_count,
            "timestamp": datetime.now().isoformat(),
            "supabase_connected": True
        }
    except Exception as e:
        return {
            "status": "healthy",
            "agents": 0,
            "timestamp": datetime.now().isoformat(),
            "supabase_connected": False,
            "error": str(e)
        }

@app.post("/agents")
async def create_agent(agent: AgentCreate, api_key: str = Depends(verify_api_key)):
    """Cria um novo agente no Supabase"""
    try:
        # Cria agente no Supabase
        new_agent = supabase_service.create_agent(
            name=agent.name,
            role=agent.role,
            instructions=agent.instructions,
            model=agent.model,
            provider=agent.provider,
            account_id=agent.account_id or str(uuid.uuid4())
        )
        
        return {
            "message": "Agente criado com sucesso",
            "agent": new_agent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(e)}")

@app.get("/agents")
async def list_agents(api_key: str = Depends(verify_api_key)):
    """Lista todos os agentes do Supabase"""
    try:
        agents = supabase_service.list_all_agents()
        return {
            "agents": agents,
            "total": len(agents) if agents else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar agentes: {str(e)}")

@app.post("/chat")
async def chat_with_agent(request: ChatMessage, api_key: str = Depends(verify_api_key)):
    """Chat com agente específico carregado do Supabase"""
    try:
        # Busca o agente no Supabase
        agent = supabase_service.get_agent(request.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        # Cria modelo mock
        model = create_model(agent.get("model", "gemini-2.5-flash"))
        
        # Gera resposta
        response = model.run(request.message)
        
        # Simula usage
        usage = {
            "input_tokens": len(request.message.split()),
            "output_tokens": len(response.split()),
            "model": agent.get("model", "gemini-2.5-flash")
        }
        
        # Salva mensagem no Supabase (se disponível)
        try:
            session_id = request.session_id or str(uuid.uuid4())
            supabase_service.save_message(
                agent_id=request.agent_id,
                user_id=request.user_id,
                session_id=session_id,
                user_message=request.message,
                agent_response=response,
                usage=usage
            )
        except Exception as e:
            print(f"Aviso: Não foi possível salvar mensagem: {e}")
        
        return {
            "response": response,
            "agent_id": request.agent_id,
            "user_id": request.user_id,
            "session_id": session_id,
            "usage": usage,
            "agent_name": agent.get("name", "Agente")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")

@app.post("/v1/messages")
async def send_message_to_agent(request: MessageRequest, api_key: str = Depends(verify_api_key)):
    """Endpoint compatível com o formato da API completa"""
    try:
        # Busca o agente no Supabase
        agent = supabase_service.get_agent(request.agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        # Cria modelo mock
        model = create_model(agent.get("model", "gemini-2.5-flash"))
        
        # Gera resposta
        response = model.run(request.mensagem)
        
        # Simula usage
        usage = {
            "input_tokens": len(request.mensagem.split()),
            "output_tokens": len(response.split()),
            "model": agent.get("model", "gemini-2.5-flash")
        }
        
        # Gera session_id se não fornecido
        session_id = request.session_id or str(uuid.uuid4())
        
        # Salva mensagem no Supabase (se disponível)
        try:
            supabase_service.save_message(
                agent_id=request.agent_id,
                user_id=request.user_id,
                session_id=session_id,
                user_message=request.mensagem,
                agent_response=response,
                usage=usage
            )
        except Exception as e:
            print(f"Aviso: Não foi possível salvar mensagem: {e}")
        
        return {
            "messages": [response],
            "transferir": False,
            "session_id": session_id,
            "user_id": request.user_id,
            "agent_id": request.agent_id,
            "custom": [],
            "agent_usage": usage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str, api_key: str = Depends(verify_api_key)):
    """Busca um agente específico no Supabase"""
    try:
        agent = supabase_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        return agent
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar agente: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API de Teste com Supabase...")
    print("📊 Carregando agentes do Supabase...")
    
    # Testa conexão com Supabase
    try:
        agents = supabase_service.list_all_agents()
        print(f"✅ {len(agents) if agents else 0} agentes carregados do Supabase")
    except Exception as e:
        print(f"⚠️  Erro ao conectar com Supabase: {e}")
    
    print("🌐 API disponível em: http://localhost:8000")
    print("📚 Documentação em: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)