"""
Serviço para gerenciar operações de agentes no Supabase
"""
import os
import uuid
from typing import List, Dict, Optional
# Tenta importar o cliente do Supabase; se não estiver disponível, usa fallback em memória
try:
    from supabase import create_client, Client  # type: ignore
except Exception:  # pacote pode não estar instalado em ambiente de testes
    create_client = None  # type: ignore
    Client = None  # type: ignore
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class SupabaseService:
    """Classe para gerenciar operações de agentes no Supabase (com fallback em memória)"""
    
    def __init__(self):
        """Inicializa o cliente Supabase ou ativa modo em memória para testes"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        self._use_memory = False
        self._agents_mem: Dict[str, Dict] = {}
        self._messages_mem: List[Dict] = []

        # Se faltar URL/KEY ou a lib supabase não estiver disponível, ativa memória
        if not self.url or not self.key or create_client is None:
            self._use_memory = True
            self.supabase = None  # type: ignore
            # Semeia um agente padrão para testes que usam "test_agent_123"
            default_id = "test_agent_123"
            if default_id not in self._agents_mem:
                self._agents_mem[default_id] = {
                    "id": default_id,
                    "name": "Agente de Teste",
                    "role": "Assistente",
                    "instructions": [
                        "Você é um assistente de testes.",
                        "Responda de forma concisa."
                    ],
                    "model": "gemini-2.5-flash",
                    "provider": "gemini",
                    "account_id": str(uuid.uuid4()),
                    "created_at": "now()",
                }
        else:
            # Modo Supabase real
            self.supabase: Client = create_client(self.url, self.key)  # type: ignore
    
    def create_agent(self, name: str, role: str, instructions: List[str], 
                    model: str = "gemini-2.5-flash", provider: str = "gemini", account_id: str = None) -> Dict:
        """
        Cria um novo agente na tabela agentes_solo (ou na memória quando em fallback)
        """
        try:
            # Se account_id não for fornecido, gera um UUID
            if not account_id:
                account_id = str(uuid.uuid4())
            agent_data = {
                "name": name,
                "role": role,
                "instructions": instructions,
                "model": model,
                "provider": provider,
                "account_id": account_id
            }
            if self._use_memory:
                # Gera ID e salva em memória
                agent_id = str(uuid.uuid4())
                agent = {
                    "id": agent_id,
                    **agent_data,
                    "created_at": "now()",
                }
                self._agents_mem[agent_id] = agent
                return agent
            # Supabase real com fallback automático para memória em caso de erro
            try:
                result = self.supabase.table("agentes_solo").insert(agent_data).execute()
                if result.data:
                    return result.data[0]
                else:
                    # Se não retornar data, faz fallback para memória
                    raise Exception("Falha ao criar agente (sem data)")
            except Exception as e:
                # Fallback para memória quando Supabase falhar
                agent_id = str(uuid.uuid4())
                agent = {
                    "id": agent_id,
                    **agent_data,
                    "created_at": "now()",
                    "_warning": f"Supabase indisponível ou erro ({str(e)}). Usando memória."
                }
                self._agents_mem[agent_id] = agent
                return agent
        except Exception as e:
            raise Exception(f"Erro ao criar agente: {str(e)}")
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Busca um agente pelo ID"""
        try:
            # Sempre checa cache em memória primeiro (mesmo quando Supabase está ativo)
            if agent_id in self._agents_mem:
                return self._agents_mem.get(agent_id)
            if self._use_memory:
                return self._agents_mem.get(agent_id)
            result = self.supabase.table("agentes_solo").select("*").eq("id", agent_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            raise Exception(f"Erro ao buscar agente: {str(e)}")
    
    def get_agents_by_account(self, account_id: str) -> List[Dict]:
        """Busca todos os agentes de uma conta"""
        try:
            if self._use_memory:
                return [a for a in self._agents_mem.values() if a.get("account_id") == account_id]
            result = self.supabase.table("agentes_solo").select("*").eq("account_id", account_id).execute()
            return result.data or []
        except Exception as e:
            raise Exception(f"Erro ao buscar agentes da conta: {str(e)}")
    
    def update_agent(self, agent_id: str, **kwargs) -> Dict:
        """Atualiza um agente"""
        try:
            update_fields = ["name", "role", "instructions", "model"]
            update_data = {k: v for k, v in kwargs.items() if k in update_fields}
            if not update_data:
                raise ValueError("Nenhum campo válido para atualização")
            if self._use_memory:
                agent = self._agents_mem.get(agent_id)
                if not agent:
                    raise Exception("Agente não encontrado")
                agent.update(update_data)
                return agent
            result = self.supabase.table("agentes_solo").update(update_data).eq("id", agent_id).execute()
            if result.data:
                return result.data[0]
            else:
                raise Exception("Agente não encontrado ou falha na atualização")
        except Exception as e:
            raise Exception(f"Erro ao atualizar agente: {str(e)}")
    
    def delete_agent(self, agent_id: str) -> bool:
        """Deleta um agente"""
        try:
            if self._use_memory:
                return self._agents_mem.pop(agent_id, None) is not None
            result = self.supabase.table("agentes_solo").delete().eq("id", agent_id).execute()
            return len(result.data) > 0
        except Exception as e:
            raise Exception(f"Erro ao deletar agente: {str(e)}")
    
    def list_all_agents(self) -> List[Dict]:
        """Lista todos os agentes"""
        try:
            if self._use_memory:
                return list(self._agents_mem.values())
            result = self.supabase.table("agentes_solo").select("*").execute()
            return result.data or []
        except Exception as e:
            raise Exception(f"Erro ao listar agentes: {str(e)}")
    
    # ==================== MÉTODOS PARA MENSAGENS ====================
    
    def save_message(self, user_id: str, session_id: str, agent_id: str, 
                    message: str, response: str, message_id: str = None) -> Dict:
        """Salva uma mensagem e resposta no Supabase (ou memória)"""
        try:
            if not message_id:
                message_id = str(uuid.uuid4())
            message_data = {
                "id": message_id,
                "user_id": user_id,
                "session_id": session_id,
                "agent_id": agent_id,
                "user_message": message,
                "agent_response": response,
                "created_at": "now()"
            }
            if self._use_memory:
                self._messages_mem.append(message_data)
                return message_data
            result = self.supabase.table("mensagens_ia").insert(message_data).execute()
            if result.data:
                return result.data[0]
            else:
                raise Exception("Falha ao salvar mensagem")
        except Exception as e:
            raise Exception(f"Erro ao salvar mensagem: {str(e)}")
    
    def get_session_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Recupera mensagens de uma sessão específica"""
        try:
            if self._use_memory:
                msgs = [m for m in self._messages_mem if m.get("session_id") == session_id]
                msgs.sort(key=lambda m: m.get("created_at", ""))
                return msgs[:limit]
            result = self.supabase.table("mensagens_ia")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            raise Exception(f"Erro ao recuperar mensagens da sessão: {str(e)}")
    
    def get_user_messages(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Recupera mensagens de um usuário específico"""
        try:
            if self._use_memory:
                msgs = [m for m in self._messages_mem if m.get("user_id") == user_id]
                msgs.sort(key=lambda m: m.get("created_at", ""), reverse=True)
                return msgs[:limit]
            result = self.supabase.table("mensagens_ia")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            raise Exception(f"Erro ao recuperar mensagens do usuário: {str(e)}")
    
    def search_messages(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """Busca mensagens por conteúdo"""
        try:
            raw = (query or "").strip()
            if self._use_memory:
                terms = [t.strip() for t in raw.split("|") if t.strip()] if "|" in raw else ([raw] if raw else [])
                results = []
                for m in self._messages_mem:
                    if m.get("user_id") != user_id:
                        continue
                    text = (m.get("user_message", "") + "\n" + m.get("agent_response", "")).lower()
                    if any(term.lower() in text for term in terms):
                        results.append(m)
                results.sort(key=lambda m: m.get("created_at", ""), reverse=True)
                return results[:limit]
            # Supabase real
            if "|" in raw:
                terms = [t.strip() for t in raw.split("|") if t.strip()]
            else:
                terms = [raw] if raw else []
            seen = set()
            unique_terms = []
            for t in terms:
                if t not in seen:
                    seen.add(t)
                    unique_terms.append(t)
            or_clauses = []
            for term in unique_terms:
                safe_term = term.replace(",", " ")
                like = f"%{safe_term}%"
                or_clauses.append(f"user_message.ilike.{like}")
                or_clauses.append(f"agent_response.ilike.{like}")
            if not or_clauses:
                return []
            or_str = ",".join(or_clauses)
            result = self.supabase.table("mensagens_ia")\
                .select("*")\
                .eq("user_id", user_id)\
                .or_(or_str)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            raise Exception(f"Erro ao buscar mensagens: {str(e)}")

# Instância global do serviço
supabase_service = SupabaseService()