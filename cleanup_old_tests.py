#!/usr/bin/env python3
"""
Script para limpeza de arquivos de teste antigos
Mantém apenas os arquivos essenciais e funcionais
"""

import os
import glob

# Arquivos de teste que devem ser MANTIDOS (essenciais)
KEEP_FILES = {
    'verificacao_final_completa.py',  # Verificação final
    'test_gemini_final.py',          # Teste Gemini funcional
    'test_api_endpoints_final.py',   # Testes de API finais
    'test_sistema_final.py',         # Teste do sistema final
    'test_memoria_final.py',         # Teste de memória final
}

def cleanup_test_files():
    """Remove arquivos de teste antigos, mantendo apenas os essenciais"""
    
    # Encontra todos os arquivos de teste
    test_files = glob.glob('test_*.py') + glob.glob('teste_*.py')
    
    files_to_remove = []
    files_to_keep = []
    
    for file in test_files:
        if file in KEEP_FILES:
            files_to_keep.append(file)
        else:
            files_to_remove.append(file)
    
    print(f"🔍 Encontrados {len(test_files)} arquivos de teste")
    print(f"✅ Mantendo {len(files_to_keep)} arquivos essenciais")
    print(f"🗑️  Removendo {len(files_to_remove)} arquivos antigos")
    
    if files_to_keep:
        print("\n📋 Arquivos mantidos:")
        for file in sorted(files_to_keep):
            print(f"  ✅ {file}")
    
    if files_to_remove:
        print(f"\n🗑️  Removendo {len(files_to_remove)} arquivos antigos...")
        for file in sorted(files_to_remove):
            try:
                os.remove(file)
                print(f"  ❌ {file}")
            except Exception as e:
                print(f"  ⚠️  Erro ao remover {file}: {e}")
    
    # Também remove arquivos JSON de teste antigos
    json_test_files = glob.glob('test_*.json') + glob.glob('teste_*.json')
    json_files_to_remove = [f for f in json_test_files if 'final' not in f.lower()]
    
    if json_files_to_remove:
        print(f"\n🗑️  Removendo {len(json_files_to_remove)} arquivos JSON de teste...")
        for file in sorted(json_files_to_remove):
            try:
                os.remove(file)
                print(f"  ❌ {file}")
            except Exception as e:
                print(f"  ⚠️  Erro ao remover {file}: {e}")
    
    print(f"\n🎉 Limpeza concluída!")
    print(f"📊 Resumo:")
    print(f"  - Arquivos Python mantidos: {len(files_to_keep)}")
    print(f"  - Arquivos Python removidos: {len(files_to_remove)}")
    print(f"  - Arquivos JSON removidos: {len(json_files_to_remove)}")
    print(f"  - Total removido: {len(files_to_remove) + len(json_files_to_remove)}")

if __name__ == "__main__":
    cleanup_test_files()