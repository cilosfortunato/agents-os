#!/usr/bin/env python3
"""
Script para testar a autenticação com Google Cloud usando Service Account
"""

import os
import json
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.generativeai as genai

def test_google_auth():
    """Testa a autenticação com Google Cloud"""
    print("=== Teste de Autenticação Google Cloud ===\n")
    
    try:
        # Carrega as credenciais do arquivo JSON
        credentials_path = "google_credentials.json"
        
        if not os.path.exists(credentials_path):
            print(f"❌ Arquivo de credenciais não encontrado: {credentials_path}")
            return False
            
        print(f"✅ Arquivo de credenciais encontrado: {credentials_path}")
        
        # Carrega as credenciais
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        print("✅ Credenciais carregadas com sucesso")
        
        # Testa se as credenciais são válidas
        request = Request()
        credentials.refresh(request)
        
        print("✅ Token de acesso obtido com sucesso")
        print(f"   - Project ID: {credentials.project_id}")
        print(f"   - Service Account: {credentials.service_account_email}")
        
        # Testa configuração do Generative AI
        print("\n=== Teste Generative AI ===")
        
        # Configura a API Key (se disponível)
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if api_key:
            print("✅ GOOGLE_AI_API_KEY encontrada no ambiente")
            genai.configure(api_key=api_key)
            
            # Lista modelos disponíveis
            try:
                models = list(genai.list_models())
                print(f"✅ {len(models)} modelos disponíveis:")
                for model in models[:3]:  # Mostra apenas os primeiros 3
                    print(f"   - {model.name}")
                    
                # Testa geração de conteúdo
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Diga apenas 'Olá, teste funcionando!'")
                print(f"✅ Teste de geração: {response.text}")
                
            except Exception as e:
                print(f"⚠️  Erro ao testar Generative AI: {e}")
        else:
            print("⚠️  GOOGLE_AI_API_KEY não encontrada no ambiente")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return False

def test_vertex_ai_client():
    """Testa o cliente Vertex AI personalizado"""
    print("\n=== Teste Vertex AI Client ===")
    
    try:
        # Importa o cliente real
        from vertex_ai_client import VertexAIClient
        
        # Configura as credenciais como variável de ambiente
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials.json'
        
        # Inicializa o cliente
        client = VertexAIClient()
        print("✅ VertexAIClient inicializado")
        
        # Testa geração de conteúdo
        messages = [{"role": "user", "content": "Diga apenas 'Cliente Vertex AI funcionando!'"}]
        response = client.generate_content(messages=messages)
        
        print(f"✅ Resposta do Vertex AI: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Vertex AI Client: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando testes de autenticação Google Cloud...\n")
    
    # Teste 1: Autenticação básica
    auth_success = test_google_auth()
    
    # Teste 2: Cliente Vertex AI
    vertex_success = test_vertex_ai_client()
    
    print("\n=== Resumo dos Testes ===")
    print(f"Autenticação Google Cloud: {'✅ Sucesso' if auth_success else '❌ Falhou'}")
    print(f"Vertex AI Client: {'✅ Sucesso' if vertex_success else '❌ Falhou'}")
    
    if auth_success and vertex_success:
        print("\n🎉 Todos os testes passaram! A API Key está funcionando.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique as configurações.")