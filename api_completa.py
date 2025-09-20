#!/usr/bin/env python3
"""
API Completa com AgentOS, Knowledge (RAG) e Memória (Mem0)
Baseada no guia definitivo do AgentOS
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Header, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import os
from dotenv import load_dotenv
import requests
import uuid
from datetime import datetime
import json
import time

# Importações para IA e memória
# import openai  # Comentado - usando apenas Vertex AI
from mem0 import MemoryClient
import redis

# Importação dos serviços
from supabase_service import SupabaseService
from dual_memory_service import dual_memory_service
# from vertex_ai_client import VertexAIClient
from vertex_ai_client_new import VertexAIClientNew  # Comentado para usar mock
from vertex_ai_client_mock import VertexAIClientMock as VertexAIClient

# Instanciar cliente Vertex AI
vertex_ai_client_new = VertexAIClientNew()

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de chaves de API
INTERNAL_API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
MEM0_API_KEY = os.getenv("MEM0_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "")
OUTBOUND_WEBHOOK_URL = os.getenv("OUTBOUND_WEBHOOK_URL", "https://webhook.doxagrowth.com.br/webhook/recebimentos-mensagens-agentos")
WEBHOOK_API_KEY = os.getenv("OUTBOUND_WEBHOOK_API_KEY", "")

# Debug: Imprimir configuração do webhook na inicialização
print(f"🔗 WEBHOOK CONFIG: URL={OUTBOUND_WEBHOOK_URL}")
print(f"🔑 WEBHOOK CONFIG: API_KEY={'SET' if WEBHOOK_API_KEY else 'NOT_SET'}")

# Configuração Google AI API (Gemini)
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ")

# Inicialização dos clientes
# openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Comentado - usando apenas Google AI
# openai.api_key = OPENAI_API_KEY  # Compat para SDKs antigos que usam openai.ChatCompletion

# Instância do cliente Vertex AI (novo)
vertex_ai_client_new = VertexAIClientNew(
    api_key="AQ.Ab8RN6LDtoXn4cdQvG62dfzA2M6FozHfH6Tgb8EG4WaS78uc3g"
)

# Inicializa cliente Google AI (Gemini) - mantido para compatibilidade
vertex_ai_client = VertexAIClient(
    api_key=GOOGLE_AI_API_KEY
)

# Função para detectar se deve usar Vertex AI
def _is_vertex_ai_model(model_id: str) -> bool:
    """Detecta se o modelo especificado é do Vertex AI (Gemini)"""
    vertex_models = ["gemini-2.5-flash", "gemini-pro", "gemini-flash", "google/gemini"]
    return any(vertex_model in model_id.lower() for vertex_model in vertex_models)

# Helper para completar com Vertex AI (usando novo cliente)
def _complete_with_vertex_ai(system_prompt: str, user_query: str, model_id: str, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
    """Completa usando Vertex AI e retorna resposta com metadados"""
    try:
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
        
        # O novo cliente já retorna no formato correto
        return {
            "text": result["text"],
            "usage": result["usage"]
        }
        
    except Exception as e:
        return {
            "text": f"Erro ao processar com Vertex AI: {str(e)}",
            "usage": {"input_tokens": 0, "output_tokens": 0, "model": model_id}
        }

# Helper compatível para chamadas OpenAI (Responses API nova ou Chat Completions legado)
def _complete_with_openai(system_prompt: str, user_query: str, model_id: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query},
    ]
    # Tenta a Responses API (SDK v1+)
    try:
        if hasattr(openai_client, "responses"):
            resp = openai_client.responses.create(
                model=model_id,
                input=messages,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            text = getattr(resp, "output_text", None)
            if not text:
                try:
                    text = resp.outputs[0].content[0].text  # fallback de extração
                except Exception:
                    text = None
            if text:
                return text
    except Exception:
        pass
    # Fallbacks do OpenAI comentados - usando apenas Vertex AI
    # try:
    #     if hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
    #         resp = openai.chat.completions.create(
    #             model=model_id,
    #             messages=messages,
    #             temperature=temperature,
    #             max_tokens=max_tokens,
    #         )
    #         return resp.choices[0].message.content
    # except Exception:
    #     pass
    # try:
    #     resp = openai.ChatCompletion.create(
    #         model=model_id,
    #         messages=messages,
    #         temperature=temperature,
    #         max_tokens=max_tokens,
    #     )
    #     return resp["choices"][0]["message"]["content"]
    # except Exception as e:
    #     raise e
    
    # Se chegou aqui, não conseguiu gerar resposta
    raise Exception("Não foi possível gerar resposta com o OpenAI")

# Função de verificação de API Key
async def verify_api_key(x_api_key: str = Header(None)):
    """Verifica se a X-API-Key é válida"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="X-API-Key header é obrigatório",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="X-API-Key inválida",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return x_api_key

