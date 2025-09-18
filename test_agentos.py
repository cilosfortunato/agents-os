#!/usr/bin/env python3
"""
Script de Teste para AgentOS com Mem0 AI

Testa todas as funcionalidades:
- Agentes individuais
- Times colaborativos
- Memória persistente
- API endpoints
"""

import asyncio
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class TestadorAgentOS:
    def __init__(self, base_url: str = "http://localhost:7777"):
        self.base_url = base_url
        self.session = requests.Session()
        self.resultados = []
    
    def log_resultado(self, teste: str, sucesso: bool, detalhes: str = ""):
        """Registra resultado de um teste"""
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{status} - {teste}")
        if detalhes:
            print(f"   Detalhes: {detalhes}")
        
        self.resultados.append({
            "teste": teste,
            "sucesso": sucesso,
            "detalhes": detalhes
        })
    
    def testar_status_sistema(self):
        """Testa se o sistema está online"""
        try:
            response = self.session.get(f"{self.base_url}/v1/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_resultado(
                    "Status do Sistema", 
                    True, 
                    f"Agentes: {len(data.get('agentes_disponiveis', []))}, Times: {len(data.get('times_disponiveis', []))}"
                )
                return True
            else:
                self.log_resultado("Status do Sistema", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_resultado("Status do Sistema", False, str(e))
            return False
    
    def testar_agente_individual(self, agent_id: str, mensagem: str):
        """Testa um agente individual"""
        try:
            payload = {
                "mensagem": mensagem,
                "agent_id": agent_id,
                "user_id": "test-user-123",
                "session_id": "test-session-456",
                "message_id": "test-msg-789",
                "cliente_id": "test-cliente",
                "id_conta": "test-conta"
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                resposta = data.get('messages', [''])[0]
                self.log_resultado(
                    f"Agente {agent_id}",
                    True,
                    f"Resposta: {resposta[:100]}..."
                )
                return True
            else:
                self.log_resultado(
                    f"Agente {agent_id}",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_resultado(f"Agente {agent_id}", False, str(e))
            return False
    
    def testar_time(self, team_id: str, mensagem: str):
        """Testa um time de agentes"""
        try:
            payload = {
                "mensagem": mensagem,
                "agent_id": team_id,
                "user_id": "test-user-team",
                "session_id": "test-session-team",
                "message_id": "test-msg-team",
                "cliente_id": "test-cliente-team",
                "id_conta": "test-conta-team"
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/team-chat",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                resposta = data.get('messages', [''])[0]
                self.log_resultado(
                    f"Time {team_id}",
                    True,
                    f"Resposta: {resposta[:100]}..."
                )
                return True
            else:
                self.log_resultado(
                    f"Time {team_id}",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_resultado(f"Time {team_id}", False, str(e))
            return False
    
    def testar_memoria_persistente(self):
        """Testa a funcionalidade de memória"""
        user_id = "test-memoria-user"
        
        # Primeira interação
        payload1 = {
            "mensagem": "Meu nome é João e eu trabalho como desenvolvedor Python",
            "agent_id": "atendimento-cliente",
            "user_id": user_id,
            "session_id": "memoria-test-1"
        }
        
        try:
            response1 = self.session.post(
                f"{self.base_url}/v1/chat",
                json=payload1,
                timeout=30
            )
            
            if response1.status_code != 200:
                self.log_resultado("Memória - Primeira Interação", False, "Falha na primeira mensagem")
                return False
            
            # Segunda interação - testando se lembra
            payload2 = {
                "mensagem": "Qual é meu nome e profissão?",
                "agent_id": "atendimento-cliente",
                "user_id": user_id,
                "session_id": "memoria-test-2"
            }
            
            response2 = self.session.post(
                f"{self.base_url}/v1/chat",
                json=payload2,
                timeout=30
            )
            
            if response2.status_code == 200:
                data = response2.json()
                resposta = data.get('messages', [''])[0].lower()
                
                # Verifica se a resposta contém informações da memória
                lembra_nome = "joão" in resposta
                lembra_profissao = "desenvolvedor" in resposta or "python" in resposta
                
                if lembra_nome or lembra_profissao:
                    self.log_resultado(
                        "Memória Persistente",
                        True,
                        f"Lembrou informações: Nome={lembra_nome}, Profissão={lembra_profissao}"
                    )
                    return True
                else:
                    self.log_resultado(
                        "Memória Persistente",
                        False,
                        "Não conseguiu recuperar informações da memória"
                    )
                    return False
            else:
                self.log_resultado("Memória - Segunda Interação", False, "Falha na segunda mensagem")
                return False
                
        except Exception as e:
            self.log_resultado("Memória Persistente", False, str(e))
            return False
    
    def executar_todos_os_testes(self):
        """Executa todos os testes disponíveis"""
        print("🧪 Iniciando Testes do AgentOS com Mem0 AI")
        print("=" * 50)
        
        # Teste 1: Status do sistema
        if not self.testar_status_sistema():
            print("❌ Sistema não está respondendo. Verifique se está rodando.")
            return
        
        print("\n📋 Testando Agentes Individuais:")
        # Teste 2: Agentes individuais
        self.testar_agente_individual(
            "atendimento-cliente", 
            "Olá! Preciso de ajuda com meu pedido."
        )
        
        self.testar_agente_individual(
            "pesquisador", 
            "Pesquise informações sobre inteligência artificial em 2024."
        )
        
        self.testar_agente_individual(
            "suporte-tecnico", 
            "Meu computador está lento, o que posso fazer?"
        )
        
        print("\n👥 Testando Times de Agentes:")
        # Teste 3: Times
        self.testar_time(
            "time-atendimento", 
            "Preciso de suporte técnico para um problema complexo."
        )
        
        self.testar_time(
            "time-pesquisa", 
            "Faça uma análise sobre as tendências de IA em 2024."
        )
        
        print("\n🧠 Testando Memória Persistente:")
        # Teste 4: Memória
        self.testar_memoria_persistente()
        
        # Resumo dos resultados
        print("\n" + "=" * 50)
        print("📊 RESUMO DOS TESTES:")
        
        total_testes = len(self.resultados)
        testes_passaram = sum(1 for r in self.resultados if r['sucesso'])
        testes_falharam = total_testes - testes_passaram
        
        print(f"Total de testes: {total_testes}")
        print(f"✅ Passaram: {testes_passaram}")
        print(f"❌ Falharam: {testes_falharam}")
        print(f"📈 Taxa de sucesso: {(testes_passaram/total_testes)*100:.1f}%")
        
        if testes_falharam > 0:
            print("\n❌ Testes que falharam:")
            for resultado in self.resultados:
                if not resultado['sucesso']:
                    print(f"   - {resultado['teste']}: {resultado['detalhes']}")
        
        return testes_passaram == total_testes

def main():
    """Função principal"""
    print("🚀 Testador AgentOS com Mem0 AI")
    print("Certifique-se de que o sistema está rodando em http://localhost:7777")
    print("Para iniciar o sistema, execute: python agentos_main.py")
    print()
    
    input("Pressione Enter para continuar com os testes...")
    
    testador = TestadorAgentOS()
    sucesso_total = testador.executar_todos_os_testes()
    
    if sucesso_total:
        print("\n🎉 Todos os testes passaram! Sistema funcionando perfeitamente.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
    
    return sucesso_total

if __name__ == "__main__":
    main()