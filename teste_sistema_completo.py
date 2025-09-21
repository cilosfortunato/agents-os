#!/usr/bin/env python3
"""
Teste Final Integrado do Sistema AgentOS
Verifica se todos os componentes estão funcionando em conjunto
"""

import os
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_api_completa():
    """Testa a API completa com um agente real"""
    print("🧪 TESTANDO API COMPLETA...")
    
    try:
        # Dados de teste baseados na estrutura fornecida
        test_data = {
            "mensagem": "Olá, como você pode me ajudar?",
            "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
            "debounce": 15000,
            "session_id": "test-session-" + str(int(time.time())),
            "message_id": "test-msg-" + str(int(time.time())),
            "cliente_id": "",
            "user_id": "test-user@lid",
            "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
        }
        
        # Testa endpoint local
        url = "http://localhost:8000/v1/chat"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": os.getenv("API_AUTH_KEY", "151fb361-f295-4a4f-84c9-ec1f42599a67")
        }
        
        print(f"📡 Enviando requisição para: {url}")
        print(f"📋 Dados: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=[test_data], headers=headers, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resposta recebida:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Verifica estrutura da resposta
            if "messages" in result and len(result["messages"]) > 0:
                print("✅ Estrutura de resposta válida")
                return True
            else:
                print("❌ Estrutura de resposta inválida")
                return False
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - API não está rodando?")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_webhook_connectivity():
    """Testa conectividade com o webhook"""
    print("\n🔗 TESTANDO CONECTIVIDADE DO WEBHOOK...")
    
    webhook_url = os.getenv("OUTBOUND_WEBHOOK_URL")
    if not webhook_url:
        print("❌ URL do webhook não configurada")
        return False
    
    try:
        response = requests.get(webhook_url, timeout=10)
        print(f"📊 Status do webhook: {response.status_code}")
        
        # 404 é esperado para GET, mas indica que o servidor está respondendo
        if response.status_code in [200, 404, 405]:
            print("✅ Webhook acessível")
            return True
        else:
            print(f"⚠️ Webhook retornou status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao acessar webhook: {e}")
        return False

def test_environment_variables():
    """Verifica se todas as variáveis essenciais estão configuradas"""
    print("\n🔧 VERIFICANDO VARIÁVEIS DE AMBIENTE...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_SERVICE_ROLE_KEY",
        "OUTBOUND_WEBHOOK_URL",
        "MEM0_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Configurada")
    
    if missing_vars:
        print(f"❌ Variáveis faltando: {missing_vars}")
        return False
    else:
        print("✅ Todas as variáveis essenciais configuradas")
        return True

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTE FINAL INTEGRADO DO SISTEMA AGNOS")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Variáveis de ambiente
    env_ok = test_environment_variables()
    results.append(("Variáveis de Ambiente", env_ok))
    
    # Teste 2: Conectividade do webhook
    webhook_ok = test_webhook_connectivity()
    results.append(("Conectividade Webhook", webhook_ok))
    
    # Teste 3: API completa (só se as outras passaram)
    if env_ok:
        api_ok = test_api_completa()
        results.append(("API Completa", api_ok))
    else:
        print("\n⏭️ Pulando teste da API devido a problemas de configuração")
        results.append(("API Completa", False))
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        return True
    elif passed >= total * 0.7:  # 70% ou mais
        print("⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        return True
    else:
        print("❌ SISTEMA COM PROBLEMAS CRÍTICOS")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)