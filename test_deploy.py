#!/usr/bin/env python3
"""
Script de teste para verificar se todas as dependências estão funcionando
corretamente no ambiente de deploy.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Testa todas as importações necessárias"""
    print("🔍 Testando importações...")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Uvicorn: {e}")
        return False
    
    try:
        import openai
        print(f"✅ OpenAI: {openai.__version__}")
    except ImportError as e:
        print(f"❌ OpenAI: {e}")
        return False
    
    try:
        import mem0
        print(f"✅ Mem0: {mem0.__version__}")
    except ImportError as e:
        print(f"❌ Mem0: {e}")
        return False
    
    try:
        import pinecone
        print(f"✅ Pinecone: {pinecone.__version__}")
    except ImportError as e:
        print(f"❌ Pinecone: {e}")
        return False
    
    try:
        import dotenv
        print(f"✅ Python-dotenv: OK")
    except ImportError as e:
        print(f"❌ Python-dotenv: {e}")
        return False
    
    return True

def test_env_vars():
    """Testa se as variáveis de ambiente estão configuradas"""
    print("\n🔍 Testando variáveis de ambiente...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'OPENROUTER_API_KEY', 
        'MEM0_API_KEY',
        'X_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Configurada")
        else:
            print(f"❌ {var}: Não encontrada")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_local_imports():
    """Testa se os módulos locais podem ser importados"""
    print("\n🔍 Testando módulos locais...")
    
    try:
        from agents import get_all_agents
        print("✅ agents.py: OK")
    except ImportError as e:
        print(f"❌ agents.py: {e}")
        return False
    
    try:
        from teams import get_all_teams
        print("✅ teams.py: OK")
    except ImportError as e:
        print(f"❌ teams.py: {e}")
        return False
    
    try:
        from memory import memory_manager
        print("✅ memory.py: OK")
    except ImportError as e:
        print(f"❌ memory.py: {e}")
        return False
    
    try:
        from config import Config
        print("✅ config.py: OK")
    except ImportError as e:
        print(f"❌ config.py: {e}")
        return False
    
    return True

def test_api_creation():
    """Testa se a API pode ser criada"""
    print("\n🔍 Testando criação da API...")
    
    try:
        from api import create_api_app
        app = create_api_app()
        print("✅ API criada com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar API: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de deploy...\n")
    
    # Carrega variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    tests = [
        ("Importações", test_imports),
        ("Variáveis de ambiente", test_env_vars),
        ("Módulos locais", test_local_imports),
        ("Criação da API", test_api_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM! Deploy deve funcionar.")
        sys.exit(0)
    else:
        print("⚠️  ALGUNS TESTES FALHARAM! Verifique os problemas acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()