"""
Serviço para gerenciar operações de agentes no Supabase
"""
import os
import uuid
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class SupabaseService:
    """Classe para gerenciar operações de agentes no Supabase"""
    
    def __init__(self):
        """Inicializa o cliente Supabase"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem estar definidas no .env")
        
        self.supabase: Client = create_client(self.url, self.key)
    
    def create_agent(self, name: str, role: str, instructions: List[str], 
                    model: str = "gpt-4o-mini", account_id: str = None) -> Dict:
        """
        Cria um novo agente na tabela agentes_solo
        
        Args:
            name: Nome do agente
            role: Papel/função do agente
            instructions: Lista de instruções para o agente
            model: Modelo a ser usado (padrão: gpt-4o-mini)
            account_id: ID da conta (se não fornecido, gera um UUID)
        
        Returns:
            Dict com os dados do agente criado
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
                "account_id": account_id
            }
            
            result = self.supabase.table("agentes_solo").insert(agent_data).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise Exception("Falha ao criar agente")
                
        except Exception as e:
            raise Exception(f"Erro ao criar agente: {str(e)}")
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """
        Busca um agente pelo ID
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Dict com os dados do agente ou None se não encontrado
        """
        try:
            result = self.supabase.table("agentes_solo").select("*").eq("id", agent_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar agente: {str(e)}")
    
    def get_agents_by_account(self, account_id: str) -> List[Dict]:
        """
        Busca todos os agentes de uma conta
        
        Args:
            account_id: ID da conta
            
        Returns:
            Lista com os agentes da conta
        """
        try:
            result = self.supabase.table("agentes_solo").select("*").eq("account_id", account_id).execute()
            return result.data or []
            
        except Exception as e:
            raise Exception(f"Erro ao buscar agentes da conta: {str(e)}")
    
    def update_agent(self, agent_id: str, **kwargs) -> Dict:
        """
        Atualiza um agente
        
        Args:
            agent_id: ID do agente
            **kwargs: Campos a serem atualizados
            
        Returns:
            Dict com os dados do agente atualizado
        """
        try:
            # Remove campos que não devem ser atualizados
            update_data = {k: v for k, v in kwargs.items() 
                          if k in ["name", "role", "instructions", "model"]}
            
            if not update_data:
                raise ValueError("Nenhum campo válido para atualização")
            
            result = self.supabase.table("agentes_solo").update(update_data).eq("id", agent_id).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise Exception("Agente não encontrado ou falha na atualização")
                
        except Exception as e:
            raise Exception(f"Erro ao atualizar agente: {str(e)}")
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Deleta um agente
        
        Args:
            agent_id: ID do agente
            
        Returns:
            True se deletado com sucesso
        """
        try:
            result = self.supabase.table("agentes_solo").delete().eq("id", agent_id).execute()
            return len(result.data) > 0
            
        except Exception as e:
            raise Exception(f"Erro ao deletar agente: {str(e)}")
    
    def list_all_agents(self) -> List[Dict]:
        """
        Lista todos os agentes
        
        Returns:
            Lista com todos os agentes
        """
        try:
            result = self.supabase.table("agentes_solo").select("*").execute()
            return result.data or []
            
        except Exception as e:
            raise Exception(f"Erro ao listar agentes: {str(e)}")
    
    # ==================== MÉTODOS PARA MENSAGENS ====================
    
    def save_message(self, user_id: str, session_id: str, agent_id: str, 
                    message: str, response: str, message_id: str = None) -> Dict:
        """
        Salva uma mensagem e resposta no Supabase
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            agent_id: ID do agente
            message: Mensagem do usuário
            response: Resposta do agente
            message_id: ID da mensagem (se não fornecido, gera um UUID)
        
        Returns:
            Dict com os dados da mensagem salva
        """
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
            
            result = self.supabase.table("mensagens_ia").insert(message_data).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise Exception("Falha ao salvar mensagem")
                
        except Exception as e:
            raise Exception(f"Erro ao salvar mensagem: {str(e)}")
    
    def get_session_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        """
        Recupera mensagens de uma sessão específica
        
        Args:
            session_id: ID da sessão
            limit: Número máximo de mensagens (padrão: 50)
        
        Returns:
            Lista de mensagens da sessão
        """
        try:
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
        """
        Recupera mensagens de um usuário específico
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de mensagens (padrão: 100)
        
        Returns:
            Lista de mensagens do usuário
        """
        try:
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
        """
        Busca mensagens por conteúdo
        
        Args:
            user_id: ID do usuário
            query: Termo de busca
            limit: Número máximo de resultados (padrão: 10)
        
        Returns:
            Lista de mensagens que contêm o termo buscado
        """
        try:
            result = self.supabase.table("mensagens_ia")\
                .select("*")\
                .eq("user_id", user_id)\
                .or_(f"user_message.ilike.%{query}%,agent_response.ilike.%{query}%")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            raise Exception(f"Erro ao buscar mensagens: {str(e)}")

# Instância global do serviço
supabase_service = SupabaseService()