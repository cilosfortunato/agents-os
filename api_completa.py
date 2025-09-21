#!/usr/bin/env python3
"""
API Completa com Sistema de Memórias Enriquecidas do Agno
Integra salvamento de mensagens e memórias contextuais usando a tabela message_history
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv
from dual_memory_optimized_service import DualMemoryOptimizedService

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicializar o serviço de memória dual otimizado
dual_memory_service = DualMemoryOptimizedService()

# Funções para integração com o serviço de memória dual otimizado
async def save_conversation(user_id: str, session_id: str, agent_id: str, user_message: str, agent_response: str) -> Dict[str, Any]:
    """Salva uma conversa completa na tabela mensagens_ia"""
    try:
        result = dual_memory_service.save_chat_message(
            user_id=user_id,
            session_id=session_id,
            agent_id=agent_id,
            user_message=user_message,
            agent_response=agent_response
        )
        
        print(f"Status do salvamento da conversa: {result.get('status', 'unknown')}")
        return result
                
    except Exception as e:
        print(f"Erro ao salvar conversa: {e}")
        return {"status": "error", "error": str(e)}

async def create_enriched_memory(user_id: str, session_id: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Cria uma memória enriquecida na tabela message_history"""
    try:
        result = dual_memory_service.create_enriched_memory(
            user_id=user_id,
            session_id=session_id,
            content=content,
            metadata=metadata or {}
        )
        
        print(f"Status da criação de memória enriquecida: {result.get('status', 'unknown')}")
        return result
                
    except Exception as e:
        print(f"Erro ao criar memória enriquecida: {e}")
        return {"status": "error", "error": str(e)}

