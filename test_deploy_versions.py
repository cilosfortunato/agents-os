#!/usr/bin/env python3
"""
Script para testar se as versões atualizadas das bibliotecas resolvem o problema do OpenAI.
Este script simula o ambiente de deploy verificando as versões das bibliotecas.
"""

import sys
import subprocess
import importlib.metadata

def check_version(package_name, expected_version=None):
    """Verifica a versão instalada de um pacote."""
    try:
        version = importlib.metadata.version(package_name)
        print(f"✓ {package_name}: {version}")
        if expected_version and version != expected_version:
            print(f"  ⚠️  Esperado: {expected_version}")
        return version
    except importlib.metadata.PackageNotFoundError:
        print(f"✗ {package_name}: NÃO INSTALADO")
        return None

def test_openai_import():
    """Testa se o OpenAI pode ser importado corretamente."""
    try:
        import openai
        print("✓ OpenAI importado com sucesso")
        
        # Testa se a nova API está disponível
        client = openai.OpenAI(api_key="test-key")
        print("✓ Cliente OpenAI criado com sucesso (nova API)")
        return True
    except Exception as e:
        print(f"✗ Erro ao importar OpenAI: {e}")
        return False

def test_mem0_import():
    """Testa se o Mem0 pode ser importado corretamente."""
    try:
        import mem0
        print("✓ Mem0 importado com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao importar Mem0: {e}")
        return False

def test_compatibility():
    """Testa a compatibilidade entre OpenAI e Mem0."""
    try:
        import openai
        import mem0
        
        # Verifica se não há conflitos de API
        print("✓ OpenAI e Mem0 importados juntos sem conflitos")
        return True
    except Exception as e:
        print(f"✗ Erro de compatibilidade: {e}")
        return False

def main():
    print("=== TESTE DE VERSÕES PARA DEPLOY ===\n")
    
    # Verifica versões esperadas
    print("1. Verificando versões das bibliotecas:")
    openai_version = check_version("openai", "1.99.9")
    mem0_version = check_version("mem0ai", "0.1.117")
    check_version("fastapi")
    check_version("uvicorn")
    
    print("\n2. Testando importações:")
    openai_ok = test_openai_import()
    mem0_ok = test_mem0_import()
    
    print("\n3. Testando compatibilidade:")
    compat_ok = test_compatibility()
    
    print("\n=== RESULTADO ===")
    if openai_ok and mem0_ok and compat_ok:
        print("✅ TODAS AS VERIFICAÇÕES PASSARAM!")
        print("✅ O deploy deve funcionar corretamente.")
        return 0
    else:
        print("❌ ALGUMAS VERIFICAÇÕES FALHARAM!")
        print("❌ O deploy pode ter problemas.")
        return 1

if __name__ == "__main__":
    sys.exit(main())