import os
import logging
from typing import List, Dict, Any, Optional
from mem0 import MemoryClient
import threading
import time

class TimeoutError(Exception):
    """Exceção customizada para timeout"""
    pass

class MemoryManager:
    """Gerenciador de memória usando Mem0"""
    
    def __init__(self):
        self.client = MemoryClient()
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
    
    def add_memory(self, user_id: str, messages: List[Dict[str, str]], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Adiciona uma nova memória para o usuário"""
        try:
            def _add():
                return self.client.add(
                    messages=messages,
                    user_id=user_id,
                    metadata=metadata or {}
                )
            
            result = self._run_with_timeout(_add, self.timeout_seconds)
            logging.info(f"✅ Memória adicionada para user_id: {user_id}")
            return True
        except TimeoutError:
            logging.warning(f"⚠️ Timeout Mem0 add ({self.timeout_seconds}s) para user {user_id}")
            return False
        except Exception as e:
            logging.error(f"⚠️ Erro ao adicionar memória: {e}")
            return False
    
    def search_memories(self, user_id: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Busca memórias com timeout"""
        try:
            def _search():
                return self.client.search(
                    query=query,
                    user_id=user_id,
                    limit=limit
                )
            
            memories = self._run_with_timeout(_search, self.timeout_seconds)
            
            if memories:
                logging.info(f"✅ Mem0 encontrou {len(memories)} memórias para user {user_id}")
                return memories
            else:
                logging.info(f"ℹ️ Nenhuma memória encontrada no Mem0 para user {user_id}")
                return []
                
        except TimeoutError:
            logging.warning(f"⚠️ Timeout Mem0 ({self.timeout_seconds}s) para user {user_id}")
            return []
        except Exception as e:
            logging.warning(f"⚠️ Erro Mem0: {e}")
            return []
    
    def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Recupera todas as memórias de um usuário"""
        try:
            def _get_all():
                return self.client.get_all(user_id=user_id)
            
            memories = self._run_with_timeout(_get_all, self.timeout_seconds)
            return memories or []
        except TimeoutError:
            logging.warning(f"⚠️ Timeout Mem0 get_all ({self.timeout_seconds}s) para user {user_id}")
            return []
        except Exception as e:
            logging.error(f"⚠️ Erro ao recuperar memórias: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Remove uma memória específica"""
        try:
            def _delete():
                return self.client.delete(memory_id=memory_id)
            
            self._run_with_timeout(_delete, self.timeout_seconds)
            logging.info(f"✅ Memória removida: {memory_id}")
            return True
        except TimeoutError:
            logging.warning(f"⚠️ Timeout Mem0 delete ({self.timeout_seconds}s) para memory {memory_id}")
            return False
        except Exception as e:
            logging.error(f"⚠️ Erro ao remover memória: {e}")
            return False
    
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza uma memória existente"""
        try:
            def _update():
                return self.client.update(memory_id=memory_id, data=data)
            
            self._run_with_timeout(_update, self.timeout_seconds)
            logging.info(f"✅ Memória atualizada: {memory_id}")
            return True
        except TimeoutError:
            logging.warning(f"⚠️ Timeout Mem0 update ({self.timeout_seconds}s) para memory {memory_id}")
            return False
        except Exception as e:
            logging.error(f"⚠️ Erro ao atualizar memória: {e}")
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