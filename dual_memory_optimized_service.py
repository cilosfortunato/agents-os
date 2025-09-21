#!/usr/bin/env python3
"""
Serviço de Memória Dual Otimizada
Implementa a arquitetura separada entre:
- mensagens_ia: Histórico bruto de conversa (pergunta-resposta)
- message_history: Memória enriquecida (fatos, preferências, resumos, contexto)
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

class DualMemoryOptimizedService:
    """Serviço de memória dual otimizada para chat e contexto enriquecido"""
    
    def __init__(self):
        """Inicializa o serviço de memória dual"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Credenciais do Supabase não encontradas")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✅ Serviço de memória dual otimizada inicializado")
    
    # ==================== MENSAGENS_IA - HISTÓRICO BRUTO ====================
    
    def save_chat_message(self, 
                         user_id: str,
                         session_id: str,
                         agent_id: str,
                         user_message: str,
                         agent_response: str,
                         agent_name: Optional[str] = None,
                         message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Salva uma conversa completa na tabela mensagens_ia (histórico bruto)
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            agent_id: ID do agente
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            agent_name: Nome do agente (opcional)
            message_id: ID da mensagem (opcional)
            
        Returns:
            Dict com informações da mensagem salva
        """
        try:
            message_data = {
                "user_id": user_id,
                "session_id": session_id,
                "agent_id": agent_id,
                "user_message": user_message,
                "agent_response": agent_response,
                "message_id": message_id or str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat()
            }
            
            # Adiciona agent_name apenas se a coluna existir na tabela
            # if agent_name:
            #     message_data["agent_name"] = agent_name
            
            result = self.supabase.table("mensagens_ia").insert(message_data).execute()
            
            if result.data:
                saved_message = result.data[0]
                print(f"✅ Mensagem salva em mensagens_ia: {saved_message['id']}")
                return {
                    "id": saved_message["id"],
                    "message_id": saved_message["message_id"],
                    "status": "saved",
                    "table": "mensagens_ia"
                }
            else:
                raise Exception("Falha ao inserir mensagem")
                
        except Exception as e:
            print(f"❌ Erro ao salvar mensagem em mensagens_ia: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "table": "mensagens_ia"
            }
    
    def get_chat_history(self, 
                        user_id: str, 
                        session_id: Optional[str] = None,
                        agent_id: Optional[str] = None,
                        limit: int = 20) -> List[Dict[str, Any]]:
        """
        Recupera histórico de chat da tabela mensagens_ia
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão (opcional)
            agent_id: ID do agente (opcional)
            limit: Limite de mensagens
            
        Returns:
            Lista de mensagens do histórico
        """
        try:
            query = self.supabase.table("mensagens_ia").select("*")
            query = query.eq("user_id", user_id)
            
            if session_id:
                query = query.eq("session_id", session_id)
            
            if agent_id:
                query = query.eq("agent_id", agent_id)
            
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            
            messages = result.data or []
            print(f"✅ Recuperadas {len(messages)} mensagens do histórico")
            return messages
            
        except Exception as e:
            print(f"❌ Erro ao recuperar histórico: {e}")
            return []
    
    # ==================== MESSAGE_HISTORY - MEMÓRIA ENRIQUECIDA ====================
    
    def create_enriched_memory(self,
                              user_id: str,
                              session_id: str,
                              agent_id: str,
                              memory_content: str,
                              memory_type: str = "enriched_memory",
                              topics: Optional[List[str]] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Cria uma memória enriquecida na tabela message_history
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            agent_id: ID do agente
            memory_content: Conteúdo da memória enriquecida
            memory_type: Tipo da memória (fact, preference, summary, etc.)
            topics: Lista de tópicos relacionados
            metadata: Metadados adicionais
            
        Returns:
            Dict com informações da memória criada
        """
        try:
            memory_id = str(uuid.uuid4())
            
            # Preparar metadados enriquecidos
            enriched_metadata = {
                "memory_id": memory_id,
                "type": memory_type,
                "agent_id": agent_id,
                "topics": topics or [],
                "created_timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # Dados para inserir na message_history
            memory_data = {
                "session_id": session_id,
                "user_id": user_id,
                "role": "system",  # Memórias enriquecidas são sempre system
                "content": memory_content,
                "metadata": enriched_metadata
            }
            
            result = self.supabase.table("message_history").insert(memory_data).execute()
            
            if result.data:
                created_memory = result.data[0]
                print(f"✅ Memória enriquecida criada: {memory_id}")
                
                return {
                    "memory_id": memory_id,
                    "id": created_memory["id"],
                    "content": memory_content,
                    "type": memory_type,
                    "topics": topics or [],
                    "metadata": enriched_metadata,
                    "status": "created",
                    "table": "message_history"
                }
            else:
                raise Exception("Falha ao inserir memória enriquecida")
                
        except Exception as e:
            print(f"❌ Erro ao criar memória enriquecida: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "table": "message_history"
            }
    
    def search_enriched_memories(self,
                                user_id: str,
                                query_topics: Optional[List[str]] = None,
                                memory_type: Optional[str] = None,
                                agent_id: Optional[str] = None,
                                limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca memórias enriquecidas na message_history
        
        Args:
            user_id: ID do usuário
            query_topics: Tópicos para filtrar
            memory_type: Tipo de memória para filtrar
            agent_id: ID do agente para filtrar
            limit: Limite de resultados
            
        Returns:
            Lista de memórias enriquecidas
        """
        try:
            query = self.supabase.table("message_history").select("*")
            query = query.eq("user_id", user_id)
            query = query.eq("role", "system")  # Apenas memórias enriquecidas
            
            # Filtrar por tipo se especificado
            if memory_type:
                query = query.contains("metadata", {"type": memory_type})
            
            # Filtrar por agent_id se especificado
            if agent_id:
                query = query.contains("metadata", {"agent_id": agent_id})
            
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            
            memories = []
            for row in result.data:
                metadata = row.get("metadata", {})
                
                # Filtrar por tópicos se especificado
                if query_topics:
                    row_topics = metadata.get("topics", [])
                    if not any(topic in row_topics for topic in query_topics):
                        continue
                
                memory_info = {
                    "memory_id": metadata.get("memory_id", f"mem-{row['id']}"),
                    "id": row["id"],
                    "content": row["content"],
                    "type": metadata.get("type", "unknown"),
                    "topics": metadata.get("topics", []),
                    "agent_id": metadata.get("agent_id"),
                    "metadata": metadata,
                    "created_at": row["created_at"]
                }
                memories.append(memory_info)
            
            print(f"✅ Encontradas {len(memories)} memórias enriquecidas")
            return memories
            
        except Exception as e:
            print(f"❌ Erro ao buscar memórias enriquecidas: {e}")
            return []
    
    # ==================== FUNÇÕES DE ENRIQUECIMENTO AUTOMÁTICO ====================
    
    def auto_enrich_conversation(self,
                                user_id: str,
                                session_id: str,
                                user_message: str,
                                agent_response: str) -> List[Dict[str, Any]]:
        """
        Enriquece automaticamente uma conversa criando uma síntese concisa da interação
        
        Cria um único registro objetivo que extrai:
        - O interesse principal do usuário
        - A informação central fornecida pelo agente
        
        Args:
            user_id: ID do usuário
            session_id: ID da sessão
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            
        Returns:
            Lista com a memória enriquecida criada
        """
        enriched_memories = []
        
        try:
            # Criar síntese concisa da interação
            synthesized_memory = self._synthesize_interaction(user_message, agent_response)
            
            if synthesized_memory:
                # Extrair tópicos da síntese para facilitar buscas futuras
                topics = self._extract_topics_from_synthesis(synthesized_memory)
                
                memory = self.create_enriched_memory(
                    user_id=user_id,
                    session_id=session_id,
                    agent_id="system",  # Memória enriquecida é sempre do sistema
                    memory_content=synthesized_memory,
                    memory_type="interaction_summary",
                    topics=topics,
                    metadata={"synthesis_version": "v1", "auto_generated": True}
                )
                if isinstance(memory, dict) and memory.get("status") == "created":
                    enriched_memories.append(memory)
                elif memory:  # Se não for dict mas existir, adiciona mesmo assim
                    enriched_memories.append(memory)
            
            print(f"✅ Criadas {len(enriched_memories)} memórias enriquecidas automaticamente")
            return enriched_memories
            
        except Exception as e:
            print(f"❌ Erro no enriquecimento automático: {e}")
            return enriched_memories
    
    def _extract_preferences(self, user_message: str, agent_response: str) -> List[Dict[str, Any]]:
        """Extrai preferências da conversa"""
        preferences = []
        
        # Detectar preferências de horário
        if any(word in user_message.lower() for word in ["horário", "funciona", "aberto", "fechado"]):
            preferences.append({
                "content": f"Usuário demonstrou interesse em horários de funcionamento",
                "topics": ["horario", "funcionamento"],
                "confidence": 0.8
            })
        
        # Detectar preferências de contato
        if any(word in user_message.lower() for word in ["whatsapp", "telefone", "contato", "ligar"]):
            preferences.append({
                "content": f"Usuário tem preferência por contato via WhatsApp/telefone",
                "topics": ["contato", "whatsapp", "telefone"],
                "confidence": 0.9
            })
        
        return preferences
    
    def _extract_facts(self, user_message: str, agent_response: str) -> List[Dict[str, Any]]:
        """Extrai fatos importantes da conversa"""
        facts = []
        
        # Extrair informações de produtos mencionados
        if any(word in user_message.lower() for word in ["produto", "comprar", "preço", "valor"]):
            facts.append({
                "content": f"Usuário demonstrou interesse em produtos/compras",
                "topics": ["produto", "compra", "interesse"],
                "confidence": 0.7
            })
        
        return facts
    
    def _create_conversation_summary(self, user_message: str, agent_response: str) -> Optional[Dict[str, Any]]:
        """Cria um resumo da conversa"""
        # Identificar tópicos principais
        topics = []
        
        if any(word in user_message.lower() for word in ["horário", "funciona"]):
            topics.append("horario")
        
        if any(word in user_message.lower() for word in ["contato", "telefone"]):
            topics.append("contato")
        
        if any(word in user_message.lower() for word in ["produto", "comprar"]):
            topics.append("produto")
        
        if topics:
            return {
                "content": f"Conversa abordou: {', '.join(topics)}",
                "topics": topics
            }
        
        return None
    
    def _extract_topics_from_synthesis(self, synthesis: str) -> List[str]:
        """
        Extrai tópicos relevantes da síntese para facilitar buscas futuras
        
        Args:
            synthesis: String com a síntese da interação
            
        Returns:
            Lista de tópicos identificados
        """
        topics = []
        synthesis_lower = synthesis.lower()
        
        # Mapear interesses para tópicos
        if "horários de funcionamento" in synthesis_lower:
            topics.extend(["horario", "funcionamento"])
        
        if "preços" in synthesis_lower or "valores" in synthesis_lower:
            topics.extend(["preco", "valor"])
        
        if "produtos" in synthesis_lower or "serviços" in synthesis_lower:
            topics.extend(["produto", "servico"])
        
        if "contato" in synthesis_lower:
            topics.extend(["contato", "comunicacao"])
        
        if "agendamento" in synthesis_lower:
            topics.extend(["agendamento", "consulta"])
        
        # Se não encontrou tópicos específicos, usar genérico
        if not topics:
            topics.append("geral")
        
        return list(set(topics))  # Remove duplicatas
    
    def _synthesize_interaction(self, user_message: str, agent_response: str) -> Optional[str]:
        """
        Sintetiza uma interação em um registro conciso seguindo o padrão:
        'Usuário demonstrou interesse em [assunto] e quis saber [detalhe]. 
         Informado pelo agente que [resumo da resposta principal].'
        
        Args:
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            
        Returns:
            String com a síntese da interação ou None se não relevante
        """
        user_msg_lower = user_message.lower()
        agent_resp_lower = agent_response.lower()
        
        # Detectar interesse principal do usuário
        interesse = None
        detalhe = None
        
        # Padrões de interesse em horários
        if any(word in user_msg_lower for word in ["horário", "funciona", "aberto", "fechado", "atende"]):
            interesse = "horários de funcionamento"
            detalhe = "quando funciona"
            
        # Padrões de interesse em preços/valores
        elif any(word in user_msg_lower for word in ["preço", "valor", "custa", "quanto"]):
            interesse = "preços"
            detalhe = "valores"
            
        # Padrões de interesse em produtos/serviços
        elif any(word in user_msg_lower for word in ["produto", "serviço", "tem", "oferece", "disponível"]):
            interesse = "produtos/serviços"
            detalhe = "disponibilidade"
            
        # Padrões de interesse em contato
        elif any(word in user_msg_lower for word in ["contato", "telefone", "whatsapp", "falar"]):
            interesse = "formas de contato"
            detalhe = "como entrar em contato"
            
        # Padrões de interesse em agendamento
        elif any(word in user_msg_lower for word in ["agendar", "marcar", "consulta", "horario"]):
            interesse = "agendamento"
            detalhe = "como agendar"
            
        # Se não detectou interesse específico, usar padrão genérico
        if not interesse:
            if len(user_message.strip()) > 10:  # Apenas para mensagens substantivas
                interesse = "informações"
                detalhe = "esclarecimentos"
            else:
                return None  # Mensagens muito curtas não são relevantes
        
        # Extrair informação principal da resposta do agente
        resposta_principal = self._extract_key_info_from_response(agent_response)
        
        if not resposta_principal:
            return None
        
        # Construir síntese seguindo o padrão especificado
        sintese = f"Usuário demonstrou interesse em {interesse} e quis saber {detalhe}. {resposta_principal}"
        
        return sintese
    
    def _extract_key_info_from_response(self, agent_response: str) -> Optional[str]:
        """
        Extrai a informação principal da resposta do agente
        
        Args:
            agent_response: Resposta do agente
            
        Returns:
            String com a informação principal ou None
        """
        response_lower = agent_response.lower()
        
        # Extrair horários de funcionamento
        if any(word in response_lower for word in ["funciona", "horário", "segunda", "sexta", "8h", "18h"]):
            if "segunda a sexta" in response_lower and "8h" in response_lower and "18h" in response_lower:
                return "Agente informou que funciona de segunda a sexta-feira, das 8h às 18h."
        
        # Extrair valores/preços
        import re
        price_pattern = r'(\d+(?:,\d+)?)\s*(?:reais?|r\$|mil)'
        prices = re.findall(price_pattern, response_lower)
        if prices:
            return f"Agente informou valores de {', '.join(prices)} reais."
        
        # Extrair informações de disponibilidade
        if any(word in response_lower for word in ["sim", "temos", "oferecemos", "disponível"]):
            return "Agente confirmou disponibilidade do serviço/produto."
        elif any(word in response_lower for word in ["não", "não temos", "indisponível"]):
            return "Agente informou que o serviço/produto não está disponível."
        
        # Extrair informações de contato
        if any(word in response_lower for word in ["whatsapp", "telefone", "contato"]):
            return "Agente forneceu informações de contato."
        
        # Extrair informações de agendamento
        if any(word in response_lower for word in ["agendar", "marcar", "consulta"]):
            return "Agente forneceu informações sobre agendamento."
        
        # Se a resposta for substantiva mas não se encaixa nos padrões, usar resumo genérico
        if len(agent_response.strip()) > 20:
            # Pegar as primeiras palavras significativas
            words = agent_response.split()[:15]
            summary = " ".join(words)
            if len(summary) > 100:
                summary = summary[:97] + "..."
            return f"Agente informou que {summary.lower()}"
        
        return None

# Instância global do serviço
dual_memory_service = DualMemoryOptimizedService()