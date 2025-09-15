from typing import List, Dict, Any, Optional
import os
from fastapi import HTTPException
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

try:
    from agno.knowledge import Knowledge, Source, VectorDB
except ImportError:
    logger.warning("Agno não está disponível. Usando implementação mock para desenvolvimento.")
    
    class MockVectorDB:
        def __init__(self, provider: str, config: Dict[str, Any]):
            self.provider = provider
            self.config = config
    
    class MockSource:
        def __init__(self, id: str, type: str, config: Dict[str, Any]):
            self.id = id
            self.type = type
            self.config = config
    
    class MockKnowledge:
        def __init__(self, id: str, vectordb: Any, sources: List[Any]):
            self.id = id
            self.vectordb = vectordb
            self.sources = sources
        
        def sync(self):
            logger.info(f"Mock sync para knowledge {self.id}")
            return True
        
        def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
            # Simulação de resultados de busca
            return [
                {
                    "content": f"Resultado simulado para: {query}",
                    "score": 0.95,
                    "metadata": {"source": "manual_produto.txt"}
                }
            ]
    
    VectorDB = MockVectorDB
    Source = MockSource
    Knowledge = MockKnowledge

class KnowledgeManager:
    """Gerenciador da base de conhecimento com Pinecone"""
    
    def __init__(self):
        self.knowledge_bases: Dict[str, Knowledge] = {}
        self._initialize_default_knowledge()
    
    def _initialize_default_knowledge(self):
        """Inicializa a base de conhecimento padrão"""
        try:
            # Configura a conexão com o Pinecone
            pinecone_db = VectorDB(
                provider="pinecone",
                config={
                    "index": "agno-knowledge-base",
                    "environment": "gcp-starter"
                }
            )
            
            # Fonte do manual do produto
            fonte_manual = Source(
                id="manual-produto-v1",
                type="file",
                config={"path": "./manual_produto.txt"}
            )
            
            # Base de conhecimento principal
            base_conhecimento = Knowledge(
                id="knowledge-produto-v1",
                vectordb=pinecone_db,
                sources=[fonte_manual]
            )
            
            self.knowledge_bases["produto"] = base_conhecimento
            logger.info("Base de conhecimento padrão inicializada")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar base de conhecimento: {e}")
    
    def sync_knowledge_base(self, knowledge_id: str = "produto") -> bool:
        """Sincroniza uma base de conhecimento específica"""
        try:
            if knowledge_id not in self.knowledge_bases:
                raise HTTPException(status_code=404, detail=f"Base de conhecimento '{knowledge_id}' não encontrada")
            
            knowledge = self.knowledge_bases[knowledge_id]
            knowledge.sync()
            logger.info(f"Base de conhecimento '{knowledge_id}' sincronizada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar base de conhecimento '{knowledge_id}': {e}")
            raise HTTPException(status_code=500, detail=f"Erro na sincronização: {str(e)}")
    
    def search_knowledge(self, query: str, knowledge_id: str = "produto", limit: int = 5) -> List[Dict[str, Any]]:
        """Busca informações na base de conhecimento"""
        try:
            if knowledge_id not in self.knowledge_bases:
                raise HTTPException(status_code=404, detail=f"Base de conhecimento '{knowledge_id}' não encontrada")
            
            knowledge = self.knowledge_bases[knowledge_id]
            results = knowledge.search(query, limit=limit)
            
            logger.info(f"Busca realizada na base '{knowledge_id}' com {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca da base de conhecimento '{knowledge_id}': {e}")
            raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")
    
    def add_knowledge_source(self, knowledge_id: str, source_config: Dict[str, Any]) -> bool:
        """Adiciona uma nova fonte à base de conhecimento"""
        try:
            if knowledge_id not in self.knowledge_bases:
                raise HTTPException(status_code=404, detail=f"Base de conhecimento '{knowledge_id}' não encontrada")
            
            # Cria nova fonte
            new_source = Source(
                id=source_config.get("id", f"source-{len(self.knowledge_bases[knowledge_id].sources)}"),
                type=source_config.get("type", "file"),
                config=source_config.get("config", {})
            )
            
            # Adiciona à base existente
            knowledge = self.knowledge_bases[knowledge_id]
            knowledge.sources.append(new_source)
            
            logger.info(f"Nova fonte adicionada à base '{knowledge_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar fonte à base '{knowledge_id}': {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao adicionar fonte: {str(e)}")
    
    def create_knowledge_base(self, knowledge_id: str, config: Dict[str, Any]) -> bool:
        """Cria uma nova base de conhecimento"""
        try:
            if knowledge_id in self.knowledge_bases:
                raise HTTPException(status_code=400, detail=f"Base de conhecimento '{knowledge_id}' já existe")
            
            # Configura VectorDB
            vectordb_config = config.get("vectordb", {
                "provider": "pinecone",
                "config": {
                    "index": "agno-knowledge-base",
                    "environment": "gcp-starter"
                }
            })
            
            vector_db = VectorDB(
                provider=vectordb_config["provider"],
                config=vectordb_config["config"]
            )
            
            # Configura fontes
            sources = []
            for source_config in config.get("sources", []):
                source = Source(
                    id=source_config["id"],
                    type=source_config["type"],
                    config=source_config["config"]
                )
                sources.append(source)
            
            # Cria base de conhecimento
            knowledge = Knowledge(
                id=knowledge_id,
                vectordb=vector_db,
                sources=sources
            )
            
            self.knowledge_bases[knowledge_id] = knowledge
            logger.info(f"Base de conhecimento '{knowledge_id}' criada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar base de conhecimento '{knowledge_id}': {e}")
            raise HTTPException(status_code=500, detail=f"Erro na criação: {str(e)}")
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """Lista todas as bases de conhecimento disponíveis"""
        try:
            bases = []
            for kb_id, knowledge in self.knowledge_bases.items():
                bases.append({
                    "id": kb_id,
                    "knowledge_id": knowledge.id,
                    "sources_count": len(knowledge.sources),
                    "vectordb_provider": knowledge.vectordb.provider
                })
            
            return bases
            
        except Exception as e:
            logger.error(f"Erro ao listar bases de conhecimento: {e}")
            raise HTTPException(status_code=500, detail=f"Erro na listagem: {str(e)}")

# Instância global do gerenciador
knowledge_manager = KnowledgeManager()