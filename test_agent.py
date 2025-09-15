from agno import Agent
from agents import create_assistente_principal

agent = create_assistente_principal()
print("Atributos do agent:")
print(dir(agent))
print("\nName:", getattr(agent, 'name', 'NOT FOUND'))
print("Config:", hasattr(agent, 'config'))
if hasattr(agent, 'config'):
    print("Config dir:", dir(agent.config))
    print("Config name:", getattr(agent.config, 'name', 'NOT FOUND'))