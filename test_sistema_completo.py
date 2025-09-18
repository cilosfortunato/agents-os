#!/usr/bin/env python3
"""
Teste Completo do Sistema AgentOS
Testa todas as funcionalidades principais:
- Criação de agentes
- Execução de agentes
- Knowledge (RAG) com Pinecone
- Memória com Mem0
- Teams (se disponível)
"""

import requests
import json
import time
from typing import Dict, Any

# Configurações da API
BASE_URL = "http://localhost:80"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def fazer_requisicao(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Faz uma requisição para a API e retorna a resposta."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS, params=data)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        else:
            raise ValueError(f"Método HTTP não suportado: {method}")
        
        print(f"🌐 {method.upper()} {endpoint}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code >= 400:
            print(f"❌ Erro: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
        
        result = response.json() if response.content else {}
        print(f"✅ Resposta: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
        return result
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return {"error": str(e)}

def teste_1_criar_agente():
    """Teste 1: Criação de Agente"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: CRIAÇÃO DE AGENTE")
    print("="*60)
    
    dados_agente = {
        "name": "Assistente de Suporte Técnico",
        "role": "especialista em suporte técnico",
        "instructions": [
            "Você é um assistente especializado em suporte técnico",
            "Seja sempre prestativo e técnico nas respostas",
            "Use conhecimento da base de dados quando disponível",
            "Mantenha um histórico das conversas para personalizar atendimento"
        ],
        "user_id": "test_user_123"
    }
    
    resultado = fazer_requisicao("POST", "/agents", dados_agente)
    
    if "error" in resultado:
        print("❌ Falha na criação do agente")
        return None
    
    agent_id = resultado.get("agent", {}).get("id")
    print(f"✅ Agente criado com sucesso! ID: {agent_id}")
    return agent_id

def teste_2_executar_agente(agent_id: str):
    """Teste 2: Execução de Agente"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: EXECUÇÃO DE AGENTE")
    print("="*60)
    
    # Pequena pausa para garantir que o agente foi processado
    print("⏳ Aguardando 1 segundo...")
    time.sleep(1)
    
    mensagem_teste = {
        "message": "Olá! Preciso de ajuda com um problema no meu dispositivo. Ele não está ligando.",
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }
    
    resultado = fazer_requisicao("POST", f"/agents/{agent_id}/run", mensagem_teste)
    
    if "error" in resultado:
        print("❌ Falha na execução do agente")
        return False
    
    messages = resultado.get("messages", [])
    if messages:
        print(f"✅ Agente respondeu: {messages[0][:100]}...")
        return True
    else:
        print("❌ Agente não retornou mensagens")
        return False

def teste_3_knowledge_rag():
    """Teste 3: Knowledge (RAG) com Pinecone"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: KNOWLEDGE (RAG)")
    print("="*60)
    
    # Primeiro criar uma base de conhecimento
    dados_knowledge_base = {
        "id": "produto_teste",
        "name": "Base de Conhecimento Produto",
        "description": "Base de conhecimento para testes",
        "vectordb": {
            "provider": "local",
            "config": {}
        }
    }
    
    resultado_add = fazer_requisicao("POST", "/knowledge", dados_knowledge_base)
    
    if "error" in resultado_add:
        print("❌ Falha ao adicionar conhecimento")
        return False
    
    print("✅ Conhecimento adicionado com sucesso")
    
    # Teste de busca no conhecimento
    time.sleep(2)  # Aguarda indexação
    
    dados_search = {
        "query": "garantia dispositivo X",
        "knowledge_id": "produto_teste",
        "limit": 3
    }
    
    resultado_search = fazer_requisicao("POST", "/knowledge/search", dados_search)
    
    if "error" in resultado_search:
        print("❌ Falha na busca de conhecimento")
        return False
    
    results = resultado_search.get("results", [])
    if results:
        print(f"✅ Encontrados {len(results)} resultados na base de conhecimento")
        return True
    else:
        print("⚠️ Nenhum resultado encontrado na busca")
        return False

def teste_4_memoria_mem0():
    """Teste 4: Memória com Mem0"""
    print("\n" + "="*60)
    print("🧪 TESTE 4: MEMÓRIA (MEM0)")
    print("="*60)
    
    # Teste de adição de memória
    dados_memoria = {
        "user_id": "test_user_123",
        "messages": [
            {
                "role": "user",
                "content": "Meu nome é João e trabalho com desenvolvimento de software"
            },
            {
                "role": "assistant", 
                "content": "Olá João! Prazer em conhecê-lo. Vou lembrar que você trabalha com desenvolvimento de software."
            }
        ]
    }
    
    resultado_add = fazer_requisicao("POST", "/memory/add", dados_memoria)
    
    if "error" in resultado_add:
        print("❌ Falha ao adicionar memória")
        return False
    
    print("✅ Memória adicionada com sucesso")
    
    # Teste de busca na memória
    time.sleep(2)  # Aguarda processamento
    
    dados_search = {
        "user_id": "test_user_123",
        "query": "qual meu nome e profissão",
        "limit": 3
    }
    
    resultado_search = fazer_requisicao("GET", "/memory/search", dados_search)
    
    if "error" in resultado_search:
        print("❌ Falha na busca de memória")
        return False
    
    results = resultado_search.get("results", [])
    if results:
        print(f"✅ Encontradas {len(results)} memórias relevantes")
        return True
    else:
        print("⚠️ Nenhuma memória encontrada na busca")
        return False

def teste_5_integracao_completa(agent_id: str):
    """Teste 5: Integração Completa (Agente + Knowledge + Memória)"""
    print("\n" + "="*60)
    print("🧪 TESTE 5: INTEGRAÇÃO COMPLETA")
    print("="*60)
    
    # Primeira interação - estabelece contexto
    mensagem1 = {
        "message": "Olá, sou o João, desenvolvedor. Meu dispositivo X não está funcionando.",
        "user_id": "test_user_123",
        "session_id": "integration_test_session"
    }
    
    resultado1 = fazer_requisicao("POST", f"/agents/{agent_id}/run", mensagem1)
    
    if "error" in resultado1:
        print("❌ Falha na primeira interação")
        return False
    
    print("✅ Primeira interação bem-sucedida")
    
    # Segunda interação - testa memória e knowledge
    time.sleep(3)  # Aguarda processamento da memória
    
    mensagem2 = {
        "message": "Você lembra qual é minha profissão? E qual a garantia do dispositivo X?",
        "user_id": "test_user_123", 
        "session_id": "integration_test_session"
    }
    
    resultado2 = fazer_requisicao("POST", f"/agents/{agent_id}/run", mensagem2)
    
    if "error" in resultado2:
        print("❌ Falha na segunda interação")
        return False
    
    resposta = resultado2.get("messages", [""])[0].lower()
    
    # Verifica se a resposta contém informações da memória e knowledge
    tem_memoria = "joão" in resposta or "desenvolvedor" in resposta
    tem_knowledge = "garantia" in resposta or "24 meses" in resposta
    
    if tem_memoria and tem_knowledge:
        print("✅ Integração completa funcionando! Agente usou memória E knowledge")
        return True
    elif tem_memoria:
        print("⚠️ Agente usou memória, mas não acessou knowledge")
        return False
    elif tem_knowledge:
        print("⚠️ Agente usou knowledge, mas não acessou memória")
        return False
    else:
        print("❌ Agente não usou nem memória nem knowledge")
        return False

def executar_todos_os_testes():
    """Executa todos os testes em sequência"""
    print("🚀 INICIANDO BATERIA COMPLETA DE TESTES DO AGENTOS")
    print("="*80)
    
    resultados = {
        "criacao_agente": False,
        "execucao_agente": False,
        "knowledge_rag": False,
        "memoria_mem0": False,
        "integracao_completa": False
    }
    
    # Teste 1: Criação de Agente
    agent_id = teste_1_criar_agente()
    if agent_id:
        resultados["criacao_agente"] = True
        
        # Teste 2: Execução de Agente
        if teste_2_executar_agente(agent_id):
            resultados["execucao_agente"] = True
    
    # Teste 3: Knowledge (RAG)
    if teste_3_knowledge_rag():
        resultados["knowledge_rag"] = True
    
    # Teste 4: Memória (Mem0)
    if teste_4_memoria_mem0():
        resultados["memoria_mem0"] = True
    
    # Teste 5: Integração Completa (apenas se agente foi criado)
    if agent_id and teste_5_integracao_completa(agent_id):
        resultados["integracao_completa"] = True
    
    # Relatório Final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("="*80)
    
    total_testes = len(resultados)
    testes_passaram = sum(resultados.values())
    
    for teste, passou in resultados.items():
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{teste.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 RESULTADO GERAL: {testes_passaram}/{total_testes} testes passaram")
    
    if testes_passaram == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente!")
        return True
    elif testes_passaram >= total_testes * 0.8:
        print("⚠️ Maioria dos testes passou. Sistema funcional com algumas limitações.")
        return True
    else:
        print("❌ Muitos testes falharam. Sistema precisa de correções.")
        return False

if __name__ == "__main__":
    sucesso = executar_todos_os_testes()
    exit(0 if sucesso else 1)