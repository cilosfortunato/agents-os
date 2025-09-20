#!/usr/bin/env python3
import requests
import json
import uuid
import time

def test_memoria_fix():
    """Testa se o erro do OpenAI foi resolvido após a atualização do Mem0"""
    
    url = 'http://localhost:8002/v1/messages'
    headers = {
        'X-API-Key': '151fb361-f295-4a4f-84c9-ec1f42599a67',
        'Content-Type': 'application/json'
    }

    # Payload que deve ativar o sistema de memória
    payload = [
        {
            "mensagem": "Teste de memória - você lembra de mim? Meu nome é João e gosto de pizza.",
            "agent_id": "1677dc47-20d0-442a-80a8-171f00d39d39",
            "debounce": 0,
            "session_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "user_id": "teste_memoria_fix@lid",
            "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
        }
    ]

    print("🔍 Testando sistema de memória após correção do OpenAI...")
    print(f"📤 Enviando mensagem para: {url}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        end_time = time.time()
        
        print(f"⏱️  Tempo de resposta: {end_time - start_time:.2f}s")
        print(f"📊 Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sucesso! Resposta recebida:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Verificar se há mensagens de erro relacionadas ao OpenAI
            messages = result.get('messages', [])
            error_found = False
            
            for msg in messages:
                msg_str = str(msg)
                if any(error_term in msg_str for error_term in [
                    'openai.ChatCompletion', 
                    'no longer supported', 
                    'openai>=1.0.0',
                    'openai migrate'
                ]):
                    print("❌ ERRO: Ainda há erro do OpenAI na resposta!")
                    print(f"   Mensagem com erro: {msg}")
                    error_found = True
                    break
            
            if not error_found:
                print("✅ SUCESSO: Nenhum erro do OpenAI detectado na resposta!")
                print("🎉 O sistema de memória está funcionando corretamente!")
                
                # Verificar se o agent_usage está presente
                agent_usage = result.get('agent_usage')
                if agent_usage:
                    print(f"📈 Uso do agente: {agent_usage}")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print("📄 Resposta:")
            print(response.text[:1000])
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout na requisição (30s)")
    except requests.exceptions.ConnectionError:
        print("🔌 Erro de conexão - API pode não estar rodando")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_memoria_fix()