async def list_enriched_memories(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Lista memórias enriquecidas do usuário"""
    try:
        memories = dual_memory_service.search_enriched_memories(
            user_id=user_id,
            limit=limit
        )
        
        print(f"✅ Encontradas {len(memories)} memórias enriquecidas para listagem")
        return memories
                
    except Exception as e:
        print(f"Erro ao listar memórias enriquecidas: {e}")
        return []

async def auto_enrich_conversation(user_id: str, session_id: str, user_message: str, agent_response: str):
    """Enriquece automaticamente a conversa criando uma síntese concisa"""
    try:
        memories = dual_memory_service.auto_enrich_conversation(
            user_id=user_id,
            session_id=session_id,
            user_message=user_message,
            agent_response=agent_response
        )
        
        print(f"✅ Criadas {len(memories)} memórias enriquecidas automaticamente")
        return {"status": "success", "memories": memories, "count": len(memories)}
                
    except Exception as e:
        print(f"Erro no enriquecimento automático: {e}")
        return {"status": "error", "error": str(e)}

# Modelos Pydantic
class MessageInput(BaseModel):
    mensagem: str
    agent_id: str
    debounce: int = 15000
    session_id: Optional[str] = None
    message_id: str
    cliente_id: str = ""
    user_id: str
    id_conta: str

class MessageOutput(BaseModel):
    messages: List[str]
    transferir: bool = False
    session_id: str
    user_id: str
    agent_id: str
    custom: List[Dict[str, str]] = []
    agent_usage: Dict[str, Any] = {}

class MemoryRequest(BaseModel):
    user_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryResponse(BaseModel):
    id: str
    user_id: str
    content: str
    metadata: Dict[str, Any]
    created_at: str

class MemoryListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int

# Inicializar FastAPI
app = FastAPI(
    title="API Completa com Memórias Enriquecidas do Agno",
    description="API que integra processamento de mensagens com sistema de memórias contextuais",
    version="2.0.0"
)

# Funções antigas removidas - agora usando DualMemoryOptimizedService

def simulate_agent_response(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Simula resposta do agente com contexto enriquecido"""
    
    # Contexto das memórias
    memories = context.get("memories", [])
    history = context.get("history", [])
    
    # Contexto adicional baseado em memórias
    memory_context = ""
    if memories:
        memory_context = f"\n\nContexto de memórias anteriores: {len(memories)} interações relevantes encontradas."
    
    # Respostas baseadas em palavras-chave
    message_lower = message.lower()
    
    if "horário" in message_lower or "funciona" in message_lower:
        response = f"A Clínica Nutri+ funciona de **segunda a sexta-feira, das 8h às 18h**. Fazemos uma pausa para o almoço entre 12h e 13h.{memory_context}\nPosso ajudar com mais alguma informação ou gostaria de agendar sua consulta ou o Plano Nutricional Online?"
    elif "preço" in message_lower or "valor" in message_lower:
        response = f"Nossos valores variam conforme o tipo de consulta:{memory_context}\n\n• **Consulta Presencial**: R$ 150,00\n• **Consulta Online**: R$ 120,00\n• **Plano Nutricional Completo**: R$ 200,00\n\nGostaria de agendar uma consulta?"
    elif "agend" in message_lower:
        response = f"Ótimo! Para agendar sua consulta:{memory_context}\n\n📞 **Telefone**: (11) 9999-9999\n💻 **WhatsApp**: (11) 9999-9999\n📧 **E-mail**: contato@nutriplus.com\n\nQual tipo de consulta você prefere: presencial ou online?"
    else:
        response = f"Olá! Sou o assistente da Clínica Nutri+.{memory_context}\n\nPosso ajudar com:\n• Informações sobre horários\n• Valores das consultas\n• Agendamentos\n• Planos nutricionais\n\nComo posso ajudar você hoje?"
    
    return {
        "response": response,
        "usage": {
            "input_tokens": len(message.split()),
            "output_tokens": len(response.split()),
            "model": "google/gemini-2.5-flash-lite"
        }
    }

@app.post("/v1/chat", response_model=MessageOutput)
async def process_message(request: List[MessageInput]):
    """Processa mensagem com sistema de memórias enriquecidas"""
    try:
        if not request or len(request) == 0:
            raise HTTPException(status_code=400, detail="Lista de mensagens vazia")
        
        # Pegar primeira mensagem
        msg_input = request[0]
        
        # Gerar session_id se não fornecido
        if not msg_input.session_id:
            msg_input.session_id = str(uuid.uuid4())
        
        # Gerar message_id se não fornecido
        if not msg_input.message_id:
            msg_input.message_id = str(uuid.uuid4())
        
        print(f"🔄 Processando mensagem para user_id: {msg_input.user_id}, agent_id: {msg_input.agent_id}")
        
        # 1. Buscar memórias enriquecidas relevantes
        memories = await list_enriched_memories(msg_input.user_id, limit=5)
        
        # 2. Preparar contexto para o agente
        context = {
            "memories": memories,
            "user_id": msg_input.user_id,
            "agent_id": msg_input.agent_id,
            "session_id": msg_input.session_id
        }
        
        # 3. Gerar resposta do agente
        agent_result = simulate_agent_response(msg_input.mensagem, context)
        response_text = agent_result["response"]
        usage_info = agent_result["usage"]
        
        # 4. Salvar conversa completa na tabela mensagens_ia
        await save_conversation(
            user_id=msg_input.user_id,
            session_id=msg_input.session_id,
            agent_id=msg_input.agent_id,
            user_message=msg_input.mensagem,
            agent_response=response_text
        )
        
        # 5. Enriquecer automaticamente a conversa
        await auto_enrich_conversation(
            user_id=msg_input.user_id,
            session_id=msg_input.session_id,
            user_message=msg_input.mensagem,
            agent_response=response_text
        )
        
        # 8. Preparar resposta
        response = MessageOutput(
            messages=[response_text],
            transferir=False,
            session_id=msg_input.session_id,
            user_id=msg_input.user_id,
            agent_id=msg_input.agent_id,
            custom=[
                {"campo": "pdf", "valor": "catalogo_doces"}
            ],
            agent_usage={
                "input_tokens": usage_info["input_tokens"],
                "output_tokens": usage_info["output_tokens"],
                "model": usage_info["model"]
            }
        )
        
        print(f"✅ Resposta gerada com contexto enriquecido")
        return response
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/v1/memory/create")
async def create_memory_endpoint(request: MemoryRequest):
    """Endpoint para criar memórias enriquecidas manualmente"""
    try:
        # Extrair session_id dos metadados ou gerar um novo
        session_id = request.metadata.get("session_id") if request.metadata else str(uuid.uuid4())
        
        result = await create_enriched_memory(
            user_id=request.user_id,
            session_id=session_id,
            content=request.content,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar memória: {str(e)}")

@app.get("/v1/memory/list/{user_id}")
async def list_memories_endpoint(user_id: str, limit: int = 10):
    """Endpoint para listar memórias enriquecidas"""
    try:
        result = await list_enriched_memories(user_id=user_id, limit=limit)
        return {"memories": result, "total": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar memórias: {str(e)}")

@app.get("/v1/memory/stats/{user_id}")
async def get_memory_stats(user_id: str, agent_id: Optional[str] = None):
    """Endpoint para obter estatísticas de memórias enriquecidas"""
    try:
        memories = await list_enriched_memories(user_id=user_id, limit=100)
        return {
            "user_id": user_id,
            "total_memories": len(memories),
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@app.get("/v1/conversations/{user_id}")
async def get_user_conversations(user_id: str, limit: int = 20):
    """Endpoint para obter histórico de conversas brutas do usuário"""
    try:
        result = dual_memory_service.get_conversation_history(user_id=user_id, limit=limit)
        
        if result.get("status") == "success":
            return {"conversations": result.get("conversations", []), "total": len(result.get("conversations", []))}
        else:
            return {"conversations": [], "total": 0, "error": result.get("error")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter conversas: {str(e)}")

@app.get("/v1/history/{session_id}")
async def get_session_history(session_id: str, user_id: str, limit: int = 20):
    """Endpoint para obter histórico de uma sessão"""
    try:
        history = get_conversation_history(session_id, user_id, limit)
        return {
            "session_id": session_id,
            "user_id": user_id,
            "messages": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da arquitetura dual"""
    try:
        # Testar conexão com tabela mensagens_ia
        mensagens_test = supabase.table("mensagens_ia").select("id").limit(1).execute()
        
        # Testar conexão com tabela message_history
        memory_test = supabase.table("message_history").select("id").limit(1).execute()
        
        # Testar serviço de memória dual
        dual_service_test = await list_enriched_memories("health-check", limit=1)
        
        return {
            "status": "healthy",
            "database": "connected",
            "mensagens_ia_table": "operational",
            "message_history_table": "operational", 
            "dual_memory_service": "operational",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "name": "API Completa com Memórias Enriquecidas do Agno",
        "version": "2.0.0",
        "description": "API que integra processamento de mensagens com sistema de memórias contextuais",
        "endpoints": {
            "chat": "/v1/chat",
            "create_memory": "/v1/memory/create",
            "list_memories": "/v1/memory/list",
            "memory_stats": "/v1/memory/stats/{user_id}",
            "session_history": "/v1/history/{session_id}",
            "health": "/health"
        },
        "features": [
            "Processamento de mensagens com contexto",
            "Sistema de memórias enriquecidas",
            "Histórico de conversas persistente",
            "Análise automática de tópicos",
            "Estatísticas de uso"
        ]
    }

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando API Completa com Memórias Enriquecidas do Agno...")
    print("📊 Recursos disponíveis:")
    print("  • Processamento de mensagens com contexto")
    print("  • Sistema de memórias enriquecidas")
    print("  • Histórico persistente de conversas")
    print("  • Análise automática de tópicos")
    print("  • Endpoints de gerenciamento de memórias")
    print("\n🌐 Acesse: http://localhost:8000/docs para documentação interativa")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)