#!/usr/bin/env python3
"""
Teste completo da API - Gemini e OpenAI
Verifica providers, cria agentes e testa mensagens
"""
import requests
import json
import uuid
import time

BASE_URL = "http://localhost:8002"
HEADERS = {
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_response(label, response):
    print(f"\n--- {label} ---")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    except:
        print(f"Raw: {response.text[:500]}")
        return None

def test_health():
    print_section("1. TESTE DE SAÚDE")
    response = requests.get(f"{BASE_URL}/v1/health", headers=HEADERS, timeout=10)
    return print_response("Health Check", response)

def test_list_agents():
    print_section("2. LISTAR AGENTES EXISTENTES")
    response = requests.get(f"{BASE_URL}/v1/agents", headers=HEADERS, timeout=15)
    data = print_response("Lista de Agentes", response)
    
    agents = []
    if data and isinstance(data, dict):
        # Pode ser {"agents": [...]} ou {"custom_agents": [...], "default_agents": [...]}
        if "agents" in data:
            agents = data["agents"]
        else:
            agents = data.get("custom_agents", []) + data.get("default_agents", [])
    elif data and isinstance(data, list):
        agents = data
    
    print(f"\nTotal de agentes encontrados: {len(agents)}")
    return agents

def create_test_agents():
    print_section("3. CRIAR AGENTES DE TESTE")
    
    # Agente Gemini
    gemini_payload = {
        "name": "Teste Gemini",
        "role": "Assistente de teste com Gemini",
        "instructions": [
            "Você é um assistente de teste usando o modelo Gemini.",
            "Responda de forma clara e concisa.",
            "Identifique-se como 'Assistente Gemini' nas respostas."
        ],
        "model": "gemini-2.5-flash",
        "provider": "gemini"
    }
    
    # Agente OpenAI
    openai_payload = {
        "name": "Teste OpenAI",
        "role": "Assistente de teste com OpenAI",
        "instructions": [
            "Você é um assistente de teste usando o modelo OpenAI.",
            "Responda de forma clara e concisa.",
            "Identifique-se como 'Assistente OpenAI' nas respostas."
        ],
        "model": "gpt-4o-mini",
        "provider": "openai"
    }
    
    created_agents = []
    
    for name, payload in [("Gemini", gemini_payload), ("OpenAI", openai_payload)]:
        print(f"\n--- Criando agente {name} ---")
        response = requests.post(f"{BASE_URL}/v1/agents", headers=HEADERS, 
                               data=json.dumps(payload), timeout=25)
        data = print_response(f"Criar Agente {name}", response)
        
        if response.status_code in [200, 201] and data:
            agent_id = data.get("id")
            if agent_id:
                created_agents.append({
                    "id": agent_id,
                    "name": payload["name"],
                    "provider": payload["provider"],
                    "model": payload["model"]
                })
                print(f"✅ Agente {name} criado com ID: {agent_id}")
            else:
                print(f"❌ Falha ao obter ID do agente {name}")
        else:
            print(f"❌ Falha ao criar agente {name}")
    
    return created_agents

def test_message_to_agent(agent):
    print_section(f"4. TESTE DE MENSAGEM - {agent['name']} ({agent['provider']})")
    
    session_id = str(uuid.uuid4())
    message_payload = [
        {
            "mensagem": f"Olá! Você pode se apresentar e me dizer qual modelo está usando?",
            "agent_id": agent["id"],
            "debounce": 0,  # Sem debounce para teste imediato
            "session_id": session_id,
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "user_id": "teste_user@lid",
            "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
        }
    ]
    
    print(f"Enviando mensagem para agente {agent['name']}...")
    response = requests.post(f"{BASE_URL}/v1/messages", headers=HEADERS,
                           data=json.dumps(message_payload), timeout=30)
    
    data = print_response(f"Resposta do {agent['name']}", response)
    
    if data and "agent_usage" in data:
        usage = data["agent_usage"]
        print(f"\n🔍 AGENT_USAGE DETECTADO:")
        print(f"   Provider: {usage.get('provider', 'N/A')}")
        print(f"   Model: {usage.get('model', 'N/A')}")
        print(f"   Input Tokens: {usage.get('input_tokens', 'N/A')}")
        print(f"   Output Tokens: {usage.get('output_tokens', 'N/A')}")
        
        # Validar se os dados batem
        expected_provider = agent["provider"]
        expected_model = agent["model"]
        actual_provider = usage.get("provider")
        actual_model = usage.get("model")
        
        print(f"\n✅ Validação:")
        print(f"   Provider esperado: {expected_provider} | Recebido: {actual_provider} | {'✅' if expected_provider == actual_provider else '❌'}")
        print(f"   Model esperado: {expected_model} | Recebido: {actual_model} | {'✅' if expected_model == actual_model else '❌'}")
    else:
        print("❌ agent_usage não encontrado na resposta!")
    
    return data

def check_swagger():
    print_section("5. VERIFICAR SWAGGER/OPENAPI")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", headers=HEADERS, timeout=10)
        data = print_response("OpenAPI Schema", response)
        
        if data and "paths" in data:
            paths = data["paths"]
            print(f"\n📋 Endpoints disponíveis:")
            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                print(f"   {path} - {', '.join(methods).upper()}")
            
            # Verificar se /v1/messages está documentado
            if "/v1/messages" in paths:
                messages_endpoint = paths["/v1/messages"]
                if "post" in messages_endpoint:
                    post_info = messages_endpoint["post"]
                    print(f"\n🔍 Endpoint /v1/messages:")
                    print(f"   Summary: {post_info.get('summary', 'N/A')}")
                    print(f"   Tags: {post_info.get('tags', 'N/A')}")
                    
                    # Verificar se agent_usage está na resposta
                    if "responses" in post_info:
                        responses = post_info["responses"]
                        if "200" in responses:
                            success_response = responses["200"]
                            print(f"   Response 200: {success_response.get('description', 'N/A')}")
                            print("   ✅ Endpoint documentado no Swagger")
                        else:
                            print("   ❌ Response 200 não documentada")
                    else:
                        print("   ❌ Responses não documentadas")
                else:
                    print("   ❌ Método POST não documentado")
            else:
                print("   ❌ Endpoint /v1/messages não encontrado no Swagger")
        else:
            print("❌ Schema OpenAPI inválido")
            
    except Exception as e:
        print(f"❌ Erro ao verificar Swagger: {e}")

def main():
    print("🚀 INICIANDO TESTES COMPLETOS DA API")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # 1. Health check
        health = test_health()
        if not health:
            print("❌ API não está respondendo!")
            return
        
        # 2. Listar agentes existentes
        existing_agents = test_list_agents()
        
        # 3. Criar agentes de teste se necessário
        test_agents = []
        
        # Verificar se já temos agentes Gemini e OpenAI
        gemini_agent = None
        openai_agent = None
        
        for agent in existing_agents:
            if isinstance(agent, dict):
                provider = agent.get("provider", "").lower()
                if provider == "gemini" and not gemini_agent:
                    gemini_agent = agent
                elif provider == "openai" and not openai_agent:
                    openai_agent = agent
        
        # Criar agentes que faltam
        if not gemini_agent or not openai_agent:
            created = create_test_agents()
            for agent in created:
                if agent["provider"] == "gemini":
                    gemini_agent = agent
                elif agent["provider"] == "openai":
                    openai_agent = agent
        
        # 4. Testar mensagens
        if gemini_agent:
            test_message_to_agent(gemini_agent)
        else:
            print("❌ Nenhum agente Gemini disponível para teste")
            
        if openai_agent:
            test_message_to_agent(openai_agent)
        else:
            print("❌ Nenhum agente OpenAI disponível para teste")
        
        # 5. Verificar Swagger
        check_swagger()
        
        print_section("RESUMO DOS TESTES")
        print("✅ Testes concluídos!")
        print(f"   - Health check: {'✅' if health else '❌'}")
        print(f"   - Agente Gemini: {'✅' if gemini_agent else '❌'}")
        print(f"   - Agente OpenAI: {'✅' if openai_agent else '❌'}")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()