# Modelos de dados para Chat/Mensagens
class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem do usuário")
    agent_name: Optional[str] = Field("Especialista em Produtos", description="Nome do agente")
    user_id: str = Field(..., description="ID do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")

class MessageRequest(BaseModel):
    mensagem: str = Field(..., description="Mensagem do usuário")
    agent_id: str = Field(..., description="ID do agente")
    user_id: str = Field(..., description="ID do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    message_id: Optional[str] = Field(None, description="ID da mensagem")
    cliente_id: Optional[str] = Field("", description="ID do cliente")
    id_conta: Optional[str] = Field(None, description="ID da conta")
    debounce: Optional[int] = Field(0, description="Tempo de debounce em ms")

# Modelos de dados para Agentes
class AgentCreateRequest(BaseModel):
    name: str = Field(..., description="Nome do agente")
    role: str = Field(..., description="Papel/função do agente")
    instructions: List[str] = Field(..., description="Lista de instruções para o agente")
    model: Optional[str] = Field("gemini-2.5-flash", description="Modelo LLM a ser usado")
    provider: Optional[str] = Field("gemini", description="Provider do modelo (gemini, openai)")
    account_id: Optional[str] = Field(None, description="ID da conta associada ao agente")

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Novo nome do agente")
    role: Optional[str] = Field(None, description="Nova função do agente")
    instructions: Optional[List[str]] = Field(None, description="Novas instruções")
    model: Optional[str] = Field(None, description="Novo modelo LLM")
    provider: Optional[str] = Field(None, description="Novo provider do modelo (gemini, openai)")
    account_id: Optional[str] = Field(None, description="Novo ID da conta")

class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    instructions: List[str]
    model: str
    provider: Optional[str]
    account_id: Optional[str]
    created_at: str

# Modelos para Knowledge e Memória
class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., description="Consulta para buscar na base de conhecimento")
    limit: Optional[int] = Field(5, description="Número máximo de resultados")

class MemorySearchRequest(BaseModel):
    user_id: str = Field(..., description="ID do usuário")
    query: str = Field(..., description="Consulta para buscar na memória")
    limit: Optional[int] = Field(3, description="Número máximo de resultados")

class MemoryAddRequest(BaseModel):
    user_id: str = Field(..., description="ID do usuário")
    content: str = Field(..., description="Conteúdo para adicionar à memória")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")

# Modelos de resposta
class ChatResponse(BaseModel):
    response: str
    agent_name: str
    user_id: str
    session_id: Optional[str]
    timestamp: str

class MessageResponse(BaseModel):
    messages: List[str]
    transferir: bool = False
    session_id: Optional[str]
    user_id: str
    agent_id: str
    custom: Optional[List[Dict[str, str]]] = []
    agent_usage: Optional[Dict[str, Any]] = None

# Inicializa FastAPI
app = FastAPI(
    title="API de Agente de Suporte com Knowledge e Memória",
    description="Uma API completa para interagir com agentes inteligentes que usam RAG nativo e memória Mem0.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Status",
            "description": "Endpoints de status e saúde do sistema"
        },
        {
            "name": "Chat & Mensagens",
            "description": "Endpoints para envio de mensagens e chat com agentes"
        },
        {
            "name": "Agentes",
            "description": "Gerenciamento de agentes inteligentes"
        },
        {
            "name": "Knowledge (RAG)",
            "description": "Base de conhecimento e busca semântica"
        },
        {
            "name": "Memória (Mem0)",
            "description": "Sistema de memória contextual"
        }
    ]
)

# Webhook fake local para testes de debounce
_last_webhook_payload: Optional[Dict[str, Any]] = None

@app.post("/fake-webhook", tags=["Status"], summary="Webhook fake para testes")
async def fake_webhook(payload: dict, request: Request):
    """Recebe o payload do debounce e armazena em memória para inspeção."""
    global _last_webhook_payload
    _last_webhook_payload = payload
    # Opcional: log rápido para depuração
    print("[fake-webhook] payload recebido:", json.dumps(payload)[:500])
    return {"status": "received", "received_at": datetime.now().isoformat()}

@app.get("/fake-webhook/last", tags=["Status"], summary="Último payload recebido no webhook fake")
async def get_last_webhook_payload():
    return _last_webhook_payload or {}

# Instancia o serviço do Supabase
supabase_service = SupabaseService()

# Simulação de banco de dados em memória para sessões
sessions_db = {}

