#!/usr/bin/env python3
"""
Teste direto da API do Google AI usando requests
"""
import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_google_ai_direct():
    """Testa a API do Google AI diretamente usando requests"""
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_AI_API_KEY não encontrada no ambiente")
        return False
    
    print(f"🔑 Usando API Key: {api_key[:20]}...")
    
    # URL da API do Google AI
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    # Payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Olá! Como você está?"
                    }
                ]
            }
        ]
    }
    
    try:
        print("🚀 Fazendo requisição para a API do Google AI...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ Resposta da API: {content}")
                return True
            else:
                print(f"❌ Resposta inesperada: {data}")
                return False
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste Direto da API do Google AI ===")
    success = test_google_ai_direct()
    
    if success:
        print("\n✅ Teste passou! A API key está funcionando.")
    else:
        print("\n❌ Teste falhou! Verifique a API key.")