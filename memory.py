from mem0 import MemoryClient
from typing import List, Dict, Any, Optional
from config import Config
import logging

class MemoryManager:
    """Gerenciador de memória usando Mem0 AI"""
    
    def __init__(self):
        self.client = MemoryClient()
        self.collection = Config.MEMORY_COLLECTION
        
    def add_memory(self, user_id: str, messages: List[Dict[str, str]], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Adiciona uma nova memória para o usuário"""
        try:
            result = self.client.add(
                messages=messages,
                user_id=user_id,
                metadata=metadata or {}
            )
            logging.info(f"Memória adicionada para user_id: {user_id}")
            return True
        except Exception as e:
            logging.error(f"Erro ao adicionar memória: {e}")
            return False
    
    def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca memórias relevantes para o usuário"""
        try:
            memories = self.client.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            return memories or []
        except Exception as e:
            logging.error(f"Erro ao buscar memórias: {e}")
            return []
    
    def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Recupera todas as memórias de um usuário"""
        try:
            memories = self.client.get_all(user_id=user_id)
            return memories or []
        except Exception as e:
            logging.error(f"Erro ao recuperar memórias: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Remove uma memória específica"""
        try:
            self.client.delete(memory_id=memory_id)
            logging.info(f"Memória removida: {memory_id}")
            return True
        except Exception as e:
            logging.error(f"Erro ao remover memória: {e}")
            return False
    
    def update_memory(self, memory_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza uma memória existente"""
        try:
            self.client.update(memory_id=memory_id, data=data)
            logging.info(f"Memória atualizada: {memory_id}")
            return True
        except Exception as e:
            logging.error(f"Erro ao atualizar memória: {e}")
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