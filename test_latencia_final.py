import requests
import json
import uuid
import time

BASE = 'http://localhost:8002'
H = {'X-API-Key': '151fb361-f295-4a4f-84c9-ec1f42599a67', 'Content-Type': 'application/json'}

def test_latencia():
    session_id = str(uuid.uuid4())
    msg_payload = [
        {
            "mensagem": "Oi! Como você está?",
            "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
            "debounce": 0,
            "session_id": session_id,
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "user_id": "teste_latencia@lid",
            "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
        }
    ]

    print("🚀 Testando latência após correção...")
    start_time = time.time()

    try:
        r = requests.post(f'{BASE}/v1/messages', headers=H, data=json.dumps(msg_payload), timeout=30)
        end_time = time.time()
        
        print(f"⏱️ Tempo total: {(end_time - start_time)*1000:.1f}ms")
        print(f"📊 Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Resposta: {data.get('messages', [''])[0][:100]}...")
            if 'agent_usage' in data:
                print(f"🔧 Modelo: {data['agent_usage'].get('model', 'N/A')}")
                print(f"📈 Tokens: {data['agent_usage'].get('input_tokens', 0)} in / {data['agent_usage'].get('output_tokens', 0)} out")
        else:
            print(f"❌ Erro: {r.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_latencia()