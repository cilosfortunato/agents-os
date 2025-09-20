"""
Serviço de Memória Dupla - Combina memória interna (Supabase) e externa (Mem0)
"""
from typing import List, Dict, Any, Optional
from supabase_service import supabase_service
from memory import memory_manager
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class DualMemoryService:
    """
    Gerenciador de memória dupla que combina:
    - Memória Interna: Histórico de mensagens no Supabase (persistente, estruturado)
    - Memória Externa: Contexto enriquecido no Mem0 (semântico, inteligente)
    """
    
    def __init__(self):
        self.supabase = supabase_service
        self.mem0 = memory_manager
        
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
    
    def get_session_context(self, session_id: str, limit: int = 10) -> str:
        """
        Recupera contexto da sessão atual (últimas mensagens)
        
        Args:
            session_id: ID da sessão
            limit: Número de mensagens a recuperar
        
        Returns:
            String formatada com o contexto da sessão
        """
        try:
            messages = self.supabase.get_session_messages(session_id, limit)
            
            if not messages:
                return "Nova sessão - sem histórico anterior."
            
            context_parts = []
            for msg in messages:
                context_parts.append(f"Usuário: {msg['user_message']}")
                context_parts.append(f"Assistente: {msg['agent_response']}")
                context_parts.append("---")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logging.error(f"Erro ao recuperar contexto da sessão: {e}")
            return "Erro ao acessar histórico da sessão."
    
    def search_user_history(self, user_id: str, query: str, limit: int = 5) -> str:
        """
        Busca no histórico do usuário por termo específico
        
        Args:
            user_id: ID do usuário
            query: Termo de busca
            limit: Número máximo de resultados
        
        Returns:
            String formatada com resultados da busca
        """
        try:
            messages = self.supabase.search_messages(user_id, query, limit)
            
            if not messages:
                return f"Nenhuma mensagem anterior encontrada sobre '{query}'."
            
            context_parts = [f"Conversas anteriores sobre '{query}':"]
            for msg in messages:
                context_parts.append(f"• {msg['user_message']} → {msg['agent_response']}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logging.error(f"Erro ao buscar histórico do usuário: {e}")
            return "Erro ao buscar no histórico."
    
    # ==================== MEMÓRIA EXTERNA (MEM0) ====================
    
    def save_to_external_memory(self, user_id: str, user_message: str, 
                              agent_response: str, agent_name: str = "Assistant") -> bool:
        """
        Salva conversa na memória externa (Mem0) para contexto enriquecido
        
        Args:
            user_id: ID do usuário
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            agent_name: Nome do agente
        
        Returns:
            True se salvo com sucesso
        """
        try:
            return self.mem0.save_conversation(
                user_id=user_id,
                user_message=user_message,
                assistant_response=agent_response,
                agent_name=agent_name
            )
        except Exception as e:
            logging.error(f"Erro ao salvar na memória externa: {e}")
            return False
    
    def get_enriched_context(self, user_id: str, query: str, limit: int = 3) -> str:
        """
        Recupera contexto enriquecido da memória externa (Mem0)
        
        Args:
            user_id: ID do usuário
            query: Mensagem atual para busca semântica
            limit: Número de memórias a recuperar
        
        Returns:
            String formatada com contexto enriquecido
        """
        try:
            memories = self.mem0.search_memories(user_id, query, limit)
            
            if not memories:
                return "Nenhum contexto enriquecido disponível."
            
            formatted_context = self.mem0.format_memories_for_context(memories)
            return f"Contexto relevante das conversas anteriores:\n{formatted_context}"
            
        except Exception as e:
            logging.error(f"Erro ao recuperar contexto enriquecido: {e}")
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
        
        # Salva na memória externa (Mem0)
        try:
            external_success = self.save_to_external_memory(
                user_id, user_message, agent_response, agent_name
            )
            results["external_memory"] = external_success
        except Exception as e:
            logging.error(f"Falha na memória externa: {e}")
        
        return results
    
    def get_complete_context(self, user_id: str, session_id: str, 
                           query: str, session_limit: int = 5, 
                           memory_limit: int = 3) -> Dict[str, str]:
        """
        Recupera contexto completo de ambas as memórias com paralelização
        """
        t0 = time.perf_counter()
        search_terms = self._extract_search_terms(query)

        results: Dict[str, str] = {
            "session_context": "",
            "enriched_context": "",
            "search_context": ""
        }

        def _get_session():
            return self.get_session_context(session_id, session_limit)

        def _get_enriched():
            return self.get_enriched_context(user_id, query, memory_limit)

        def _get_search():
            return self._search_with_multiple_terms(user_id, search_terms, 5)

        with ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {
                executor.submit(_get_session): "session_context",
                executor.submit(_get_enriched): "enriched_context",
                executor.submit(_get_search): "search_context",
            }
            for fut in as_completed(future_map):
                key = future_map[fut]
                try:
                    results[key] = fut.result()
                except Exception as e:
                    logging.warning(f"Falha ao obter {key}: {e}")
                    results[key] = ""
        t1 = time.perf_counter()
        try:
            logging.info(
                f"[METRICS] get_complete_context | total: {(t1 - t0)*1000:.1f}ms"
            )
        except Exception:
            pass
        return results

    def _search_with_multiple_terms(self, user_id: str, search_terms: List[str], limit: int = 5) -> str:
        """
        Busca usando múltiplos termos com tentativa de query única (OR) e fallback
        """
        if not search_terms:
            return "Nenhum termo de busca fornecido."

        # Tenta uma única chamada com termos combinados, se o serviço suportar
        try:
            query_str = " | ".join(search_terms)  # usado como sugestão de OR/FTS no service
            messages = self.supabase.search_messages(user_id, query_str, limit)
            if messages:
                # Ordena por data (mais recente primeiro) e limita
                messages.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                messages = messages[:limit]
                context_parts = [f"Conversas anteriores relevantes (termos: {', '.join(search_terms)}):"]
                for msg in messages:
                    context_parts.append(f"• {msg['user_message']} → {msg['agent_response']}")
                return "\n".join(context_parts)
        except Exception as e:
            logging.warning(f"Falha na busca OR única, aplicando fallback: {e}")

        # Fallback: N chamadas sequenciais, evitando duplicatas
        all_results = []
        seen = set()
        for term in search_terms:
            try:
                msgs = self.supabase.search_messages(user_id, term, limit)
            except Exception as e:
                logging.warning(f"Erro ao buscar por '{term}': {e}")
                continue
            for msg in msgs or []:
                key = (msg.get('id'), msg.get('created_at'))
                if key not in seen:
                    seen.add(key)
                    all_results.append(msg)

        if not all_results:
            return f"Nenhuma mensagem anterior encontrada para os termos: {', '.join(search_terms)}"

        all_results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        limited_results = all_results[:limit]
        context_parts = [f"Conversas anteriores relevantes (termos: {', '.join(search_terms)}):"]
        for msg in limited_results:
            context_parts.append(f"• {msg['user_message']} → {msg['agent_response']}")
        return "\n".join(context_parts)
    
    def get_memory_context(self, user_id: str, query: str = "", limit: int = 5) -> str:
        """
        Método principal para recuperar contexto de memória
        Combina histórico recente do usuário e busca semântica
        
        Args:
            user_id: ID do usuário
            query: Consulta para busca semântica (opcional)
            limit: Número máximo de resultados
        
        Returns:
            String formatada com contexto de memória
        """
        try:
            # Busca mensagens recentes do usuário
            recent_messages = self.supabase.get_user_messages(user_id, limit)
            
            context_parts = []
            
            if recent_messages:
                context_parts.append("📝 Contexto de conversas anteriores:")
                for msg in recent_messages:
                    context_parts.append(f"• Usuário: {msg['user_message']}")
                    context_parts.append(f"• Assistente: {msg['agent_response']}")
                    context_parts.append("---")
            
            # Se há uma query específica, tenta busca semântica no Mem0
            if query and self.mem0:
                try:
                    enriched_context = self.get_enriched_context(user_id, query, 3)
                    if enriched_context and "Nenhuma memória" not in enriched_context:
                        context_parts.append("\n🧠 Memórias relevantes:")
                        context_parts.append(enriched_context)
                except Exception as e:
                    logging.warning(f"Falha na busca semântica: {e}")
            
            return "\n".join(context_parts) if context_parts else "Nenhum contexto anterior encontrado."
            
        except Exception as e:
             logging.error(f"Erro ao recuperar contexto de memória: {e}")
             return "Erro ao acessar memória."
    
    def search_memory(self, user_id: str, query: str, limit: int = 3) -> List[Dict]:
        """
        Busca memórias específicas do usuário
        Compatível com o endpoint da API
        
        Args:
            user_id: ID do usuário
            query: Consulta de busca
            limit: Número máximo de resultados
        
        Returns:
            Lista de memórias encontradas
        """
        try:
            memories = []
            
            # Busca no Supabase (memória interna)
            supabase_messages = self.supabase.search_messages(user_id, query, limit)
            for msg in supabase_messages:
                memories.append({
                    "source": "supabase",
                    "content": f"Usuário: {msg['user_message']} | Assistente: {msg['agent_response']}",
                    "timestamp": msg.get('created_at', ''),
                    "metadata": {"session_id": msg.get('session_id', '')}
                })
            
            # Busca no Mem0 (memória externa) se disponível
            if self.mem0:
                try:
                    # Usa o MemoryManager para buscar memórias no Mem0
                    mem0_results = self.mem0.search_memories(user_id=user_id, query=query, limit=limit)
                    for result in mem0_results:
                        memories.append({
                            "source": "mem0",
                            "content": result.get('text', result.get('memory', '')),
                            "timestamp": result.get('created_at', ''),
                            "metadata": result.get('metadata', {})
                        })
                except Exception as e:
                    logging.warning(f"Erro na busca Mem0: {e}")
            
            return memories[:limit]  # Limita o total de resultados
            
        except Exception as e:
            logging.error(f"Erro na busca de memória: {e}")
            return []
    
    def add_memory(self, user_id: str, content: str, metadata: Dict = None) -> bool:
        """
        Adiciona uma nova memória
        Compatível com o endpoint da API
        
        Args:
            user_id: ID do usuário
            content: Conteúdo da memória
            metadata: Metadados adicionais
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            success_mem0 = False
            success_internal = False

            # Adiciona no Mem0 (memória externa)
            if self.mem0:
                try:
                    messages = [
                        {"role": "user", "content": content},
                        {"role": "assistant", "content": f"Memória registrada: {content}"}
                    ]
                    success_mem0 = self.mem0.add_memory(user_id=user_id, messages=messages, metadata=metadata or {})
                except Exception as e:
                    logging.warning(f"Erro ao adicionar memória no Mem0: {e}")

            # Também registra na memória interna (Supabase) para garantir busca por texto
            try:
                session_id = (metadata or {}).get("session_id") if metadata else None
                if not session_id:
                    session_id = f"mem_{user_id}_{int(time.time())}"
                agent_id = (metadata or {}).get("agent_id", "memory_service")
                saved = self.save_message_to_internal_memory(
                    user_id=user_id,
                    session_id=session_id,
                    agent_id=agent_id,
                    user_message=content,
                    agent_response="Memória registrada"
                )
                success_internal = bool(saved)
            except Exception as e:
                logging.warning(f"Erro ao adicionar memória interna: {e}")

            return bool(success_mem0 or success_internal)
        except Exception as e:
            logging.error(f"Erro ao adicionar memória: {e}")
            return False

    def _extract_search_terms(self, query: str) -> List[str]:
        """
        Extrai termos de busca relevantes da query
        """
        import re
        
        # Remove pontuação e converte para minúsculas
        clean_query = re.sub(r'[^\w\s]', ' ', query.lower())
        
        # Divide em palavras e remove palavras muito curtas
        words = [word.strip() for word in clean_query.split() if len(word.strip()) > 2]
        
        # Remove palavras comuns (stop words básicas em português)
        stop_words = {
            'que', 'para', 'com', 'uma', 'por', 'como', 'mais', 'mas', 'foi', 'dos', 
            'tem', 'seu', 'sua', 'são', 'ele', 'ela', 'isso', 'este', 'esta', 'esse',
            'essa', 'aquele', 'aquela', 'quando', 'onde', 'porque', 'qual', 'quais'
        }
        
        terms = [word for word in words if word not in stop_words]
        
        # Retorna no máximo 5 termos mais relevantes
        return terms[:5] if terms else [query.lower()]

# Instância global do serviço de memória dupla
dual_memory_service = DualMemoryService()