# Simulação das funcionalidades de Knowledge e Memória
class KnowledgeService:
    """Serviço de Knowledge (RAG) com Pinecone"""
    
    def __init__(self):
        self.knowledge_base = [
            {"content": "O modo noturno pode ser ativado no menu de configurações > tela.", "score": 0.95, "id": "kb_1"},
            {"content": "A bateria do dispositivo X dura 24 horas com uso moderado.", "score": 0.90, "id": "kb_2"},
            {"content": "Para reiniciar o dispositivo, pressione o botão de energia por 10 segundos.", "score": 0.85, "id": "kb_3"},
            {"content": "A garantia padrão do produto é de 12 meses e cobre defeitos de fabricação.", "score": 0.80, "id": "kb_4"},
            {"content": "O suporte técnico está disponível de segunda a sexta, das 8h às 18h.", "score": 0.75, "id": "kb_5"},
            {"content": "O dispositivo suporta carregamento rápido de 30W.", "score": 0.70, "id": "kb_6"},
            {"content": "A tela tem resolução 4K e suporte a HDR.", "score": 0.65, "id": "kb_7"},
            {"content": "O produto é resistente à água com certificação IP68.", "score": 0.60, "id": "kb_8"}
        ]
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict]:
        """Busca na base de conhecimento"""
        query_lower = query.lower()
        results = []
        
        for item in self.knowledge_base:
            if any(word in item["content"].lower() for word in query_lower.split()):
                results.append(item)
        
        # Ordena por relevância (score)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def sync_knowledge(self) -> bool:
        """Sincroniza a base de conhecimento"""
        return True

class MemoryService:
    """Serviço de Memória com Mem0 - Integrado com dual_memory_service"""
    
    def __init__(self):
        # Usar o dual_memory_service já importado
        self.dual_memory = dual_memory_service
    
    def save_memory(self, user_id: str, prompt: str, response: str) -> bool:
        """Salva interação na memória usando dual_memory_service"""
        try:
            return self.dual_memory.save_complete_interaction(
                user_id=user_id,
                session_id=f"direct_session_{user_id}",
                agent_id="direct_memory",
                user_message=prompt,
                agent_response=response,
                agent_name="Sistema"
            )
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")
            return False
    
    def search_memory(self, user_id: str, query: str, limit: int = 3) -> List[Dict]:
        """Busca memórias do usuário usando dual_memory_service"""
        try:
            # Usar o método search_memory do dual_memory_service que retorna lista
            results = self.dual_memory.search_memory(user_id, query, limit)
            return results
        except Exception as e:
            print(f"Erro ao buscar memória: {e}")
            return []
    
    def add_memory(self, user_id: str, content: str, metadata: Dict = None) -> bool:
        """Adiciona memória específica usando dual_memory_service"""
        try:
            # Usar o método add_memory do dual_memory_service que aceita metadata
            return self.dual_memory.add_memory(user_id, content, metadata)
        except Exception as e:
            print(f"Erro ao adicionar memória: {e}")
            return False

# Cliente Redis (opcional)
redis_client = None
if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        # Teste simples de conexão
        redis_client.ping()
    except Exception:
        redis_client = None

# Adiciona resolução automática de sessão (auto-resume)
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "86400"))  # 24h por padrão
_active_sessions_mem: Dict = {}
_active_sessions_expiry: Dict = {}

def _active_session_key(agent_id: str, user_id: str) -> str:
    return f"active_session:{agent_id}:{user_id}"

def _remember_active_session(agent_id: str, user_id: str, session_id: str):
    try:
        if redis_client:
            redis_client.setex(_active_session_key(agent_id, user_id), SESSION_TTL_SECONDS, session_id)
        else:
            _active_sessions_mem[(agent_id, user_id)] = session_id
            _active_sessions_expiry[(agent_id, user_id)] = time.time() + SESSION_TTL_SECONDS
    except Exception:
        # Evita quebrar o fluxo por erro de cache
        pass

def resolve_session_id(agent_id: str, user_id: str, provided_session_id: Optional[str]) -> str:
    """Resolve e mantém o session_id ativo por (agent_id,user_id) se o cliente não enviar.
    - Se o cliente enviar, lembra esse ID com TTL.
    - Se não enviar, tenta recuperar do Redis/memória.
    - Se não existir, cria um novo e lembra.
    """
    try:
        if provided_session_id:
            _remember_active_session(agent_id, user_id, provided_session_id)
            return provided_session_id
        if redis_client:
            sid = redis_client.get(_active_session_key(agent_id, user_id))
            if sid:
                return sid
        else:
            exp = _active_sessions_expiry.get((agent_id, user_id))
            if exp and exp > time.time():
                sid = _active_sessions_mem.get((agent_id, user_id))
                if sid:
                    return sid
        # Não havia sessão ativa -> cria nova
        new_sid = str(uuid.uuid4())
        _remember_active_session(agent_id, user_id, new_sid)
        return new_sid
    except Exception:
        # Fallback total
        return provided_session_id or str(uuid.uuid4())

