#!/usr/bin/env python3
"""
Teste final completo do sistema de memória com busca inteligente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_complete_memory_system():
    """Testa o sistema completo de memória via API"""
    print("🧠 TESTE FINAL COMPLETO DO SISTEMA DE MEMÓRIA")
    print("=" * 60)
    
    # Configuração da API
    base_url = "http://localhost:8002"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
    }
    
    # User ID que sabemos que tem dados
    user_id = "test_user_memory"
    session_id = "test_session_final"
    agent_id = "test_agent_123"
    
    # Sequência de testes
    test_cases = [
        {
            "name": "Pergunta sobre nome",
            "message": "Você se lembra do meu nome?",
            "expected_keywords": ["joão", "nome"]
        },
        {
            "name": "Pergunta sobre comida",
            "message": "O que eu gosto de comer?",
            "expected_keywords": ["pizza", "gosto"]
        },
        {
            "name": "Pergunta combinada",
            "message": "Qual é o meu nome e o que eu gosto de comer?",
            "expected_keywords": ["joão", "pizza"]
        },
        {
            "name": "Nova informação",
            "message": "Meu nome é João e eu adoro pizza margherita",
            "expected_keywords": ["joão", "pizza", "margherita"]
        },
        {
            "name": "Verificação da nova informação",
            "message": "Que tipo de pizza eu gosto?",
            "expected_keywords": ["margherita", "pizza"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 TESTE {i}: {test_case['name']}")
        print(f"📝 Mensagem: '{test_case['message']}'")
        print("-" * 50)
        
        # Prepara o payload
        payload = {
            "mensagem": test_case['message'],
            "agent_id": agent_id,
            "session_id": session_id,
            "user_id": user_id,
            "debounce": 0
        }
        
        try:
            # Faz a requisição
            response = requests.post(
                f"{base_url}/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                if messages:
                    agent_response = messages[0]
                    print(f"🤖 Resposta: {agent_response}")
                    
                    # Verifica se a resposta contém palavras-chave esperadas
                    response_lower = agent_response.lower()
                    found_keywords = []
                    
                    for keyword in test_case['expected_keywords']:
                        if keyword.lower() in response_lower:
                            found_keywords.append(keyword)
                    
                    print(f"🔍 Palavras-chave encontradas: {found_keywords}")
                    
                    # Avalia o sucesso
                    if found_keywords:
                        print("✅ SUCESSO: Agente demonstrou memória!")
                    else:
                        print("⚠️  PARCIAL: Resposta gerada, mas sem evidência clara de memória")
                else:
                    print("❌ FALHA: Nenhuma mensagem retornada")
            else:
                print(f"❌ FALHA: Erro HTTP {response.status_code}")
                print(f"Resposta: {response.text}")
                
        except Exception as e:
            print(f"❌ ERRO: {e}")
        
        # Pausa entre testes
        import time
        time.sleep(1)
    
    print(f"\n🎯 TESTE FINAL CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    test_complete_memory_system()