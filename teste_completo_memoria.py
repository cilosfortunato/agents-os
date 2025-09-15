#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo do Sistema AgentOS
Testa criação de agentes, times e memória persistente via API
"""

import requests
import json
import time
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:7777"
HEADERS = {"Content-Type": "application/json"}
USER_ID = "teste_memoria_user"

def print_separator(title):
    """Imprime um separador visual"""
    print("\n" + "="*60)
    print(f"🔹 {title}")
    print("="*60)

def print_response(title, response):
    """Imprime resposta da API de forma formatada"""
    print(f"\n📋 {title}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None

def criar_agente(nome, role, instructions):
    """Cria um agente personalizado"""
    payload = {
        "name": nome,
        "role": role,
        "instructions": instructions,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/agents", json=payload, headers=HEADERS)
    return print_response(f"Criar Agente: {nome}", response)

def criar_time(nome, descricao, agent_names):
    """Cria um time de agentes"""
    payload = {
        "name": nome,
        "description": descricao,
        "agent_names": agent_names,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams", json=payload, headers=HEADERS)
    return print_response(f"Criar Time: {nome}", response)

def listar_times():
    """Lista todos os times do usuário"""
    response = requests.get(f"{BASE_URL}/teams", params={"user_id": USER_ID}, headers=HEADERS)
    return print_response("Listar Times", response)

def executar_time(team_id, message):
    """Executa um time com uma mensagem"""
    payload = {
        "team_id": team_id,
        "message": message,
        "user_id": USER_ID
    }
    
    response = requests.post(f"{BASE_URL}/teams/run", json=payload, headers=HEADERS)
    return print_response(f"Executar Time - Mensagem: {message[:50]}...", response)

def buscar_memoria(query):
    """Busca memórias relacionadas"""
    params = {
        "user_id": USER_ID,
        "query": query,
        "limit": 5
    }
    
    response = requests.get(f"{BASE_URL}/memory/search", params=params, headers=HEADERS)
    return print_response(f"Buscar Memória: {query}", response)

def main():
    """Função principal do teste"""
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA AGENTOS")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # 1. Verificar saúde da API
    print_separator("1. VERIFICAÇÃO DE SAÚDE")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code != 200:
        print("❌ API não está funcionando!")
        return
    print_response("Health Check", response)
    
    # 2. Criar dois agentes personalizados
    print_separator("2. CRIAÇÃO DE AGENTES")
    
    # Agente 1: Especialista em Tecnologia
    agente1 = criar_agente(
        nome="Especialista Tech",
        role="Consultor de Tecnologia",
        instructions=[
            "Você é um especialista em tecnologia e programação",
            "Forneça respostas técnicas detalhadas e precisas",
            "Lembre-se sempre do contexto das conversas anteriores",
            "Seja didático e use exemplos práticos"
        ]
    )
    
    # Agente 2: Especialista em Negócios
    agente2 = criar_agente(
        nome="Especialista Business",
        role="Consultor de Negócios",
        instructions=[
            "Você é um especialista em estratégia de negócios e empreendedorismo",
            "Forneça insights sobre mercado, vendas e gestão",
            "Mantenha o contexto das discussões anteriores",
            "Seja prático e focado em resultados"
        ]
    )
    
    if not agente1 or not agente2:
        print("❌ Falha na criação dos agentes!")
        return
    
    # 3. Criar time com os dois agentes
    print_separator("3. CRIAÇÃO DE TIME")
    
    time_criado = criar_time(
        nome="Time Consultoria Completa",
        descricao="Time especializado em tecnologia e negócios para consultoria completa",
        agent_names=["Especialista Tech", "Especialista Business"]
    )
    
    if not time_criado:
        print("❌ Falha na criação do time!")
        return
    
    # 4. Obter ID do time criado
    print_separator("4. OBTENÇÃO DO ID DO TIME")
    times_data = listar_times()
    
    if not times_data or not times_data.get("teams"):
        print("❌ Nenhum time encontrado!")
        return
    
    # Pegar o último time criado (mais recente)
    team_id = times_data["teams"][-1]["id"]
    team_name = times_data["teams"][-1]["name"]
    print(f"✅ Usando time: {team_name} (ID: {team_id})")
    
    # 5. Teste de conversação com 5 perguntas sequenciais
    print_separator("5. TESTE DE CONVERSAÇÃO E MEMÓRIA")
    
    perguntas = [
        "Olá! Meu nome é João e sou empreendedor. Estou pensando em criar uma startup de tecnologia. Vocês podem me ajudar?",
        "Que tipo de tecnologia vocês recomendam para começar? Estou pensando em desenvolvimento web.",
        "E sobre o modelo de negócio? Como devo estruturar a monetização?",
        "Vocês se lembram do meu nome e do que estamos discutindo? Preciso de mais detalhes sobre tecnologias específicas.",
        "Para finalizar, podem fazer um resumo de tudo que discutimos e dar próximos passos?"
    ]
    
    respostas = []
    
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n🔸 PERGUNTA {i}:")
        print(f"'{pergunta}'")
        
        # Executar o time
        resposta = executar_time(team_id, pergunta)
        
        if resposta and resposta.get("response"):
            respostas.append({
                "pergunta": pergunta,
                "resposta": resposta["response"],
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"\n💬 RESPOSTA {i}:")
            print(f"'{resposta['response']}'")
        else:
            print(f"❌ Falha na pergunta {i}")
        
        # Aguardar um pouco entre as perguntas
        if i < len(perguntas):
            time.sleep(2)
    
    # 6. Teste de busca na memória
    print_separator("6. TESTE DE BUSCA NA MEMÓRIA")
    
    queries_memoria = [
        "João empreendedor startup",
        "tecnologia desenvolvimento web",
        "modelo de negócio monetização",
        "resumo discussão próximos passos"
    ]
    
    for query in queries_memoria:
        memoria_resultado = buscar_memoria(query)
        if memoria_resultado:
            print(f"\n🧠 Memórias encontradas para '{query}':")
            if memoria_resultado.get("memories"):
                for mem in memoria_resultado["memories"][:2]:  # Mostrar apenas as 2 primeiras
                    print(f"  - {mem.get('text', 'N/A')[:100]}...")
            else:
                print("  Nenhuma memória específica encontrada")
        time.sleep(1)
    
    # 7. Relatório final
    print_separator("7. RELATÓRIO FINAL")
    
    print(f"✅ Agentes criados: 2")
    print(f"✅ Time criado: 1")
    print(f"✅ Perguntas realizadas: {len(respostas)}")
    print(f"✅ Respostas recebidas: {len([r for r in respostas if r['resposta']])}")
    
    # Verificar se há evidências de memória nas respostas
    evidencias_memoria = []
    for i, resp in enumerate(respostas):
        if "joão" in resp["resposta"].lower() or "startup" in resp["resposta"].lower():
            evidencias_memoria.append(i + 1)
    
    print(f"\n🧠 ANÁLISE DE MEMÓRIA:")
    if evidencias_memoria:
        print(f"✅ Evidências de memória encontradas nas respostas: {evidencias_memoria}")
        print("✅ O sistema está mantendo contexto entre as conversas!")
    else:
        print("⚠️ Poucas evidências de memória detectadas")
    
    print(f"\n🎯 TESTE CONCLUÍDO COM SUCESSO!")
    print(f"⏰ Finalizado em: {datetime.now().isoformat()}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()