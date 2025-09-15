import os
from dotenv import load_dotenv
from mem0 import MemoryClient

# Carrega as variáveis de ambiente
load_dotenv()

# Inicializa o cliente Mem0
memory_client = MemoryClient()

# ID do usuário usado pelo time (formato: user_id_team_team_id)
team_user_id = "default_user_team_57daeaa8-861a-4c33-9d0c-1cbeafa12b07"

print(f"Buscando memórias para: {team_user_id}")
print("=" * 50)

try:
    # Busca todas as memórias do usuário
    memories = memory_client.get_all(user_id=team_user_id)
    
    if memories:
        print(f"Encontradas {len(memories)} memórias:")
        for i, memory in enumerate(memories, 1):
            print(f"\nMemória {i}:")
            print(f"ID: {memory.get('id', 'N/A')}")
            print(f"Memória completa: {memory}")
            print(f"Texto: {memory.get('memory', memory.get('text', 'N/A'))}")
            print(f"Data: {memory.get('created_at', 'N/A')}")
    else:
        print("Nenhuma memória encontrada.")
        
    # Testa busca por query específica
    print("\n" + "=" * 50)
    print("Testando busca por 'João':")
    search_results = memory_client.search(query="João", user_id=team_user_id, limit=5)
    
    if search_results:
        print(f"Encontrados {len(search_results)} resultados:")
        for i, result in enumerate(search_results, 1):
            print(f"\nResultado {i}:")
            print(f"Texto: {result.get('text', 'N/A')}")
            print(f"Score: {result.get('score', 'N/A')}")
    else:
        print("Nenhum resultado encontrado na busca.")
        
except Exception as e:
    print(f"Erro ao acessar Mem0: {e}")