# Estruturas de fallback em memória
_inmemory_buffers = {}
_inmemory_deadlines = {}
_inmemory_locks = {}

class DebounceManager:
    def __init__(self, redis_cli=None, default_ms: int = 15000):
        self.redis = redis_cli
        self.default_ms = default_ms

    def _keys(self, base_key: str):
        msgs_key = f"db:{base_key}:messages"
        deadline_key = f"db:{base_key}:deadline"
        lock_key = f"db:{base_key}:lock"
        return msgs_key, deadline_key, lock_key

    def add_message(self, base_key: str, message_obj: dict, window_ms: int):
        ms = window_ms if (window_ms is not None and window_ms >= 0) else self.default_ms
        now = time.time()
        deadline = now + (ms / 1000.0)
        if self.redis:
            msgs_key, deadline_key, _ = self._keys(base_key)
            pipe = self.redis.pipeline()
            pipe.rpush(msgs_key, json.dumps(message_obj))
            pipe.set(deadline_key, str(deadline))
            # Expiração de segurança (5x janela + 60s)
            expire_sec = max(int(ms / 1000) * 5 + 60, 120)
            pipe.expire(msgs_key, expire_sec)
            pipe.expire(deadline_key, expire_sec)
            pipe.execute()
        else:
            buf = _inmemory_buffers.setdefault(base_key, [])
            buf.append(message_obj)
            _inmemory_deadlines[base_key] = deadline

    def _acquire_lock(self, base_key: str, ttl_sec: int = 60) -> bool:
        if self.redis:
            _, _, lock_key = self._keys(base_key)
            try:
                return bool(self.redis.set(lock_key, "1", nx=True, ex=ttl_sec))
            except Exception:
                return False
        # Fallback em memória
        if _inmemory_locks.get(base_key):
            return False
        _inmemory_locks[base_key] = True
        return True

    def _release_lock(self, base_key: str):
        if self.redis:
            _, _, lock_key = self._keys(base_key)
            try:
                self.redis.delete(lock_key)
            except Exception:
                pass
        else:
            _inmemory_locks.pop(base_key, None)

    def _get_deadline(self, base_key: str) -> float:
        if self.redis:
            _, deadline_key, _ = self._keys(base_key)
            val = self.redis.get(deadline_key)
            try:
                return float(val) if val is not None else 0.0
            except Exception:
                return 0.0
        return float(_inmemory_deadlines.get(base_key, 0.0))

    def _drain_messages(self, base_key: str) -> list:
        if self.redis:
            msgs_key, deadline_key, _ = self._keys(base_key)
            try:
                msgs = self.redis.lrange(msgs_key, 0, -1) or []
                self.redis.delete(msgs_key)
                self.redis.delete(deadline_key)
                out = []
                for m in msgs:
                    try:
                        out.append(json.loads(m))
                    except Exception:
                        pass
                return out
            except Exception:
                return []
        # fallback
        msgs = _inmemory_buffers.pop(base_key, [])
        _inmemory_deadlines.pop(base_key, None)
        return msgs

    def process_when_ready(self, base_key: str, handler_fn, poll_interval: float = 0.5):
        # Evita múltiplos workers simultâneos
        if not self._acquire_lock(base_key):
            return
        try:
            while True:
                deadline = self._get_deadline(base_key)
                now = time.time()
                if deadline <= 0:
                    # Nada a processar (limpo por outro worker)
                    return
                delta = deadline - now
                if delta > 0:
                    time.sleep(min(delta, poll_interval))
                    continue
                # Deadline atingido: drena e processa
                messages = self._drain_messages(base_key)
                if messages:
                    handler_fn(messages)
                return
        finally:
            self._release_lock(base_key)

# Instância do debounce manager
debounce_manager = DebounceManager(redis_cli=redis_client)

