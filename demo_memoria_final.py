#!/usr/bin/env python3
"""
Demonstração Final Interativa do Sistema de Memória
Sistema completo de AgentOS com Knowledge (RAG) e Memória (Mem0)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time

class MemorySystemDemo:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
        }
        self.user_id = "demo_user_final"
        self.session_id = "demo_session_final"
        self.agent_id = "test_agent_123"
    
    def send_message(self, message: str) -> str:
        """Envia mensagem para o agente e retorna a resposta"""
        payload = {
            "mensagem": message,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "debounce": 0
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                return messages[0] if messages else "Sem resposta"
            else:
                return f"Erro HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"Erro: {e}"
    
    def print_conversation(self, user_message: str, agent_response: str):
        """Formata e exibe a conversa"""
        print(f"👤 Usuário: {user_message}")
        print(f"🤖 Agente: {agent_response}")
        print("-" * 80)
    
    def run_demo(self):
        """Executa a demonstração completa"""
        print("🧠 DEMONSTRAÇÃO FINAL: SISTEMA DE MEMÓRIA AGNOS")
        print("=" * 80)
        print("Este demo mostra um agente com memória persistente usando:")
        print("• 🧠 Memória Dupla (Supabase + Mem0)")
        print("• 🔍 Busca Inteligente com Extração de Palavras-chave")
        print("• 📚 Knowledge Base (RAG) com Pinecone")
        print("• 🤖 AgentOS nativo")
        print("=" * 80)
        
        # Sequência de demonstração
        demo_steps = [
            {
                "step": "1. Apresentação Inicial",
                "message": "Olá! Meu nome é Maria e eu trabalho como desenvolvedora de software.",
                "description": "Salvando informações pessoais na memória"
            },
            {
                "step": "2. Preferências",
                "message": "Eu adoro pizza de calabresa e programar em Python.",
                "description": "Adicionando preferências à memória"
            },
            {
                "step": "3. Teste de Memória - Nome",
                "message": "Você se lembra do meu nome?",
                "description": "Testando se o agente lembra informações pessoais"
            },
            {
                "step": "4. Teste de Memória - Profissão",
                "message": "Qual é a minha profissão?",
                "description": "Verificando memória sobre trabalho"
            },
            {
                "step": "5. Teste de Memória - Comida",
                "message": "O que eu gosto de comer?",
                "description": "Testando memória sobre preferências alimentares"
            },
            {
                "step": "6. Teste de Memória - Tecnologia",
                "message": "Qual linguagem de programação eu prefiro?",
                "description": "Verificando memória sobre preferências técnicas"
            },
            {
                "step": "7. Conversa Contextual",
                "message": "Você pode me recomendar um curso de Python para desenvolvedores?",
                "description": "Testando uso contextual da memória"
            },
            {
                "step": "8. Nova Informação",
                "message": "Ah, esqueci de mencionar que também gosto de pizza margherita!",
                "description": "Adicionando nova informação à memória existente"
            },
            {
                "step": "9. Verificação Final",
                "message": "Quais tipos de pizza eu gosto?",
                "description": "Testando se o agente lembra de ambas as preferências"
            }
        ]
        
        for i, step in enumerate(demo_steps, 1):
            print(f"\n🎯 {step['step']}")
            print(f"📝 {step['description']}")
            print("-" * 40)
            
            # Envia mensagem e recebe resposta
            response = self.send_message(step['message'])
            
            # Exibe a conversa
            self.print_conversation(step['message'], response)
            
            # Pausa para leitura
            time.sleep(1)
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("=" * 80)
        print("✅ FUNCIONALIDADES DEMONSTRADAS:")
        print("• Memória persistente entre conversas")
        print("• Busca inteligente por palavras-chave")
        print("• Contexto enriquecido com informações relevantes")
        print("• Integração nativa com AgentOS")
        print("• API robusta com FastAPI")
        print("=" * 80)

if __name__ == "__main__":
    demo = MemorySystemDemo()
    demo.run_demo()