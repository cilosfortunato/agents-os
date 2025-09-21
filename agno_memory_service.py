#!/usr/bin/env python3
"""
Serviço de Memórias do Agno - Implementação das APIs create-memory e list-memories
Usa a tabela message_history existente no Supabase para armazenar memórias enriquecidas
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

class AgnoMemoryService:
    """Serviço de memórias do Agno usando Supabase"""
    
    def __init__(self):
        """Inicializa o serviço de memórias"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Credenciais do Supabase não encontradas")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✅ Serviço de memórias do Agno inicializado")
    
    def create_memory(self, 
                     memory: str, 
                     user_id: str, 
                     agent_id: Optional[str] = None,
                     session_id: Optional[str] = None,
                     topics: Optional[List[str]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Cria uma nova memória no sistema
        
        Args:
            memory: Conteúdo da memória
            user_id: ID do usuário
            agent_id: ID do agente (opcional)
            session_id: ID da sessão (opcional)
            topics: Lista de tópicos relacionados (opcional)
            metadata: Metadados adicionais (opcional)
            
        Returns:
            Dict com informações da memória criada
        """
        try:
            # Gerar ID único para a memória
            memory_id = str(uuid.uuid4())
            
            # Preparar metadados
            memory_metadata = {
                "memory_id": memory_id,
                "type": "enriched_memory",
                "topics": topics or [],
                "agent_id": agent_id,
                **(metadata or {})
            }
            
            # Dados para inserir na tabela message_history
            memory_data = {
                "session_id": session_id or f"memory-session-{memory_id[:8]}",
                "user_id": user_id,
                "role": "system",  # Memórias são do tipo system
                "content": memory,
                "metadata": memory_metadata
            }
            
            # Inserir na tabela message_history
            result = self.supabase.table("message_history").insert(memory_data).execute()
            
            if result.data:
                created_memory = result.data[0]
                print(f"✅ Memória criada: {memory_id}")
                
                return {
                    "memory_id": memory_id,
                    "id": created_memory["id"],
                    "memory": memory,
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "session_id": created_memory["session_id"],
                    "topics": topics or [],
                    "metadata": memory_metadata,
                    "created_at": created_memory["created_at"],
                    "status": "created"
                }
            else:
                raise Exception("Falha ao inserir memória")
                
        except Exception as e:
            print(f"❌ Erro ao criar memória: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def list_memories(self, 
                     user_id: str, 
                     agent_id: Optional[str] = None,
                     limit: int = 10,
                     topics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Lista memórias do usuário
        
        Args:
            user_id: ID do usuário
            agent_id: ID do agente (opcional)
            limit: Limite de resultados
            topics: Filtrar por tópicos (opcional)
            
        Returns:
            Dict com lista de memórias
        """
        try:
            # Construir query base
            query = self.supabase.table("message_history").select("*")
            
            # Filtros
            query = query.eq("user_id", user_id)
            query = query.eq("role", "system")  # Apenas memórias (role=system)
            
            # Filtrar por agent_id se fornecido
            if agent_id:
                query = query.contains("metadata", {"agent_id": agent_id})
            
            # Filtrar por type=enriched_memory
            query = query.contains("metadata", {"type": "enriched_memory"})
            
            # Ordenar por data de criação (mais recentes primeiro)
            query = query.order("created_at", desc=True)
            
            # Aplicar limite
            query = query.limit(limit)
            
            # Executar query
            result = query.execute()
            
            memories = []
            for row in result.data:
                metadata = row.get("metadata", {})
                
                # Filtrar por tópicos se especificado
                if topics:
                    row_topics = metadata.get("topics", [])
                    if not any(topic in row_topics for topic in topics):
                        continue
                
                memory_info = {
                    "memory_id": metadata.get("memory_id", f"mem-{row['id']}"),
                    "id": row["id"],
                    "memory": row["content"],
                    "user_id": row["user_id"],
                    "agent_id": metadata.get("agent_id"),
                    "session_id": row["session_id"],
                    "topics": metadata.get("topics", []),
                    "metadata": metadata,
                    "created_at": row["created_at"]
                }
                memories.append(memory_info)
            
            print(f"✅ Encontradas {len(memories)} memórias para user_id: {user_id}")
            
            return {
                "memories": memories,
                "count": len(memories),
                "user_id": user_id,
                "agent_id": agent_id,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Erro ao listar memórias: {e}")
            return {
                "memories": [],
                "count": 0,
                "error": str(e),
                "status": "failed"
            }
    
    def update_memory(self, memory_id: str, memory: str, topics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Atualiza uma memória existente
        
        Args:
            memory_id: ID da memória
            memory: Novo conteúdo
            topics: Novos tópicos (opcional)
            
        Returns:
            Dict com resultado da atualização
        """
        try:
            # Buscar a memória existente
            result = self.supabase.table("message_history").select("*").contains("metadata", {"memory_id": memory_id}).execute()
            
            if not result.data:
                return {"error": "Memória não encontrada", "status": "not_found"}
            
            existing_memory = result.data[0]
            existing_metadata = existing_memory.get("metadata", {})
            
            # Atualizar metadados
            updated_metadata = existing_metadata.copy()
            if topics is not None:
                updated_metadata["topics"] = topics
            
            # Dados para atualização
            update_data = {
                "content": memory,
                "metadata": updated_metadata
            }
            
            # Atualizar no banco
            update_result = self.supabase.table("message_history").update(update_data).eq("id", existing_memory["id"]).execute()
            
            if update_result.data:
                print(f"✅ Memória atualizada: {memory_id}")
                return {
                    "memory_id": memory_id,
                    "memory": memory,
                    "topics": topics,
                    "status": "updated"
                }
            else:
                return {"error": "Falha na atualização", "status": "failed"}
                
        except Exception as e:
            print(f"❌ Erro ao atualizar memória: {e}")
            return {"error": str(e), "status": "failed"}
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Remove uma memória
        
        Args:
            memory_id: ID da memória
            
        Returns:
            Dict com resultado da remoção
        """
        try:
            # Buscar e remover a memória
            result = self.supabase.table("message_history").delete().contains("metadata", {"memory_id": memory_id}).execute()
            
            if result.data:
                print(f"✅ Memória removida: {memory_id}")
                return {"memory_id": memory_id, "status": "deleted"}
            else:
                return {"error": "Memória não encontrada", "status": "not_found"}
                
        except Exception as e:
            print(f"❌ Erro ao remover memória: {e}")
            return {"error": str(e), "status": "failed"}
    
    def get_memory_statistics(self, user_id: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém estatísticas das memórias
        
        Args:
            user_id: ID do usuário
            agent_id: ID do agente (opcional)
            
        Returns:
            Dict com estatísticas
        """
        try:
            # Query base
            query = self.supabase.table("message_history").select("*", count="exact")
            query = query.eq("user_id", user_id)
            query = query.eq("role", "system")
            query = query.contains("metadata", {"type": "enriched_memory"})
            
            if agent_id:
                query = query.contains("metadata", {"agent_id": agent_id})
            
            result = query.execute()
            
            total_memories = result.count or 0
            
            # Contar tópicos únicos
            topics_set = set()
            for row in result.data:
                metadata = row.get("metadata", {})
                topics = metadata.get("topics", [])
                topics_set.update(topics)
            
            return {
                "user_id": user_id,
                "agent_id": agent_id,
                "total_memories": total_memories,
                "unique_topics": len(topics_set),
                "topics_list": list(topics_set),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {"error": str(e), "status": "failed"}

def test_memory_service():
    """Testa o serviço de memórias"""
    print("🧪 Testando serviço de memórias do Agno...")
    
    try:
        # Inicializar serviço
        memory_service = AgnoMemoryService()
        
        # Dados de teste
        test_user_id = "test-user-123"
        test_agent_id = "test-agent-456"
        test_memory = "Usuário prefere respostas técnicas e detalhadas sobre programação"
        test_topics = ["preferencias", "programacao", "estilo"]
        
        # Teste 1: Criar memória
        print("\n1️⃣ Testando criação de memória...")
        create_result = memory_service.create_memory(
            memory=test_memory,
            user_id=test_user_id,
            agent_id=test_agent_id,
            topics=test_topics
        )
        print(f"Resultado: {create_result}")
        
        if create_result.get("status") == "created":
            memory_id = create_result["memory_id"]
            
            # Teste 2: Listar memórias
            print("\n2️⃣ Testando listagem de memórias...")
            list_result = memory_service.list_memories(
                user_id=test_user_id,
                agent_id=test_agent_id
            )
            print(f"Memórias encontradas: {list_result.get('count', 0)}")
            
            # Teste 3: Estatísticas
            print("\n3️⃣ Testando estatísticas...")
            stats_result = memory_service.get_memory_statistics(
                user_id=test_user_id,
                agent_id=test_agent_id
            )
            print(f"Estatísticas: {stats_result}")
            
            # Teste 4: Atualizar memória
            print("\n4️⃣ Testando atualização de memória...")
            update_result = memory_service.update_memory(
                memory_id=memory_id,
                memory="Usuário prefere respostas técnicas, detalhadas e com exemplos práticos",
                topics=["preferencias", "programacao", "estilo", "exemplos"]
            )
            print(f"Atualização: {update_result}")
            
            # Teste 5: Remover memória de teste
            print("\n5️⃣ Limpando memória de teste...")
            delete_result = memory_service.delete_memory(memory_id)
            print(f"Remoção: {delete_result}")
            
            print("\n✅ Todos os testes concluídos!")
        else:
            print("❌ Falha na criação da memória - testes interrompidos")
            
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")

if __name__ == "__main__":
    test_memory_service()