# Função handler que será chamada quando a janela de debounce expirar
def _debounce_handler_factory(agent_id: str, user_id: str, session_id: str):
    def _handler(msg_list: list):
        # msg_list é uma lista de objetos do request original
        try:
            # Buscar dados do agente
            try:
                agent = supabase_service.get_agent(agent_id)
                if not agent:
                    raise Exception("Agente não encontrado")
            except Exception as e:
                # Fallback resiliente: tenta listar agentes e, se falhar, usa defaults
                try:
                    agents = supabase_service.list_all_agents()
                    agent = agents[0] if agents else None
                except Exception as e2:
                    agent = None
                if not agent:
                    agent = {"name": "Agente", "model": "gpt-4o-mini", "role": "assistente", "instructions": []}

            # Combinar mensagens (ordem de recebimento)
            incoming_texts = [m.get("mensagem", "") for m in msg_list if isinstance(m, dict)]
            combined_query = "\n".join(incoming_texts).strip()
            last_message = incoming_texts[-1] if incoming_texts else ""

            # Recuperar contexto com base no último prompt (mais recente) + histórico combinado como apoio
            try:
                memory_context = dual_memory_service.get_complete_context(
                    user_id=user_id,
                    session_id=session_id,
                    query=last_message or combined_query,
                    session_limit=5,
                    memory_limit=3
                )
            except Exception as e:
                memory_context = {
                    "session_context": "",
                    "enriched_context": "",
                    "related_history": ""
                }

            # Executar agente com contexto
            agent_result = execute_agent_with_memory(last_message or combined_query, user_id, agent, memory_context)
            response_text = agent_result["text"]
            agent_usage = agent_result["usage"]

            # Salvar memória da interação combinada (não bloquear envio de webhook)
            try:
                dual_memory_service.save_complete_interaction(
                    user_id=user_id,
                    session_id=session_id,
                    agent_id=agent_id,
                    user_message=combined_query or last_message,
                    agent_response=response_text,
                    agent_name=agent.get("name", "Agente")
                )
            except Exception:
                pass

            # Construir payload para webhook
            payload = {
                "messages": [response_text],
                "transferir": False,
                "session_id": session_id,
                "user_id": user_id,
                "agent_id": agent_id,
                "custom": [],
                "agent_usage": agent_usage
            }

            headers = {
                "Content-Type": "application/json"
            }
            if WEBHOOK_API_KEY:
                headers["X-API-Key"] = WEBHOOK_API_KEY

            try:
                resp = requests.post(OUTBOUND_WEBHOOK_URL, headers=headers, data=json.dumps(payload), timeout=15)
                try:
                    print(f"[WEBHOOK] Enviado para {OUTBOUND_WEBHOOK_URL} status={resp.status_code}")
                except Exception:
                    pass
            except Exception as e:
                try:
                    print(f"[WEBHOOK][ERRO] Falha ao enviar: {e}")
                except Exception:
                    pass
        except Exception:
            # Logar erro em produção
            pass
    return _handler

# Instâncias dos serviços
knowledge_service = KnowledgeService()
# Instanciando o MemoryService que agora usa o dual_memory_service internamente
memory_service = MemoryService()

