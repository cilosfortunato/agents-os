import os
import requests
import json
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

print('=== VERIFICANDO CONFIGURAÇÃO ATUAL DO WEBHOOK ===')

# Verificar variáveis de ambiente
webhook_url = os.getenv("OUTBOUND_WEBHOOK_URL", "https://webhook.doxagrowth.com.br/webhook/recebimentos-mensagens-agentos")
webhook_key = os.getenv("OUTBOUND_WEBHOOK_API_KEY", "")

print(f'OUTBOUND_WEBHOOK_URL: {webhook_url}')
print(f'WEBHOOK_API_KEY: {webhook_key}')

# Verificar se há alguma sobrescrita no código
print('\n=== SIMULANDO ENVIO DE WEBHOOK ===')

# Simular o que o código faz
payload = {
    "messages": ["Teste de webhook"],
    "transferir": False,
    "session_id": "test-session",
    "user_id": "test-user",
    "agent_id": "test-agent",
    "custom": [],
    "agent_usage": {"provider": "gemini", "model": "gemini-2.5-flash"}
}

headers = {
    "Content-Type": "application/json"
}
if webhook_key:
    headers["X-API-Key"] = webhook_key

print(f'URL que seria usada: {webhook_url}')
print(f'Headers: {headers}')
print(f'Payload: {json.dumps(payload, indent=2)}')

# Testar se o webhook responde
print('\n=== TESTANDO WEBHOOK REAL ===')
try:
    # Fazer um POST de teste
    resp = requests.post(webhook_url, headers=headers, data=json.dumps(payload), timeout=10)
    print(f'Status: {resp.status_code}')
    print(f'Response: {resp.text[:500]}')
except Exception as e:
    print(f'Erro: {e}')

# Verificar se há alguma configuração no sistema
print('\n=== VERIFICANDO VARIÁVEIS DO SISTEMA ===')
for key, value in os.environ.items():
    if 'webhook' in key.lower() or 'outbound' in key.lower():
        print(f'{key}: {value}')