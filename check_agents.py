from agents import get_all_agents

agents = get_all_agents()
print('Agentes disponíveis:')
for i, agent in enumerate(agents):
    print(f'Agente {i}:')
    print(f'  ID: {getattr(agent, "id", "SEM_ID")}')
    config = getattr(agent, 'config', {})
    print(f'  Config: {config}')
    if hasattr(agent, 'get_system_prompt'):
        try:
            prompt = agent.get_system_prompt()
            print(f'  System Prompt: {prompt[:100]}...')
        except:
            print(f'  System Prompt: Erro ao obter')
    print('---')