# Função para executar agente usando OpenAI diretamente
def execute_agent(query: str, user_id: str, agent_data: dict) -> Dict[str, Any]:
    """Executa o agente usando OpenAI ou Vertex AI e retorna resposta com metadados"""
    try:
        # Template de prompt para o agente
        prompt = (
            f"Você é um {agent_data['role']}.\n"
            f"Siga estas instruções:\n"
            f"{chr(10).join(agent_data['instructions'])}\n\n"
            f"Responda à pergunta do usuário de forma precisa e profissional."
        )
        
        # Modelo (remove prefixo openai/ se existir)
        model_id = (agent_data.get("model") or "gemini-2.5-flash").replace("openai/", "")
        
        # Detecta se deve usar Vertex AI
        if _is_vertex_ai_model(model_id):
            result = _complete_with_vertex_ai(
                system_prompt=prompt,
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
            # Usa OpenAI
            text = _complete_with_openai(
                system_prompt=prompt,
                user_query=query,
                model_id=model_id,
                temperature=0.7,
                max_tokens=1000,
            )
            return {
                "text": text,
                "usage": {"input_tokens": 0, "output_tokens": 0, "model": model_id}
            }

    except Exception as e:
        return {
            "text": f"Desculpe, ocorreu um erro ao processar sua solicitação. Por favor, tente novamente. Erro: {str(e)}",
            "usage": {"input_tokens": 0, "output_tokens": 0, "model": "error"}
        }

def execute_agent_with_memory(query: str, user_id: str, agent_data: dict, memory_context: dict) -> Dict[str, Any]:
    """Executa agente com contexto de memória dupla usando OpenAI ou Vertex AI"""
    try:
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
        
        # Detecta se deve usar Vertex AI
        if _is_vertex_ai_model(model_id):
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
            # Usa OpenAI
            text = _complete_with_openai(
                system_prompt=system_prompt,
                user_query=query,
                model_id=model_id,
                temperature=0.7,
                max_tokens=1000,
            )
            return {
                "text": text,
                "usage": {"input_tokens": 0, "output_tokens": 0, "model": model_id}
            }
            
    except Exception as e:
        return {
            "text": f"Desculpe, ocorreu um erro ao processar sua solicitação com memória. Erro: {str(e)}",
            "usage": {"input_tokens": 0, "output_tokens": 0, "model": "error"}
        }

# Função para gerar resposta inteligente com memória dupla
def generate_intelligent_response(query: str, user_id: str, session_id: str, agent_name: str = "Especialista em Produtos") -> str:
    """Gera resposta usando AgentOS real com contexto de memória dupla"""
    try:
        # Busca agentes no Supabase
        agents = supabase_service.list_all_agents()
        
        # Procura por um agente com nome similar ou usa o primeiro disponível
        agent_data = None
        for agent in agents:
            if agent_name.lower() in agent.get("name", "").lower():
                agent_data = agent
                break
        
        # Se não encontrou, usa o primeiro agente disponível
        if not agent_data and agents:
            agent_data = agents[0]
        
        if not agent_data:
            return "Nenhum agente disponível"
        
        # Recupera contexto completo da memória dupla
        memory_context = dual_memory_service.get_complete_context(
            user_id=user_id,
            session_id=session_id,
            query=query,
            session_limit=5,
            memory_limit=3
        )
        
        # Executa o agente com contexto enriquecido
        agent_result = execute_agent_with_memory(query, user_id, agent_data, memory_context)
        return agent_result["text"]
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

# ===== CHAT & MENSAGENS =====

@app.post("/v1/chat", tags=["Chat & Mensagens"], summary="Chat com agente")
async def chat_with_agent(request: ChatRequest, api_key: str = Depends(verify_api_key)) -> ChatResponse:
    """Endpoint principal para chat com agentes com memória dupla"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Gera resposta inteligente com memória dupla
        response = generate_intelligent_response(
            query=request.message, 
            user_id=request.user_id, 
            session_id=session_id,
            agent_name=request.agent_name
        )
        
        # Salva na memória dupla (Supabase + Mem0)
        agent_id = request.agent_name  # Usando agent_name como ID temporário
        memory_result = dual_memory_service.save_complete_interaction(
            user_id=request.user_id,
            session_id=session_id,
            agent_id=agent_id,
            user_message=request.message,
            agent_response=response,
            agent_name=request.agent_name
        )
        
        # Salva na sessão (compatibilidade)
        if session_id not in sessions_db:
            sessions_db[session_id] = []
        
        sessions_db[session_id].append({
            "user_message": request.message,
            "agent_response": response,
            "timestamp": datetime.now().isoformat(),
            "memory_saved": memory_result
        })
        
        return ChatResponse(
            response=response,
            agent_name=request.agent_name,
            user_id=request.user_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")

@app.post("/v1/messages", tags=["Chat & Mensagens"], summary="Enviar mensagem para agente")
async def send_message_to_agent(
    request: Union[MessageRequest, List[MessageRequest]],
    api_key: str = Depends(verify_api_key),
    background_tasks: BackgroundTasks = None
) -> MessageResponse:
    """
    Endpoint principal para envio de mensagens para agentes inteligentes.
    
    Suporta receber um único objeto MessageRequest OU uma lista de objetos (compatibilidade com integrações que enviam arrays).
    
    Comportamento de debounce: mensagens recebidas dentro da janela (debounce em ms) são agrupadas
    e processadas em uma única resposta enviada ao webhook de saída.
    """
    try:
        t0 = time.perf_counter()
        
        # Normaliza para lista de itens ANTES de acessar atributos (evita erro quando o corpo é uma lista)
        items: List[MessageRequest] = request if isinstance(request, list) else [request]
        last_item = items[-1]
        
        # Session ID inicial seguro mesmo quando o corpo for uma lista
        session_id = (last_item.session_id or str(uuid.uuid4()))

        # Resolve/atribui session_id de forma estável por (agent_id,user_id)
        session_id = resolve_session_id(last_item.agent_id, last_item.user_id, last_item.session_id)

        # Apenas valida se existe pelo menos 1 agente (não processa aqui)
        agent = None
        try:
            agent = supabase_service.get_agent(last_item.agent_id)
            if not agent:
                raise Exception("Agente não encontrado")
        except Exception:
            agents = supabase_service.list_all_agents()
            if not agents:
                raise HTTPException(status_code=404, detail="Nenhum agente disponível")
            # Fallback: tenta localizar o agente pelo id; se não achar, usa o primeiro disponível
            if isinstance(agents, list):
                try:
                    agent = next((a for a in agents if isinstance(a, dict) and a.get("id") == last_item.agent_id), None)
                except Exception:
                    agent = None
                if agent is None:
                    agent = agents[0]
        t1 = time.perf_counter()

        # Monta chave de agrupamento
        base_key = f"{last_item.agent_id}:{last_item.user_id}:{session_id}"
        # Define debounce efetivo (permite 0) usando o último item
        effective_debounce_ms = last_item.debounce if last_item.debounce is not None else 15000

        # Enfileira TODAS as mensagens recebidas nesta chamada
        for it in items:
            # Garante que todo item use o session_id resolvido para manter o agrupamento
            debounce_manager.add_message(
                base_key,
                {
                    "mensagem": it.mensagem,
                    "agent_id": it.agent_id,
                    "user_id": it.user_id,
                    "session_id": session_id,
                    "message_id": it.message_id,
                    "cliente_id": it.cliente_id,
                    "id_conta": it.id_conta,
                    "timestamp": datetime.now().isoformat()
                },
                effective_debounce_ms
            )
        t2 = time.perf_counter()

        # Agenda o worker que aguardará a janela e processará quando expirar (apenas uma vez)
        if background_tasks is not None:
            background_tasks.add_task(
                debounce_manager.process_when_ready,
                base_key,
                _debounce_handler_factory(last_item.agent_id, last_item.user_id, session_id)
            )
        t3 = time.perf_counter()

        # Log de métricas por etapa
        try:
            print(
                "[METRICS] /v1/messages | validação: {:.1f}ms | enqueue: {:.1f}ms | agendamento: {:.1f}ms | total: {:.1f}ms".format(
                    (t1 - t0) * 1000.0,
                    (t2 - t1) * 1000.0,
                    (t3 - t2) * 1000.0,
                    (t3 - t0) * 1000.0,
                )
            )
        except Exception:
            pass

        # Retorna ACK imediato informando que a resposta será enviada ao webhook
        return MessageResponse(
            messages=[f"Debounce iniciado. A resposta será enviada ao webhook em até {int((effective_debounce_ms)/1000)}s se não houver novas mensagens."],
            transferir=False,
            session_id=session_id,
            user_id=last_item.user_id,
            agent_id=last_item.agent_id,
            custom=[],
            agent_usage={
                "provider": (agent.get("provider") if isinstance(agent, dict) else None),
                "model": (agent.get("model") if isinstance(agent, dict) else None),
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")

# ===== AGENTES =====

@app.post("/v1/agents", tags=["Agentes"], summary="Criar novo agente")
async def create_agent(request: AgentCreateRequest, api_key: str = Depends(verify_api_key)) -> AgentResponse:
    """Cria um novo agente inteligente"""
    try:
        # Usa o Supabase para criar o agente
        agent = supabase_service.create_agent(
            name=request.name,
            role=request.role,
            instructions=request.instructions,
            model=request.model or "gemini-2.5-flash",
            provider=request.provider or "gemini",
            account_id=request.account_id
        )
        
        # Adiciona created_at se não existir
        if "created_at" not in agent:
            agent["created_at"] = datetime.now().isoformat()
        
        return AgentResponse(**agent)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(e)}")

@app.get("/v1/agents", tags=["Agentes"], summary="Listar agentes")
async def list_agents(account_id: Optional[str] = Query(None, description="Filtrar por ID da conta"), api_key: str = Depends(verify_api_key)):
    """Lista todos os agentes disponíveis"""
    try:
        # Busca agentes no Supabase
        if account_id:
            agents_list = supabase_service.get_agents_by_account(account_id)
        else:
            agents_list = supabase_service.list_all_agents()
        
        # Converte os agentes para a estrutura correta de resposta
        formatted_agents = []
        for agent in agents_list:
            # Garante que todos os campos obrigatórios estejam presentes
            agent_response = {
                "id": agent.get("id"),
                "name": agent.get("name"),
                "role": agent.get("role"),
                "instructions": agent.get("instructions", []),
                "model": agent.get("model", "gpt-4o-mini"),
                "account_id": agent.get("account_id"),
                "created_at": agent.get("created_at", datetime.now().isoformat())
            }
            formatted_agents.append(agent_response)
        
        return {
            "agents": formatted_agents,
            "total": len(formatted_agents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar agentes: {str(e)}")

@app.get("/v1/agents/{agent_id}", tags=["Agentes"], summary="Obter agente específico")
async def get_agent(agent_id: str, api_key: str = Depends(verify_api_key)) -> AgentResponse:
    """Obtém detalhes de um agente específico"""
    try:
        agent = supabase_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        # Adiciona created_at se não existir
        if "created_at" not in agent:
            agent["created_at"] = datetime.now().isoformat()
        
        return AgentResponse(**agent)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter agente: {str(e)}")

@app.put("/v1/agents/{agent_id}", tags=["Agentes"], summary="Atualizar agente")
async def update_agent(agent_id: str, request: AgentUpdateRequest, api_key: str = Depends(verify_api_key)) -> AgentResponse:
    """Atualiza um agente existente"""
    try:
        # Prepara dados para atualização (apenas campos não nulos)
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.role is not None:
            update_data["role"] = request.role
        if request.instructions is not None:
            update_data["instructions"] = request.instructions
        if request.model is not None:
            update_data["model"] = request.model
        if request.account_id is not None:
            update_data["account_id"] = request.account_id
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização")
        
        # Atualiza no Supabase
        agent = supabase_service.update_agent(agent_id, **update_data)
        
        # Adiciona created_at se não existir
        if "created_at" not in agent:
            agent["created_at"] = datetime.now().isoformat()
        
        return AgentResponse(**agent)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar agente: {str(e)}")

@app.delete("/v1/agents/{agent_id}", tags=["Agentes"], summary="Deletar agente")
async def delete_agent(agent_id: str, api_key: str = Depends(verify_api_key)):
    """Deleta um agente"""
    try:
        # Tenta deletar no Supabase
        success = supabase_service.delete_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        return {"message": "Agente deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar agente: {str(e)}")

# ===== KNOWLEDGE (RAG) =====

@app.get("/v1/knowledge/search", tags=["Knowledge (RAG)"], summary="Buscar na base de conhecimento")
async def search_knowledge(
    query: str = Query(..., description="Consulta para buscar na base de conhecimento"),
    limit: int = Query(5, description="Número máximo de resultados"),
    api_key: str = Depends(verify_api_key)
):
    """Busca direta na base de conhecimento (RAG)"""
    try:
        results = knowledge_service.search_knowledge(query, limit)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")

@app.post("/v1/knowledge/sync", tags=["Knowledge (RAG)"], summary="Sincronizar base de conhecimento")
async def sync_knowledge(api_key: str = Depends(verify_api_key)):
    """Sincroniza a base de conhecimento com Pinecone"""
    try:
        success = knowledge_service.sync_knowledge()
        if success:
            return {"message": "Base de conhecimento sincronizada com sucesso", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Falha na sincronização")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")

# ===== MEMÓRIA (MEM0) =====

@app.get("/v1/memory/search", tags=["Memória (Mem0)"], summary="Buscar memórias do usuário")
async def search_memory(
    user_id: str = Query(..., description="ID do usuário"), 
    query: str = Query(..., description="Consulta de busca"), 
    limit: int = Query(3, description="Limite de resultados"),
    api_key: str = Depends(verify_api_key)
):
    """Busca memórias específicas do usuário"""
    try:
        memories = memory_service.search_memory(user_id, query, limit)
        return {
            "user_id": user_id,
            "query": query,
            "memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca de memória: {str(e)}")

@app.post("/v1/memory/add", tags=["Memória (Mem0)"], summary="Adicionar memória")
async def add_memory(request: MemoryAddRequest, api_key: str = Depends(verify_api_key)):
    """Adiciona uma nova memória para o usuário"""
    try:
        success = memory_service.add_memory(request.user_id, request.content, request.metadata)
        if success:
            return {"message": "Memória adicionada com sucesso", "user_id": request.user_id}
        else:
            raise HTTPException(status_code=500, detail="Falha ao adicionar memória")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar memória: {str(e)}")

@app.get("/v1/memory/{user_id}", tags=["Memória (Mem0)"], summary="Obter todas as memórias do usuário")
async def get_user_memories(user_id: str, api_key: str = Depends(verify_api_key)):
    """Obtém todas as memórias de um usuário"""
    try:
        # Usar o memory_service que agora integra com dual_memory_service
        memories = memory_service.search_memory(user_id, "", limit=100)  # Busca ampla para obter todas
        return {
            "user_id": user_id,
            "memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter memórias: {str(e)}")

# ===== STATUS =====

@app.get("/v1/health", tags=["Status"], summary="Status de saúde do sistema")
async def health_check():
    """Verifica o status de todos os componentes"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "api": "online",
                "knowledge_service": "online",
                "memory_service": "online",
                "agents": "online"
            },
            "features": {
                "rag_enabled": True,
                "memory_enabled": True,
                "agents_enabled": True,
                "chat_enabled": True
            },
            "statistics": {
                "total_agents": len(supabase_service.list_all_agents()),
                "total_sessions": len(sessions_db),
                "memory_service": "integrated_with_dual_memory"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Novo bloco __main__ movido para o final do arquivo, após inicialização do Redis e DebounceManager
if __name__ == "__main__":
    import uvicorn
    
    # Usar a porta do arquivo .env ou 8002 como padrão
    port = int(os.getenv("PORT", 8002))
    
    print("🚀 Iniciando API Completa com Knowledge e Memória...")
    print(f"📚 Documentação disponível em http://localhost:{port}/docs")
    print("🔍 Endpoints disponíveis:")
    print("  - Chat: POST /v1/chat")
    print("  - Mensagens: POST /v1/messages")
    print("  - Agentes: GET/POST/PUT/DELETE /v1/agents")
    print("  - Knowledge: GET /v1/knowledge/search")
    print("  - Memória: GET /v1/memory/search")
    print("  - Status: GET /v1/health")
    uvicorn.run(app, host="0.0.0.0", port=port)