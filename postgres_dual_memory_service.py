"""
Serviço de Memória Dupla - Combina memória interna (Supabase) e externa (PostgreSQL com pgvector)
Substitui completamente o Mem0 por PostgreSQL para melhor performance e controle
"""
import os
from typing import List, Dict, Any, Optional
from supabase_service import supabase_service
from postgres_memory_system import PostgreSQLMemorySystem
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class PostgresDualMemoryService:
    """
    Gerenciador de memória dupla que combina:
    - Memória Interna: Histórico de mensagens no Supabase (persistente, estruturado)
    - Memória Externa: Contexto enriquecido no PostgreSQL com pgvector (semântico, inteligente)
    """
    
    def __init__(self, postgres_connection_string=None):
        """Inicializa o serviço de memória dual com Supabase e PostgreSQL"""
        # Inicializa o sistema de memória interna (Supabase)
        self.supabase = supabase_service
        
        # Usa a connection string fornecida ou a padrão do ambiente
        if postgres_connection_string is None:
            postgres_connection_string = os.getenv(
                "POSTGRES_CONNECTION_STRING",
                "postgres://postgres:329fe52ffbdf73289f3c@painel.doxagrowth.com.br:5523/agentes-python?sslmode=disable"
            )
        
        # Inicializa o sistema de memória externa (PostgreSQL)
        self.postgres_memory = PostgreSQLMemorySystem(postgres_connection_string)
        
    # ==================== MEMÓRIA INTERNA (SUPABASE) ====================
    
    def save_message_to_internal_memory(self, user_id: str, session_id: str, 
                                      agent_id: str, user_message: str, 
                                      agent_response: str, message_id: str = None) -> Dict:
        """
        Salva mensagem na memória interna (Supabase)
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            agent_id: ID do agente
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            message_id: ID da mensagem (opcional)
        
        Returns:
            Dict com dados da mensagem salva
        """
        try:
            return self.supabase.save_message(
                user_id=user_id,
                session_id=session_id,
                agent_id=agent_id,
                message=user_message,
                response=agent_response,
                message_id=message_id
            )
        except Exception as e:
            logging.error(f"Erro ao salvar na memória interna: {e}")
            return {}
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """
        Recupera histórico da sessão da memória interna
        
        Args:
            session_id: ID da sessão
            limit: Número de mensagens a recuperar
        
        Returns:
            Lista de mensagens da sessão
        """
        try:
            return self.supabase.get_session_messages(session_id, limit)
        except Exception as e:
            logging.error(f"Erro ao recuperar histórico da sessão: {e}")
            return []
    
    def search_user_history(self, user_id: str, query: str, limit: int = 5) -> str:
        """
        Busca no histórico do usuário por termo específico
        
        Args:
            user_id: ID do usuário
            query: Termo de busca
            limit: Número de resultados
        
        Returns:
            String formatada com resultados
        """
        try:
            messages = self.supabase.search_user_messages(user_id, query, limit)
            
            if not messages:
                return f"Nenhuma conversa anterior encontrada sobre '{query}'."
            
            context_parts = [f"Conversas anteriores sobre '{query}':"]
            for msg in messages:
                context_parts.append(f"• {msg['user_message']} → {msg['agent_response']}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logging.error(f"Erro ao buscar histórico do usuário: {e}")
            return "Erro ao buscar no histórico."
    
    # ==================== MEMÓRIA EXTERNA (POSTGRESQL) ====================
    
    def save_to_external_memory(self, user_id: str, user_message: str, 
                              agent_response: str, agent_name: str = "Assistant") -> bool:
        """
        Salva conversa na memória externa (PostgreSQL) para contexto enriquecido
        
        Args:
            user_id: ID do usuário
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            agent_name: Nome do agente
        
        Returns:
            True se salvo com sucesso
        """
        try:
            # Salva no histórico de mensagens
            self.postgres_memory.save_message_history(
                user_id=user_id,
                user_message=user_message,
                assistant_response=agent_response,
                agent_name=agent_name
            )
            
            # Salva na memória enriquecida
            return self.postgres_memory.save_enriched_memory(
                user_id=user_id,
                content=f"Usuário: {user_message}\nAssistente: {agent_response}",
                metadata={
                    "agent_name": agent_name,
                    "interaction_type": "conversation"
                }
            )
        except Exception as e:
            logging.error(f"Erro ao salvar na memória externa PostgreSQL: {e}")
            return False
    
    def get_enriched_context(self, user_id: str, query: str, limit: int = 3) -> str:
        """
        Recupera contexto enriquecido da memória externa (PostgreSQL)
        
        Args:
            user_id: ID do usuário
            query: Mensagem atual para busca semântica
            limit: Número de memórias a recuperar
        
        Returns:
            String formatada com contexto enriquecido
        """
        try:
            memories = self.postgres_memory.search_memories(user_id, query, limit)
            
            if not memories:
                return "Nenhum contexto enriquecido disponível."
            
            context_parts = ["Contexto relevante das conversas anteriores:"]
            for memory in memories:
                similarity = memory.get('similarity', 0)
                content = memory.get('content', '')
                context_parts.append(f"• {content} (relevância: {similarity:.2f})")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logging.error(f"Erro ao recuperar contexto enriquecido PostgreSQL: {e}")
            return "Erro ao acessar memória contextual."
    
    # ==================== MEMÓRIA COMBINADA ====================
    
    def save_complete_interaction(self, user_id: str, session_id: str, agent_id: str,
                                user_message: str, agent_response: str, 
                                agent_name: str = "Assistant", message_id: str = None) -> Dict:
        """
        Salva interação completa em ambas as memórias
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            agent_id: ID do agente
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            agent_name: Nome do agente
            message_id: ID da mensagem (opcional)
        
        Returns:
            Dict com resultado das operações
        """
        results = {
            "internal_memory": False,
            "external_memory": False,
            "message_data": {}
        }
        
        # Salva na memória interna (Supabase)
        try:
            message_data = self.save_message_to_internal_memory(
                user_id, session_id, agent_id, user_message, agent_response, message_id
            )
            results["internal_memory"] = bool(message_data)
            results["message_data"] = message_data
        except Exception as e:
            logging.error(f"Falha na memória interna: {e}")
        
        # Salva na memória externa (PostgreSQL)
        try:
            external_success = self.save_to_external_memory(
                user_id, user_message, agent_response, agent_name
            )
            results["external_memory"] = external_success
        except Exception as e:
            logging.error(f"Falha na memória externa PostgreSQL: {e}")
        
        return results
    
    def get_complete_context(self, user_id: str, session_id: str, 
                           query: str = None, limit: int = 5) -> str:
        """
        Recupera contexto completo combinando ambas as memórias
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            query: Query para busca semântica (opcional)
            limit: Número de itens por fonte
        
        Returns:
            String formatada com contexto completo
        """
        context_parts = []
        
        # 1. Histórico da sessão atual (Supabase)
        try:
            session_history = self.get_session_history(session_id, limit)
            if session_history:
                context_parts.append("=== HISTÓRICO DA SESSÃO ATUAL ===")
                for msg in session_history[-3:]:  # Últimas 3 mensagens
                    context_parts.append(f"Usuário: {msg.get('user_message', '')}")
                    context_parts.append(f"Assistente: {msg.get('agent_response', '')}")
                context_parts.append("")
        except Exception as e:
            logging.error(f"Erro ao recuperar histórico da sessão: {e}")
        
        # 2. Contexto enriquecido (PostgreSQL)
        if query:
            try:
                enriched_context = self.get_enriched_context(user_id, query, limit)
                if enriched_context and "Nenhum contexto" not in enriched_context:
                    context_parts.append("=== CONTEXTO ENRIQUECIDO ===")
                    context_parts.append(enriched_context)
                    context_parts.append("")
            except Exception as e:
                logging.error(f"Erro ao recuperar contexto enriquecido: {e}")
        
        # 3. Busca específica no histórico do usuário (Supabase)
        if query:
            try:
                user_history = self.search_user_history(user_id, query, 3)
                if user_history and "Nenhuma conversa" not in user_history:
                    context_parts.append("=== HISTÓRICO RELACIONADO ===")
                    context_parts.append(user_history)
            except Exception as e:
                logging.error(f"Erro ao buscar histórico relacionado: {e}")
        
        if not context_parts:
            return "Nenhum contexto anterior disponível."
        
        return "\n".join(context_parts)
    
    def get_session_context(self, session_id: str, limit: int = 5) -> str:
        """
        Recupera apenas o contexto da sessão atual
        
        Args:
            session_id: ID da sessão
            limit: Número de mensagens
        
        Returns:
            String formatada com contexto da sessão
        """
        try:
            messages = self.get_session_history(session_id, limit)
            if not messages:
                return "Nenhum histórico da sessão disponível."
            
            context_parts = ["Histórico da conversa atual:"]
            for msg in messages:
                context_parts.append(f"Usuário: {msg.get('user_message', '')}")
                context_parts.append(f"Assistente: {msg.get('agent_response', '')}")
            
            return "\n".join(context_parts)
        except Exception as e:
            logging.error(f"Erro ao recuperar contexto da sessão: {e}")
            return "Erro ao acessar histórico da sessão."
    
    # ==================== MÉTODOS DE COMPATIBILIDADE ====================
    
    def search_memory(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """
        Busca memórias (compatibilidade com API anterior)
        
        Args:
            user_id: ID do usuário
            query: Query de busca
            limit: Número de resultados
        
        Returns:
            Lista de memórias encontradas
        """
        try:
            # Busca no PostgreSQL
            postgres_results = self.postgres_memory.search_memories(user_id, query, limit)
            
            # Busca no Supabase
            supabase_results = self.supabase.search_user_messages(user_id, query, limit)
            
            # Combina resultados
            combined_results = []
            
            # Adiciona resultados do PostgreSQL
            for result in postgres_results:
                combined_results.append({
                    "text": result.get('content', ''),
                    "source": "postgresql",
                    "similarity": result.get('similarity', 0),
                    "metadata": result.get('metadata', {})
                })
            
            # Adiciona resultados do Supabase
            for result in supabase_results:
                combined_results.append({
                    "text": f"Usuário: {result.get('user_message', '')}\nAssistente: {result.get('agent_response', '')}",
                    "source": "supabase",
                    "similarity": 0.8,  # Score fixo para resultados do Supabase
                    "metadata": {
                        "session_id": result.get('session_id', ''),
                        "agent_id": result.get('agent_id', '')
                    }
                })
            
            # Ordena por similaridade
            combined_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return combined_results[:limit]
            
        except Exception as e:
            logging.error(f"Erro na busca de memórias: {e}")
            return []
    
    def add_memory(self, user_id: str, content: str, metadata: Dict = None) -> bool:
        """
        Adiciona memória (compatibilidade com API anterior)
        
        Args:
            user_id: ID do usuário
            content: Conteúdo da memória
            metadata: Metadados opcionais
        
        Returns:
            True se adicionado com sucesso
        """
        try:
            return self.postgres_memory.save_enriched_memory(
                user_id=user_id,
                content=content,
                metadata=metadata or {}
            )
        except Exception as e:
            logging.error(f"Erro ao adicionar memória: {e}")
            return False

# Instância global para uso na API
postgres_dual_memory_service = PostgresDualMemoryService()