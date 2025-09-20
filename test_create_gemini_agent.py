#!/usr/bin/env python3
"""
Script para testar a criação de um novo agente Gemini 2.5 Flash via API
"""
import requests
import json
import uuid
from datetime import datetime

# Configurações da API
API_BASE_URL = "http://localhost:80"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

def test_create_gemini_agent():
    """Testa a criação de um novo agente Gemini via API"""
    
    print("🚀 Testando criação de agente Gemini 2.5 Flash via API...")
    print("=" * 60)
    
    # Dados do novo agente
    agent_data = {
        "name": f"Agente Gemini Test {datetime.now().strftime('%H:%M:%S')}",
        "role": "Assistente de Testes",
        "instructions": [
            "Você é um assistente especializado em testes de API.",
            "Responda de forma clara e objetiva.",
            "Sempre mencione que você está usando o modelo Gemini 2.5 Flash."
        ],
        "model": "gemini-2.5-flash",
        "provider": "gemini",
        "account_id": str(uuid.uuid4())
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        # Fazer requisição para criar o agente
        print(f"📤 Enviando requisição POST para {API_BASE_URL}/v1/agents")
        print(f"📋 Dados do agente:")
        print(json.dumps(agent_data, indent=2, ensure_ascii=False))
        print()
        
        response = requests.post(
            f"{API_BASE_URL}/v1/agents",
            json=agent_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            agent_response = response.json()
            print("✅ Agente criado com sucesso!")
            print(f"📋 Resposta da API:")
            print(json.dumps(agent_response, indent=2, ensure_ascii=False))
            
            # Extrair o ID do agente criado
            agent_id = agent_response.get("id")
            if agent_id:
                print(f"\n🆔 ID do agente criado: {agent_id}")
                return agent_id
            else:
                print("❌ Erro: ID do agente não encontrado na resposta")
                return None
                
        else:
            print(f"❌ Erro ao criar agente: {response.status_code}")
            print(f"📋 Resposta de erro:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def verify_agent_in_database(agent_id: str):
    """Verifica se o agente foi salvo corretamente no banco"""
    
    print(f"\n🔍 Verificando agente {agent_id} no banco de dados...")
    
    headers = {
        "X-API-Key": API_KEY
    }
    
    try:
        # Buscar o agente criado
        response = requests.get(
            f"{API_BASE_URL}/v1/agents/{agent_id}",
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status da verificação: {response.status_code}")
        
        if response.status_code == 200:
            agent_data = response.json()
            print("✅ Agente encontrado no banco!")
            print(f"📋 Dados do agente:")
            print(json.dumps(agent_data, indent=2, ensure_ascii=False))
            
            # Verificar se os campos provider e model estão corretos
            provider = agent_data.get("provider")
            model = agent_data.get("model")
            
            print(f"\n🔍 Validação dos campos:")
            print(f"   Provider: {provider} {'✅' if provider == 'gemini' else '❌'}")
            print(f"   Model: {model} {'✅' if model == 'gemini-2.5-flash' else '❌'}")
            
            return agent_data
            
        else:
            print(f"❌ Erro ao buscar agente: {response.status_code}")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Erro ao verificar agente: {e}")
        return None

def main():
    """Função principal"""
    print("🧪 TESTE DE CRIAÇÃO DE AGENTE GEMINI 2.5 FLASH")
    print("=" * 60)
    
    # Testar criação do agente
    agent_id = test_create_gemini_agent()
    
    if agent_id:
        # Verificar se foi salvo corretamente
        agent_data = verify_agent_in_database(agent_id)
        
        if agent_data:
            print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print(f"   ✅ Agente criado: {agent_id}")
            print(f"   ✅ Provider: {agent_data.get('provider')}")
            print(f"   ✅ Model: {agent_data.get('model')}")
        else:
            print(f"\n❌ TESTE FALHOU: Agente não encontrado no banco")
    else:
        print(f"\n❌ TESTE FALHOU: Não foi possível criar o agente")

if __name__ == "__main__":
    main()