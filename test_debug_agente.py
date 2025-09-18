#!/usr/bin/env python3
"""
Teste de Debug para verificar o problema com agentes
"""

import requests
import json
import time

# Configurações da API
BASE_URL = "http://localhost:80"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
}

def fazer_requisicao(metodo, endpoint, dados=None):
    """Função auxiliar para fazer requisições HTTP"""
    url = f"{BASE_URL}{endpoint}"
    print(f"🌐 {metodo} {endpoint}")
    
    try:
        if metodo == "GET":
            response = requests.get(url, headers=HEADERS)
        elif metodo == "POST":
            response = requests.post(url, headers=HEADERS, json=dados)
        elif metodo == "PUT":
            response = requests.put(url, headers=HEADERS, json=dados)
        elif metodo == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ Resposta: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
            return resultado
        else:
            erro = response.json() if response.content else {"detail": "Sem conteúdo"}
            print(f"❌ Erro: {json.dumps(erro, ensure_ascii=False)}")
            return {"error": erro}
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return {"error": str(e)}

def main():
    print("🔍 TESTE DE DEBUG - VERIFICAÇÃO DE AGENTES")
    print("="*60)
    
    # 1. Listar agentes existentes
    print("\n1️⃣ Listando agentes existentes:")
    agentes_existentes = fazer_requisicao("GET", "/agents")
    
    # 2. Criar novo agente
    print("\n2️⃣ Criando novo agente:")
    dados_agente = {
        "name": "Agente Debug",
        "role": "assistente de teste",
        "instructions": ["Você é um assistente de teste"],
        "user_id": "debug_user"
    }
    
    resultado_criacao = fazer_requisicao("POST", "/agents", dados_agente)
    
    if "error" in resultado_criacao:
        print("❌ Falha na criação do agente")
        return
    
    agent_id = resultado_criacao.get("id")
    print(f"✅ Agente criado com ID: {agent_id}")
    
    # 3. Verificar se o agente aparece na lista imediatamente
    print("\n3️⃣ Verificando lista de agentes após criação:")
    agentes_apos_criacao = fazer_requisicao("GET", "/agents")
    
    # 4. Tentar buscar o agente específico
    print(f"\n4️⃣ Buscando agente específico {agent_id}:")
    agente_especifico = fazer_requisicao("GET", f"/agents/{agent_id}")
    
    # 5. Aguardar um pouco e tentar executar
    print("\n5️⃣ Aguardando 2 segundos...")
    time.sleep(2)
    
    print(f"\n6️⃣ Tentando executar agente {agent_id}:")
    dados_execucao = {
        "input": "Olá, você está funcionando?"
    }
    resultado_execucao = fazer_requisicao("POST", f"/agents/{agent_id}/run", dados_execucao)
    
    # 7. Verificar novamente a lista
    print("\n7️⃣ Verificando lista final de agentes:")
    agentes_finais = fazer_requisicao("GET", "/agents")

if __name__ == "__main__":
    main()