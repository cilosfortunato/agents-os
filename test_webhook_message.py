import requests
import json

BASE = 'http://localhost:8002'
H = {'X-API-Key': '151fb361-f295-4a4f-84c9-ec1f42599a67', 'Content-Type': 'application/json'}

# Mensagem conforme solicitado
payload = [{
    'mensagem': 'Olá, boa tarde! Eu vi um post de vocês no Instagram e fiquei interessada na harmonização facial. Nunca fiz e tenho algumas dúvidas, funciona para o meu tipo de rosto?',
    'agent_id': 'da93fcc7-cf93-403e-aa99-9e295080d692',
    'user_id': 'c4a7b2d8-1e9f-4a2b-8d6c-3e5f7a9b0c1d',
    'session_id': 'a1b2c3d4-5e6f-7a8b-9c0d-1e2f3a4b5c6d',
    'id_conta': '8b1e3e5e-2f3b-4c8a-9e1d-5a6b7c8d9f0a',
    'debounce': 0,
    'message_id': '12345',
    'cliente_id': ''
}]

print('=== ENVIANDO MENSAGEM ===')
print('Payload:', json.dumps(payload, indent=2, ensure_ascii=False))

try:
    r = requests.post(f'{BASE}/v1/messages', headers=H, data=json.dumps(payload), timeout=30)
    print(f'Status: {r.status_code}')
    
    if r.status_code == 200:
        resp = r.json()
        print('Resposta ACK:')
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        
        # Verificar se tem agent_usage
        usage = resp.get('agent_usage', {})
        print(f'Agent Usage: provider={usage.get("provider")}, model={usage.get("model")}')
        
        # Verificar se o agente existe
        print('\n=== VERIFICANDO AGENTE ===')
        agent_r = requests.get(f'{BASE}/v1/agents/{payload[0]["agent_id"]}', headers=H, timeout=15)
        print(f'Agent Status: {agent_r.status_code}')
        if agent_r.status_code == 200:
            agent_data = agent_r.json()
            print('Agente encontrado:')
            print(json.dumps(agent_data, indent=2, ensure_ascii=False))
        else:
            print(f'Agente não encontrado: {agent_r.text}')
            
    else:
        print(f'Erro: {r.text}')
        
except Exception as e:
    print(f'Erro na requisição: {e}')

# Testar webhook
print('\n=== TESTANDO WEBHOOK ===')
webhook_url = 'https://webhook.doxagrowth.com.br/webhook/recebimentos-mensagens-agentos'
try:
    webhook_r = requests.get(webhook_url, timeout=10)
    print(f'Webhook GET Status: {webhook_r.status_code}')
    print(f'Webhook Response: {webhook_r.text}')
except Exception as e:
    print(f'Erro ao testar webhook: {e}')