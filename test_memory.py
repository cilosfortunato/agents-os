from memory import memory_manager

# Testa busca de memórias
memories = memory_manager.search_memories('user123', 'qual é o nome do usuário?')
print('Memórias encontradas:', len(memories))
for i, mem in enumerate(memories):
    print(f'{i+1}. {mem}')

# Testa busca por idade
memories_age = memory_manager.search_memories('user123', 'quantos anos tem?')
print('\nMemórias sobre idade:', len(memories_age))
for i, mem in enumerate(memories_age):
    print(f'{i+1}. {mem}')