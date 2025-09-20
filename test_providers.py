import requests
import json

BASE = 'http://localhost:8002'
H = {'X-API-Key': '151fb361-f295-4a4f-84c9-ec1f42599a67', 'Content-Type': 'application/json'}

print('=== CRIANDO AGENTE GEMINI ===')
gemini_payload = {
    'name': 'Teste Gemini Provider',
    'role': 'Assistente Gemini',
    'instructions': ['Você é um assistente usando Gemini.'],
    'model': 'gemini-2.5-flash',
    'provider': 'gemini'
}

r = requests.post(f'{BASE}/v1/agents', headers=H, data=json.dumps(gemini_payload), timeout=20)
print(f'Status: {r.status_code}')
if r.status_code in [200, 201]:
    data = r.json()
    print(f'Agente criado: {data.get("id")}')
    print(f'Provider: {data.get("provider")}')
    print(f'Model: {data.get("model")}')
    gemini_id = data.get("id")
else:
    print(f'Erro: {r.text}')
    gemini_id = None

print('\n=== CRIANDO AGENTE OPENAI ===')
openai_payload = {
    'name': 'Teste OpenAI Provider',
    'role': 'Assistente OpenAI',
    'instructions': ['Você é um assistente usando OpenAI.'],
    'model': 'gpt-4o-mini',
    'provider': 'openai'
}

r = requests.post(f'{BASE}/v1/agents', headers=H, data=json.dumps(openai_payload), timeout=20)
print(f'Status: {r.status_code}')
if r.status_code in [200, 201]:
    data = r.json()
    print(f'Agente criado: {data.get("id")}')
    print(f'Provider: {data.get("provider")}')
    print(f'Model: {data.get("model")}')
    openai_id = data.get("id")
else:
    print(f'Erro: {r.text}')
    openai_id = None

# Testar mensagens com os agentes criados
if gemini_id:
    print(f'\n=== TESTANDO MENSAGEM GEMINI ===')
    payload = [{
        'mensagem': 'Oi! Qual seu provider?',
        'agent_id': gemini_id,
        'debounce': 0,
        'session_id': '',
        'message_id': '123',
        'cliente_id': '',
        'user_id': 'test@lid',
        'id_conta': None
    }]
    
    r = requests.post(f'{BASE}/v1/messages', headers=H, data=json.dumps(payload), timeout=20)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        resp = r.json()
        usage = resp.get('agent_usage', {})
        print(f'Agent Usage: provider={usage.get("provider")}, model={usage.get("model")}')
    else:
        print(f'Erro: {r.text}')

if openai_id:
    print(f'\n=== TESTANDO MENSAGEM OPENAI ===')
    payload = [{
        'mensagem': 'Oi! Qual seu provider?',
        'agent_id': openai_id,
        'debounce': 0,
        'session_id': '',
        'message_id': '456',
        'cliente_id': '',
        'user_id': 'test@lid',
        'id_conta': None
    }]
    
    r = requests.post(f'{BASE}/v1/messages', headers=H, data=json.dumps(payload), timeout=20)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        resp = r.json()
        usage = resp.get('agent_usage', {})
        print(f'Agent Usage: provider={usage.get("provider")}, model={usage.get("model")}')
    else:
        print(f'Erro: {r.text}')