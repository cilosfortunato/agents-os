import requests
import json

BASE = 'http://localhost:8002'
H = {'X-API-Key': '151fb361-f295-4a4f-84c9-ec1f42599a67', 'Content-Type': 'application/json'}

print('=== HEALTH ===')
r = requests.get(f'{BASE}/v1/health', headers=H, timeout=10)
print(f'Status: {r.status_code}')

print('\n=== AGENTS ===')
r = requests.get(f'{BASE}/v1/agents', headers=H, timeout=15)
data = r.json()
print(f'Status: {r.status_code}')
agents = data.get('agents', [])
print(f'Total agents: {len(agents)}')

if agents:
    agent = agents[0]
    print(f'First agent: {agent.get("name")} - {agent.get("provider")} - {agent.get("model")}')
    
    print('\n=== TEST MESSAGE ===')
    payload = [{
        'mensagem': 'Oi! Qual seu nome?',
        'agent_id': agent['id'],
        'debounce': 0,
        'session_id': '',
        'message_id': '123',
        'cliente_id': '',
        'user_id': 'test@lid',
        'id_conta': None
    }]
    
    r = requests.post(f'{BASE}/v1/messages', headers=H, data=json.dumps(payload), timeout=20)
    print(f'Message Status: {r.status_code}')
    
    if r.status_code == 200:
        resp = r.json()
        usage = resp.get('agent_usage', {})
        print(f'Agent Usage: provider={usage.get("provider")}, model={usage.get("model")}')
        print(f'Messages: {resp.get("messages", [])}')
    else:
        print(f'Error: {r.text}')
else:
    print('No agents found')