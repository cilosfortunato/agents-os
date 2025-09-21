#!/usr/bin/env python3
"""
VERIFICAÇÃO FINAL COMPLETA DO SISTEMA AGNOS
===========================================

Este script realiza uma verificação completa de todos os componentes do sistema:
1. Configurações de ambiente
2. Conectividade com Supabase
3. Conectividade com PostgreSQL (memória)
4. Configuração de webhook
5. Teste de agente real
6. Verificação de persistência de memórias
7. Teste de webhook real
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class VerificacaoCompleta:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.agent_id = "da93fcc7-cf93-403e-aa99-9e295080d692"  # Agente real do Supabase
        self.user_id = "test_user_verificacao_final"
        self.session_id = f"session_{int(time.time())}"
        self.resultados = []
        
    def log(self, status, titulo, detalhes=""):
        """Log formatado dos resultados"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        emoji = "✅" if status == "SUCESSO" else "❌" if status == "ERRO" else "⚠️"
        print(f"[{timestamp}] {emoji} {titulo}")
        if detalhes:
            print(f"    {detalhes}")
        
        self.resultados.append({
            "timestamp": timestamp,
            "status": status,
            "titulo": titulo,
            "detalhes": detalhes
        })
        
    def verificar_variaveis_ambiente(self):
        """Verifica se todas as variáveis de ambiente necessárias estão configuradas"""
        print("\n" + "="*60)
        print("1. VERIFICANDO VARIÁVEIS DE AMBIENTE")
        print("="*60)
        
        variaveis_obrigatorias = [
            "OPENAI_API_KEY",
            "SUPABASE_URL", 
            "SUPABASE_ANON_KEY",
            "OUTBOUND_WEBHOOK_URL"
        ]
        
        variaveis_opcionais = [
            "SUPABASE_SERVICE_ROLE_KEY",
            "DATABASE_URL",
            "POSTGRES_HOST",
            "WEBHOOK_API_KEY",
            "PORT"
        ]
        
        for var in variaveis_obrigatorias:
            valor = os.getenv(var)
            if valor:
                self.log("SUCESSO", f"{var}: Configurada", f"Valor: {valor[:20]}...")
            else:
                self.log("ERRO", f"{var}: NÃO CONFIGURADA", "Esta variável é obrigatória")
                
        for var in variaveis_opcionais:
            valor = os.getenv(var)
            if valor:
                self.log("SUCESSO", f"{var}: Configurada", f"Valor: {valor[:20]}...")
            else:
                self.log("AVISO", f"{var}: Não configurada", "Esta variável é opcional")
    
    def verificar_api_rodando(self):
        """Verifica se a API está rodando"""
        print("\n" + "="*60)
        print("2. VERIFICANDO SE A API ESTÁ RODANDO")
        print("="*60)
        
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code == 200:
                self.log("SUCESSO", "API está rodando", f"Status: {response.status_code}")
                return True
            else:
                self.log("ERRO", "API retornou erro", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("ERRO", "API não está acessível", str(e))
            return False
    
    def verificar_agentes_carregados(self):
        """Verifica se os agentes foram carregados do Supabase"""
        print("\n" + "="*60)
        print("3. VERIFICANDO AGENTES CARREGADOS")
        print("="*60)
        
        try:
            response = requests.get(f"{self.api_base}/agents", timeout=10)
            if response.status_code == 200:
                agents = response.json()
                self.log("SUCESSO", f"Encontrados {len(agents)} agentes", f"Agentes: {[a.get('id', 'N/A') for a in agents]}")
                
                # Verificar se nosso agente específico está na lista
                agent_encontrado = any(a.get('id') == self.agent_id for a in agents)
                if agent_encontrado:
                    self.log("SUCESSO", "Agente específico encontrado", f"ID: {self.agent_id}")
                else:
                    self.log("AVISO", "Agente específico não encontrado", f"ID: {self.agent_id}")
                
                return True
            else:
                self.log("ERRO", "Erro ao buscar agentes", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("ERRO", "Erro na requisição de agentes", str(e))
            return False
    
    def testar_chat_agente(self):
        """Testa o chat com o agente real"""
        print("\n" + "="*60)
        print("4. TESTANDO CHAT COM AGENTE REAL")
        print("="*60)
        
        payload = {
            "mensagem": "Olá! Este é um teste de verificação final do sistema. Você pode me responder?",
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "message_id": f"msg_{int(time.time())}",
            "id_conta": "conta_teste_verificacao"
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/v1/messages",
                json=[payload],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                messages = result.get('messages', [])
                if messages:
                    self.log("SUCESSO", "Chat funcionando", f"Resposta: {messages[0][:100]}...")
                    return result
                else:
                    self.log("ERRO", "Chat sem resposta", "Nenhuma mensagem retornada")
                    return None
            else:
                self.log("ERRO", "Erro no chat", f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log("ERRO", "Erro na requisição de chat", str(e))
            return None
    
    def verificar_webhook_config(self):
        """Verifica a configuração do webhook"""
        print("\n" + "="*60)
        print("5. VERIFICANDO CONFIGURAÇÃO DO WEBHOOK")
        print("="*60)
        
        webhook_url = os.getenv("OUTBOUND_WEBHOOK_URL")
        webhook_api_key = os.getenv("WEBHOOK_API_KEY")
        
        if webhook_url:
            self.log("SUCESSO", "URL do webhook configurada", webhook_url)
            
            # Testar se o webhook está acessível
            try:
                response = requests.get(webhook_url, timeout=5)
                self.log("SUCESSO", "Webhook acessível", f"Status: {response.status_code}")
            except Exception as e:
                self.log("AVISO", "Webhook pode não estar acessível", str(e))
        else:
            self.log("ERRO", "URL do webhook não configurada", "OUTBOUND_WEBHOOK_URL não definida")
        
        if webhook_api_key:
            self.log("SUCESSO", "API Key do webhook configurada", f"Key: {webhook_api_key[:10]}...")
        else:
            self.log("AVISO", "API Key do webhook não configurada", "WEBHOOK_API_KEY não definida")
    
    def verificar_persistencia_supabase(self):
        """Verifica se as mensagens estão sendo salvas no Supabase"""
        print("\n" + "="*60)
        print("6. VERIFICANDO PERSISTÊNCIA NO SUPABASE")
        print("="*60)
        
        try:
            # Importar e testar o serviço Supabase
            from supabase_service import supabase_service
            
            # Tentar buscar mensagens da sessão atual
            messages = supabase_service.get_session_messages(self.session_id)
            
            if messages:
                self.log("SUCESSO", f"Encontradas {len(messages)} mensagens no Supabase", f"Session: {self.session_id}")
            else:
                self.log("AVISO", "Nenhuma mensagem encontrada no Supabase", "Pode ser normal se for primeira execução")
            
            # Testar salvamento de uma mensagem
            test_message = {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "agent_id": self.agent_id,
                "message": "Teste de persistência",
                "response": "Resposta de teste",
                "timestamp": datetime.now().isoformat()
            }
            
            saved = supabase_service.save_message(test_message)
            if saved:
                self.log("SUCESSO", "Teste de salvamento no Supabase", "Mensagem salva com sucesso")
            else:
                self.log("ERRO", "Falha no salvamento no Supabase", "Não foi possível salvar mensagem")
                
        except Exception as e:
            self.log("ERRO", "Erro ao verificar Supabase", str(e))
    
    def verificar_memoria_postgresql(self):
        """Verifica se a memória PostgreSQL está funcionando"""
        print("\n" + "="*60)
        print("7. VERIFICANDO MEMÓRIA POSTGRESQL")
        print("="*60)
        
        try:
            # Verificar se há configuração PostgreSQL
            database_url = os.getenv("DATABASE_URL")
            postgres_host = os.getenv("POSTGRES_HOST")
            
            if database_url or postgres_host:
                self.log("SUCESSO", "Configuração PostgreSQL encontrada", database_url or postgres_host)
                
                # Tentar importar e testar o sistema de memória
                try:
                    from postgres_memory_system import PostgreSQLMemorySystem
                    memory_system = PostgreSQLMemorySystem()
                    
                    # Testar salvamento de memória
                    test_memory = {
                        "user_id": self.user_id,
                        "session_id": self.session_id,
                        "content": "Teste de memória PostgreSQL",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    saved = memory_system.save_memory(test_memory)
                    if saved:
                        self.log("SUCESSO", "Sistema de memória PostgreSQL funcionando", "Memória salva com sucesso")
                    else:
                        self.log("ERRO", "Falha no sistema de memória PostgreSQL", "Não foi possível salvar memória")
                        
                except Exception as e:
                    self.log("ERRO", "Erro no sistema de memória PostgreSQL", str(e))
            else:
                self.log("AVISO", "PostgreSQL não configurado", "DATABASE_URL e POSTGRES_HOST não definidos")
                
        except Exception as e:
            self.log("ERRO", "Erro ao verificar PostgreSQL", str(e))
    
    def verificar_mem0(self):
        """Verifica se o Mem0 está configurado e funcionando"""
        print("\n" + "="*60)
        print("8. VERIFICANDO MEM0")
        print("="*60)
        
        try:
            mem0_api_key = os.getenv("MEM0_API_KEY")
            
            if mem0_api_key:
                self.log("SUCESSO", "API Key Mem0 configurada", f"Key: {mem0_api_key[:10]}...")
                
                # Tentar importar e testar Mem0
                try:
                    from mem0 import MemoryClient
                    client = MemoryClient()
                    
                    # Testar busca de memórias
                    memories = client.search(query="teste", user_id=self.user_id, limit=1)
                    self.log("SUCESSO", "Mem0 funcionando", f"Encontradas {len(memories)} memórias")
                    
                except Exception as e:
                    self.log("ERRO", "Erro ao testar Mem0", str(e))
            else:
                self.log("AVISO", "Mem0 não configurado", "MEM0_API_KEY não definida")
                
        except Exception as e:
            self.log("ERRO", "Erro ao verificar Mem0", str(e))
    
    def gerar_relatorio_final(self):
        """Gera um relatório final da verificação"""
        print("\n" + "="*60)
        print("RELATÓRIO FINAL DA VERIFICAÇÃO")
        print("="*60)
        
        sucessos = len([r for r in self.resultados if r["status"] == "SUCESSO"])
        erros = len([r for r in self.resultados if r["status"] == "ERRO"])
        avisos = len([r for r in self.resultados if r["status"] == "AVISO"])
        
        print(f"\n📊 RESUMO:")
        print(f"   ✅ Sucessos: {sucessos}")
        print(f"   ❌ Erros: {erros}")
        print(f"   ⚠️  Avisos: {avisos}")
        print(f"   📝 Total de verificações: {len(self.resultados)}")
        
        if erros == 0:
            print(f"\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
        elif erros <= 2:
            print(f"\n⚠️  SISTEMA FUNCIONANDO COM PEQUENOS PROBLEMAS")
        else:
            print(f"\n❌ SISTEMA COM PROBLEMAS CRÍTICOS")
        
        # Salvar relatório em arquivo
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "resumo": {
                "sucessos": sucessos,
                "erros": erros,
                "avisos": avisos,
                "total": len(self.resultados)
            },
            "detalhes": self.resultados
        }
        
        with open("relatorio_verificacao_final.json", "w", encoding="utf-8") as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: relatorio_verificacao_final.json")
    
    def executar_verificacao_completa(self):
        """Executa todas as verificações"""
        print("🚀 INICIANDO VERIFICAÇÃO FINAL COMPLETA DO SISTEMA AGNOS")
        print("=" * 80)
        
        # Executar todas as verificações
        self.verificar_variaveis_ambiente()
        
        if self.verificar_api_rodando():
            self.verificar_agentes_carregados()
            self.testar_chat_agente()
        
        self.verificar_webhook_config()
        self.verificar_persistencia_supabase()
        self.verificar_memoria_postgresql()
        self.verificar_mem0()
        
        # Gerar relatório final
        self.gerar_relatorio_final()

if __name__ == "__main__":
    verificacao = VerificacaoCompleta()
    verificacao.executar_verificacao_completa()