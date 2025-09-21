#!/usr/bin/env python3
"""
Sistema de Memória PostgreSQL com pgvector
Baseado no exemplo memoria_pgvector
"""
import psycopg2
import psycopg2.extras
import json
from openai import OpenAI
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import os

# Configuração da OpenAI - Nova API
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
)

class PostgreSQLMemorySystem:
    """Sistema de memória usando PostgreSQL com pgvector"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.init_database()
    
    def get_connection(self):
        """Retorna conexão PostgreSQL"""
        return psycopg2.connect(self.connection_string)
    
    def init_database(self):
        """Inicializa o banco PostgreSQL com as tabelas e extensão pgvector"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Habilita a extensão pgvector
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ Extensão pgvector habilitada")
            
            # Tabela de histórico de mensagens
            cur.execute("""
                CREATE TABLE IF NOT EXISTS message_history (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Tabela message_history criada")
            
            # Índices para performance
            cur.execute("CREATE INDEX IF NOT EXISTS idx_session_messages ON message_history(session_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_user_messages ON message_history(user_id);")
            print("✅ Índices de message_history criados")
            
            # Tabela de memórias enriquecidas com pgvector
            cur.execute("""
                CREATE TABLE IF NOT EXISTS enriched_memories (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    memory TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    embedding vector(1536),  -- OpenAI ada-002 tem 1536 dimensões
                    metadata JSONB DEFAULT '{}',
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            print("✅ Tabela enriched_memories criada")
            
            # Índices para busca vetorial
            cur.execute("CREATE INDEX IF NOT EXISTS idx_user_memories ON enriched_memories(user_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_category ON enriched_memories(category);")
            
            # Índice HNSW para busca vetorial eficiente
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_embedding_hnsw ON enriched_memories USING hnsw (embedding vector_cosine_ops);")
                print("✅ Índice HNSW para busca vetorial criado")
            except Exception as e:
                print(f"⚠️ Aviso: Não foi possível criar índice HNSW: {e}")
                # Cria índice IVFFlat como alternativa
                try:
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_embedding_ivf ON enriched_memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);")
                    print("✅ Índice IVFFlat para busca vetorial criado")
                except Exception as e2:
                    print(f"⚠️ Aviso: Não foi possível criar índice IVFFlat: {e2}")
            
            conn.commit()
            print("✅ Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
    
    # ============ HISTÓRICO DE MENSAGENS ============
    
    def save_message(self, session_id: str, user_id: str, role: str, content: str, metadata: Dict = None):
        """Salva uma mensagem no histórico"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            metadata = metadata or {}
            cur.execute("""
                INSERT INTO message_history (session_id, user_id, role, content, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, user_id, role, content, json.dumps(metadata)))
            
            conn.commit()
        except Exception as e:
            print(f"Erro ao salvar mensagem: {e}")
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Recupera histórico de uma sessão"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cur.execute("""
                SELECT role, content, metadata, created_at 
                FROM message_history 
                WHERE session_id = %s 
                ORDER BY created_at DESC
                LIMIT %s
            """, (session_id, limit))
            
            messages = []
            for row in cur.fetchall():
                messages.append({
                    'role': row['role'],
                    'content': row['content'],
                    'metadata': row['metadata'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None
                })
            
            return list(reversed(messages))  # Retorna em ordem cronológica
            
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    # ============ MEMÓRIA ENRIQUECIDA ============
    
    def get_embedding(self, text: str) -> List[float]:
        """Gera embedding do texto usando OpenAI"""
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Erro ao gerar embedding: {e}")
            # Retorna um vetor dummy para teste
            return [0.0] * 1536
    
    def save_memory(self, user_id: str, memory: str, category: str = "general", metadata: Dict = None):
        """Salva uma memória enriquecida com embedding"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Gera embedding
            embedding = self.get_embedding(memory)
            metadata = metadata or {}
            
            # Salva no banco
            cur.execute("""
                INSERT INTO enriched_memories (user_id, memory, category, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, memory, category, embedding, json.dumps(metadata)))
            
            conn.commit()
            
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()
    
    def search_memories(self, user_id: str, query: str, limit: int = 5, similarity_threshold: float = 0.7) -> List[Dict]:
        """Busca memórias relevantes usando similaridade cosseno com pgvector"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            # Gera embedding da query
            query_embedding = self.get_embedding(query)
            
            # Busca usando similaridade cosseno do pgvector
            cur.execute("""
                SELECT 
                    memory, 
                    category, 
                    metadata,
                    created_at,
                    1 - (embedding <=> %s::vector) as similarity
                FROM enriched_memories
                WHERE user_id = %s
                    AND 1 - (embedding <=> %s::vector) > %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, user_id, query_embedding, similarity_threshold, query_embedding, limit))
            
            memories = []
            for row in cur.fetchall():
                memories.append({
                    'memory': row['memory'],
                    'category': row['category'],
                    'metadata': row['metadata'],
                    'similarity': float(row['similarity']),
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None
                })
            
            return memories
            
        except Exception as e:
            print(f"Erro ao buscar memórias: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def get_all_user_memories(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Recupera todas as memórias de um usuário"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cur.execute("""
                SELECT memory, category, metadata, created_at
                FROM enriched_memories
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            memories = []
            for row in cur.fetchall():
                memories.append({
                    'memory': row['memory'],
                    'category': row['category'],
                    'metadata': row['metadata'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None
                })
            
            return memories
            
        except Exception as e:
            print(f"Erro ao buscar memórias do usuário: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    # ============ MÉTODO PRINCIPAL ============
    
    def extract_facts(self, user_message: str, assistant_response: str) -> List[str]:
        """Extrai fatos importantes da conversa usando GPT"""
        try:
            prompt = f"""
            Extraia fatos importantes desta conversa.
            Retorne apenas fatos objetivos sobre o usuário, um por linha.
            Ignore informações genéricas ou temporárias.
            
            Usuário: {user_message}
            Assistente: {assistant_response}
            
            Fatos importantes:
            """
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extraia apenas informações importantes e duradouras sobre o usuário."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            facts = response.choices[0].message.content.strip().split('\n')
            return [f.strip() for f in facts if f.strip() and len(f.strip()) > 10]
        except Exception as e:
            print(f"Erro ao extrair fatos: {e}")
            return []
    
    def process_and_save(self, session_id: str, user_id: str, user_message: str, assistant_response: str):
        """Método principal: salva histórico e extrai memórias"""
        try:
            # 1. Salva no histórico
            self.save_message(session_id, user_id, "user", user_message)
            self.save_message(session_id, user_id, "assistant", assistant_response)
            
            # 2. Extrai fatos importantes
            facts = self.extract_facts(user_message, assistant_response)
            
            # 3. Salva cada fato como memória
            saved_facts = []
            for fact in facts:
                if fact and len(fact.strip()) > 10:  # Só salva se não estiver vazio e tiver conteúdo
                    try:
                        self.save_memory(user_id, fact)
                        saved_facts.append(fact)
                    except Exception as e:
                        print(f"Erro ao salvar fato '{fact}': {e}")
            
            return saved_facts
            
        except Exception as e:
            print(f"Erro no processamento: {e}")
            return []
    
    def get_context(self, user_id: str, current_message: str = "", session_id: str = "") -> str:
        """Recupera contexto completo para o agente"""
        context_parts = []
        
        try:
            # Busca memórias relevantes se houver mensagem atual
            if current_message:
                relevant = self.search_memories(user_id, current_message, limit=3)
                if relevant:
                    context_parts.append("Informações relevantes sobre o usuário:")
                    for mem in relevant:
                        context_parts.append(f"• {mem['memory']} (similaridade: {mem['similarity']:.2f})")
            
            # Busca histórico recente da sessão
            if session_id:
                history = self.get_history(session_id, limit=6)  # Últimas 3 trocas
                if history:
                    context_parts.append("\nHistórico recente da conversa:")
                    for msg in history[-6:]:  # Últimas 6 mensagens
                        role_emoji = "👤" if msg['role'] == "user" else "🤖"
                        context_parts.append(f"{role_emoji} {msg['content'][:100]}...")
            
            # Busca memórias gerais (limitado)
            all_memories = self.get_all_user_memories(user_id, limit=5)
            if all_memories:
                context_parts.append("\nO que sei sobre o usuário:")
                for mem in all_memories:
                    context_parts.append(f"• {mem['memory']}")
            
        except Exception as e:
            print(f"Erro ao gerar contexto: {e}")
            context_parts.append("Erro ao recuperar contexto da memória.")
        
        return "\n".join(context_parts) if context_parts else ""

def test_postgres_memory():
    """Testa o sistema de memória PostgreSQL"""
    print("🧠 TESTANDO SISTEMA DE MEMÓRIA POSTGRESQL")
    print("=" * 60)
    
    # String de conexão fornecida
    connection_string = "postgres://postgres:329fe52ffbdf73289f3c@painel.doxagrowth.com.br:5523/agentes-python?sslmode=disable"
    
    try:
        # Inicializa o sistema
        print("Inicializando sistema de memória...")
        memory = PostgreSQLMemorySystem(connection_string)
        
        # 1. Testa salvar mensagem
        print("\n1. Testando histórico de mensagens...")
        memory.save_message("teste_sessao", "teste_user", "user", "Olá, meu nome é João e trabalho com tecnologia")
        memory.save_message("teste_sessao", "teste_user", "assistant", "Olá João! Prazer em conhecê-lo. Como posso ajudar?")
        print("✅ Histórico funcionando")
        
        # 2. Testa salvar memória
        print("\n2. Testando memória enriquecida...")
        memory.save_memory("teste_user", "Usuário se chama João", "personal")
        memory.save_memory("teste_user", "Usuário trabalha com tecnologia", "professional")
        print("✅ Memória enriquecida funcionando")
        
        # 3. Testa buscar memórias
        print("\n3. Testando busca de memórias...")
        memorias = memory.search_memories("teste_user", "nome do usuário", limit=3)
        print(f"✅ Busca funcionando: {len(memorias)} memórias encontradas")
        for i, mem in enumerate(memorias, 1):
            print(f"   {i}. {mem['memory']} (similaridade: {mem['similarity']:.2f})")
        
        # 4. Testa contexto completo
        print("\n4. Testando contexto completo...")
        contexto = memory.get_context("teste_user", "Qual é meu nome?", "teste_sessao")
        print(f"✅ Contexto gerado ({len(contexto)} caracteres)")
        print(f"Contexto:\n{contexto}")
        
        # 5. Testa processamento completo
        print("\n5. Testando processamento completo...")
        facts = memory.process_and_save(
            "teste_sessao", 
            "teste_user", 
            "Eu moro em São Paulo e tenho 30 anos",
            "Que legal! São Paulo é uma cidade incrível. Como posso ajudar?"
        )
        print(f"✅ Processamento completo: {len(facts)} fatos extraídos")
        for fact in facts:
            print(f"   • {fact}")
        
        print("\n" + "=" * 60)
        print("🎉 SISTEMA DE MEMÓRIA POSTGRESQL FUNCIONANDO!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_postgres_memory()