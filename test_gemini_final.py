#!/usr/bin/env python3
"""
Teste específico para agentes Gemini após correções
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da API
API_BASE_URL = "http://localhost:80"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_gemini_agent():
    """Testa criação e uso de agente Gemini"""
    print("=== Teste do Agente Gemini ===")
    
    # 1. Criar agente Gemini
    print("1. Criando agente Gemini...")
    agent_data = {
        "name": "teste-gemini-final",
        "role": "Assistente Gemini de teste",
        "instructions": ["Você é um assistente Gemini que responde de forma criativa e útil."],
        "model": "google/gemini-pro",
        "provider": "google"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/agents", json=agent_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            agent_info = response.json()
            print(f"✅ Agente Gemini criado: {agent_info['agent']['id']}")
            agent_id = agent_info['agent']['id']
            
            # 2. Testar chat com agente Gemini
            print("\n2. Testando chat com agente Gemini...")
            chat_data = {
                "message": "Olá! Você pode me contar uma curiosidade interessante sobre inteligência artificial?",
                "agent_name": "teste-gemini-final",
                "user_id": "test-user-gemini"
            }
            
            chat_response = requests.post(f"{API_BASE_URL}/chat", json=chat_data, headers=headers)
            print(f"Status: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                print(f"✅ Resposta do Gemini: {chat_result['response'][:200]}...")
                return True
            else:
                print(f"❌ Erro no chat: {chat_response.text}")
                return False
                
        else:
            print(f"❌ Erro na criação: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_gemini_model_creation():
    """Testa criação direta do modelo Gemini"""
    print("\n=== Teste de Criação do Modelo Gemini ===")
    
    try:
        # Importa e testa criação do modelo
        from agents import create_model_from_config
        
        # Testa configuração Gemini
        config = {
            "model": "google/gemini-pro",
            "provider": "google"
        }
        
        model = create_model_from_config(config)
        print(f"✅ Modelo Gemini criado com sucesso: {type(model)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação do modelo: {e}")
        return False

def main():
    """Executa todos os testes Gemini"""
    print("🧪 Iniciando testes específicos do Gemini...\n")
    
    # Verifica se a API está rodando
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", headers=headers)
        if health_response.status_code != 200:
            print("❌ API não está respondendo. Certifique-se de que está rodando.")
            return
    except:
        print("❌ Não foi possível conectar à API.")
        return
    
    # Executa testes
    results = []
    
    # Teste 1: Criação do modelo
    results.append(test_gemini_model_creation())
    
    # Teste 2: Agente via API
    results.append(test_gemini_agent())
    
    # Resumo
    print("\n=== Resumo dos Testes Gemini ===")
    print(f"✅ Criação do modelo: {'OK' if results[0] else 'FALHOU'}")
    print(f"✅ Agente via API: {'OK' if results[1] else 'FALHOU'}")
    
    if all(results):
        print("\n🎉 Todos os testes Gemini passaram!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()