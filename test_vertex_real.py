#!/usr/bin/env python3
"""
Teste do VertexAIClientReal com Service Account
"""

import os
from vertex_ai_client_real import VertexAIClientReal, get_vertex_ai_client

def test_vertex_real():
    """Testa o cliente real do Vertex AI"""
    print("=== Teste VertexAIClientReal ===\n")
    
    try:
        # Configurar credenciais
        credentials_path = "google_credentials.json"
        
        # Teste 1: Inicialização com Service Account
        print("1. Testando inicialização com Service Account...")
        client = VertexAIClientReal(
            credentials_path="./service_account.json",
            project_id="projetos-n8n-438817",
            location="us-central1"
        )
        print("✅ Cliente inicializado com Service Account")
        print(f"Project ID: {client.project_id}")
        print(f"Método de autenticação: {client.auth_method}")
        
        # Teste 2: Teste de conexão
        print("\n2. Testando conexão...")
        connection_test = client.test_connection()
        print(f"Status: {connection_test['status']}")
        print(f"Método de auth: {connection_test['auth_method']}")
        print(f"Projeto: {connection_test['project_id']}")
        
        if connection_test['status'] == 'success':
            print("✅ Conexão estabelecida com sucesso")
        else:
            print(f"❌ Erro na conexão: {connection_test['message']}")
            return False
        
        # Teste 3: Geração de conteúdo com messages
        print("\n3. Testando geração com messages...")
        messages = [
            {"role": "user", "content": "Diga apenas 'Teste de messages funcionando!'"}
        ]
        response = client.generate_content(messages=messages)
        
        if response and 'candidates' in response:
            text = response['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Resposta: {text}")
        else:
            print("❌ Erro na geração com messages")
            return False
        
        # Teste 4: Geração de conteúdo com prompt direto
        print("\n4. Testando geração com prompt...")
        response = client.generate_content(prompt="Diga apenas 'Teste de prompt funcionando!'")
        
        if response and 'candidates' in response:
            text = response['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Resposta: {text}")
        else:
            print("❌ Erro na geração com prompt")
            return False
        
        # Teste 5: Listagem de modelos
        print("\n5. Testando listagem de modelos...")
        models = client.list_models()
        
        if models:
            print(f"✅ {len(models)} modelos encontrados:")
            for model in models[:3]:  # Mostra apenas os primeiros 3
                print(f"   - {model['name']}")
        else:
            print("⚠️  Nenhum modelo encontrado")
        
        # Teste 6: Função get_vertex_ai_client
        print("\n6. Testando função get_vertex_ai_client...")
        client2 = get_vertex_ai_client(credentials_path=credentials_path)
        response = client2.generate_content(prompt="Teste da função global")
        
        if response and 'candidates' in response:
            text = response['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Função global funcionando: {text[:50]}...")
        else:
            print("❌ Erro na função global")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_with_env_credentials():
    """Testa usando credenciais do ambiente"""
    print("\n=== Teste com Credenciais do Ambiente ===\n")
    
    try:
        # Configurar variável de ambiente
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials.json'
        
        # Inicializar cliente sem parâmetros
        client = VertexAIClientReal()
        print("✅ Cliente inicializado com credenciais do ambiente")
        
        # Testar geração
        response = client.generate_content(prompt="Teste com credenciais do ambiente")
        
        if response and 'candidates' in response:
            text = response['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Resposta: {text[:50]}...")
            return True
        else:
            print("❌ Erro na geração")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando testes do VertexAIClientReal...\n")
    
    # Teste 1: Cliente com Service Account
    test1_success = test_vertex_real()
    
    # Teste 2: Cliente com credenciais do ambiente
    test2_success = test_with_env_credentials()
    
    print("\n=== Resumo dos Testes ===")
    print(f"VertexAIClientReal: {'✅ Sucesso' if test1_success else '❌ Falhou'}")
    print(f"Credenciais do ambiente: {'✅ Sucesso' if test2_success else '❌ Falhou'}")
    
    if test1_success and test2_success:
        print("\n🎉 Todos os testes passaram! O cliente real está funcionando.")
    else:
        print("\n⚠️  Alguns testes falharam.")