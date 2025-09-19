#!/usr/bin/env python3
"""
Teste de conectividade e configuração do Mem0
"""

import os
from dotenv import load_dotenv
from mem0 import MemoryClient
import json

# Carrega variáveis de ambiente
load_dotenv()

def test_env_variables():
    """Testa se as variáveis de ambiente estão configuradas"""
    print("=" * 60)
    print("TESTE DE VARIÁVEIS DE AMBIENTE")
    print("=" * 60)
    
    required_vars = [
        "OPENAI_API_KEY",
        "MEM0_API_KEY"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}...{value[-10:] if len(value) > 20 else value}")
        else:
            print(f"❌ {var}: NÃO CONFIGURADA")
    
    print()

def test_mem0_connection():
    """Testa a conexão com o Mem0"""
    print("=" * 60)
    print("TESTE DE CONEXÃO COM MEM0")
    print("=" * 60)
    
    try:
        # Inicializa o cliente
        client = MemoryClient()
        print("✅ Cliente Mem0 inicializado com sucesso")
        
        # Testa uma operação simples
        test_user_id = "test_connection_user"
        test_messages = [
            {"role": "user", "content": "Meu nome é João e eu gosto de café"},
            {"role": "assistant", "content": "Olá João! Entendi que você gosta de café."}
        ]
        
        print(f"📤 Testando adição de memória para user_id: {test_user_id}")
        result = client.add(messages=test_messages, user_id=test_user_id)
        print(f"✅ Memória adicionada: {result}")
        
        # Testa busca
        print(f"🔍 Testando busca de memórias...")
        memories = client.search(query="nome café", user_id=test_user_id, limit=3)
        print(f"✅ Memórias encontradas: {len(memories) if memories else 0}")
        
        if memories:
            print("📋 Memórias:")
            for i, memory in enumerate(memories, 1):
                print(f"   {i}. {memory}")
        
        # Testa recuperação de todas as memórias
        print(f"📚 Testando recuperação de todas as memórias...")
        all_memories = client.get_all(user_id=test_user_id)
        print(f"✅ Total de memórias: {len(all_memories) if all_memories else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com Mem0: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")
        return False

def test_memory_manager():
    """Testa o gerenciador de memória local"""
    print("=" * 60)
    print("TESTE DO GERENCIADOR DE MEMÓRIA LOCAL")
    print("=" * 60)
    
    try:
        from memory import memory_manager
        print("✅ MemoryManager importado com sucesso")
        
        # Testa salvamento de conversa
        test_user_id = "test_manager_user"
        success = memory_manager.save_conversation(
            user_id=test_user_id,
            user_message="Meu nome é Maria e tenho 30 anos",
            assistant_response="Olá Maria! Prazer em conhecê-la.",
            agent_name="TestAgent"
        )
        
        if success:
            print("✅ Conversa salva com sucesso")
        else:
            print("❌ Falha ao salvar conversa")
        
        # Testa busca
        memories = memory_manager.search_memories(
            user_id=test_user_id,
            query="nome idade",
            limit=3
        )
        
        print(f"✅ Busca realizada: {len(memories)} memórias encontradas")
        
        if memories:
            print("📋 Memórias encontradas:")
            for i, memory in enumerate(memories, 1):
                print(f"   {i}. {memory}")
        
        return success
        
    except Exception as e:
        print(f"❌ Erro no gerenciador de memória: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")
        return False

def test_api_memory_endpoint():
    """Testa o endpoint de memória da API"""
    print("=" * 60)
    print("TESTE DO ENDPOINT DE MEMÓRIA DA API")
    print("=" * 60)
    
    import requests
    
    try:
        # Testa busca de memória via API
        response = requests.get(
            "http://localhost:80/v1/memory/search",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67"
            },
            params={
                "user_id": "test_api_user",
                "query": "teste",
                "limit": 3
            },
            timeout=10
        )
        
        print(f"Status da API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de memória funcionando")
            print(f"📊 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erro na API: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DO SISTEMA DE MEMÓRIA")
    print("=" * 60)
    
    # 1. Testa variáveis de ambiente
    test_env_variables()
    
    # 2. Testa conexão direta com Mem0
    mem0_ok = test_mem0_connection()
    
    # 3. Testa gerenciador de memória local
    manager_ok = test_memory_manager()
    
    # 4. Testa endpoint da API
    api_ok = test_api_memory_endpoint()
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Mem0 Direto: {'✅' if mem0_ok else '❌'}")
    print(f"Memory Manager: {'✅' if manager_ok else '❌'}")
    print(f"API Endpoint: {'✅' if api_ok else '❌'}")
    
    if all([mem0_ok, manager_ok, api_ok]):
        print("\n🎉 Todos os testes passaram! O sistema de memória está funcionando.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as configurações e logs.")