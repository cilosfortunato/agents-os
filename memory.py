import os
import logging
from typing import List, Dict, Any, Optional
from postgres_memory_system import PostgreSQLMemorySystem
import threading
import time

class TimeoutError(Exception):
    """Exceção customizada para timeout"""
    pass

class MemoryManager:
    """Gerenciador de memória usando PostgreSQL"""
    
    def __init__(self):
        # Configuração PostgreSQL usando variáveis do .env
        postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        postgres_port = os.getenv('POSTGRES_PORT', '5432')
        postgres_db = os.getenv('POSTGRES_DB', 'agnos_memory')
        postgres_user = os.getenv('POSTGRES_USER', 'postgres')
        postgres_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        
        connection_string = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        self.client = PostgreSQLMemorySystem(connection_string)
        self.timeout_seconds = 5  # Timeout de 5 segundos
    
    def _run_with_timeout(self, func, timeout_seconds=None):
        """Executa uma função com timeout usando threading (compatível com Windows)"""
        if timeout_seconds is None:
            timeout_seconds = self.timeout_seconds
            
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout_seconds)
        
        if thread.is_alive():
            # Thread ainda está rodando, significa timeout
            raise TimeoutError(f"Operação excedeu {timeout_seconds} segundos")
        
        if exception[0]:
            raise exception[0]
            
        return result[0]
    
    def add_memory(self, user_id: str, messages, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Adiciona uma nova memória para o usuário"""
        try:
            def _add():
                # Adapta para a interface PostgreSQL usando os métodos corretos
                session_id = metadata.get('session_id', 'default') if metadata else 'default'
                
                # Se messages é uma string, converte para formato de mensagem
                if isinstance(messages, str):
                    # Salva diretamente como memória enriquecida
                    self.client.save_memory(
                        user_id=user_id,
                        memory=messages,
                        category='user_input',
                        metadata=metadata or {}
                    )
                    return True
                
                # Se messages é uma lista, processa cada mensagem
                for message in messages:
                    # Usa save_message em vez de add_message
                    self.client.save_message(
                        session_id=session_id,
                        user_id=user_id,
                        role=message.get('role', 'user'),
                        content=message.get('content', ''),
                        metadata=metadata or {}
                    )
                    
                    # Se for uma mensagem do usuário, também salva como memória enriquecida
                    if message.get('role') == 'user' and message.get('content'):
                        self.client.save_memory(
                            user_id=user_id,
                            memory=message.get('content', ''),
                            category='conversation',
                            metadata=metadata or {}
                        )
                return True
            
            result = self._run_with_timeout(_add, self.timeout_seconds)
            logging.info(f"✅ Memória PostgreSQL adicionada para user_id: {user_id}")
            return True
        except TimeoutError:
            logging.warning(f"⚠️ Timeout PostgreSQL add ({self.timeout_seconds}s) para user {user_id}")
            return False
        except Exception as e:
            logging.error(f"⚠️ Erro ao adicionar memória PostgreSQL: {e}")
            return False
    
    def search_memories(self, user_id: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Busca memórias com timeout"""
        try:
            def _search():
                return self.client.search_memories(
                    user_id=user_id,
                    query=query,
                    limit=limit
                )
            
            memories = self._run_with_timeout(_search, self.timeout_seconds)
            
            if memories:
                logging.info(f"✅ PostgreSQL encontrou {len(memories)} memórias para user {user_id}")
                return memories
            else:
                logging.info(f"ℹ️ Nenhuma memória encontrada no PostgreSQL para user {user_id}")
                return []
                
        except TimeoutError:
            logging.warning(f"⚠️ Timeout PostgreSQL ({self.timeout_seconds}s) para user {user_id}")
            return []
        except Exception as e:
            logging.warning(f"⚠️ Erro PostgreSQL: {e}")
            return []
    
    def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Recupera todas as memórias de um usuário"""
        try:
            def _get_all():
                # Usa get_all_user_memories em vez de get_user_messages
                return self.client.get_all_user_memories(user_id=user_id, limit=50)
            
            memories = self._run_with_timeout(_get_all, self.timeout_seconds)
            return memories or []
        except TimeoutError:
            logging.warning(f"⚠️ Timeout PostgreSQL get_all ({self.timeout_seconds}s) para user {user_id}")
            return []
        except Exception as e:
            logging.error(f"⚠️ Erro ao recuperar memórias PostgreSQL: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Remove uma memória específica - PostgreSQL não implementado"""
        logging.warning("⚠️ delete_memory não implementado para PostgreSQL")
        return False
    
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza uma memória existente - PostgreSQL não implementado"""
        logging.warning("⚠️ update_memory não implementado para PostgreSQL")
        return False
    
    def format_memories_for_context(self, memories: List[Dict[str, Any]]) -> str:
        """Formata memórias para uso como contexto em conversas"""
        if not memories:
            return "Nenhuma memória relevante encontrada."
        
        context_parts = []
        for memory in memories:
            if 'text' in memory:
                context_parts.append(f"- {memory['text']}")
            elif 'content' in memory:
                context_parts.append(f"- {memory['content']}")
        
        return "\n".join(context_parts)
    
    def save_conversation(self, user_id: str, user_message: str, assistant_response: str, agent_name: str = "Assistant") -> bool:
        """Salva uma conversa completa na memória"""
        messages = [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response}
        ]
        
        metadata = {
            "agent_name": agent_name,
            "conversation_type": "chat"
        }
        
        return self.add_memory(user_id, messages, metadata)

# Instância global do gerenciador de memória
memory_manager = MemoryManager()