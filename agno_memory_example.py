"""
Exemplo de configuração do MemoryManager do Agno com instruções personalizadas
para captura seletiva de memórias seguindo o padrão de síntese concisa.
"""

import os
from agno.db.postgres import PostgresDb
from agno.memory import MemoryManager
from agno.models.openai import OpenAIChat
from agno.models.message import Message
from rich.pretty import pprint

# Configuração do banco de dados (ajuste conforme sua configuração)
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
memory_db = PostgresDb(db_url=db_url)

# Instruções personalizadas para captura de memória seguindo o padrão especificado
MEMORY_CAPTURE_INSTRUCTIONS = """
Resuma cada interação usuário-agente em um único registro objetivo, extraindo o interesse principal do usuário e a informação central fornecida pelo agente.

Não armazene todo o histórico de mensagens nem dados irrelevantes. A memória enriquecida deve conter apenas:

1. O que o usuário demonstrou interesse de forma explícita (ex: produto, serviço, dúvida concreta)
2. O que o agente respondeu de importante, especialmente valores, condições, disponibilidade, prazos ou recomendações.

Siga a estrutura:
"Usuário demonstrou interesse em [assunto ou produto] e quis saber [detalhe/specificidade]. Informado pelo agente que [resumo da resposta principal, incluindo valores, condições etc.]."

Exemplos:
- Se o usuário perguntar: "Vocês têm botox? Qual o preço?"
  E o agente responder: "Sim, temos, o valor é 1500 reais por 1ml."
  Então, salve na memória: "Usuário demonstrou interesse em botox e quis saber o preço. Agente informou que o valor é 1500 reais por 1ml."

Adote frases claras, sem citar nomes próprios nem mensagens literais, e prefira sempre o resumo do sentido principal da troca para facilitar buscas e personalização futuras.

Ignore:
- Cumprimentos e saudações
- Mensagens muito curtas ou sem conteúdo substantivo
- Conversas casuais sem interesse comercial ou informativo específico
- Nomes próprios e dados pessoais irrelevantes
"""

# Configuração do MemoryManager com instruções personalizadas
memory_manager = MemoryManager(
    model=OpenAIChat(id="gpt-4o"),
    memory_capture_instructions=MEMORY_CAPTURE_INSTRUCTIONS,
    db=memory_db,
)

def exemplo_captura_memoria_texto():
    """Exemplo de captura de memória a partir de texto simples"""
    
    user_id = "cliente_exemplo@email.com"
    
    # Exemplo 1: Interesse em horários
    texto_interacao = """
    Usuário: Qual horário vocês funcionam?
    Agente: Funcionamos de segunda a sexta-feira, das 8h às 18h, com pausa para almoço das 12h às 13h.
    """
    
    print("=== Exemplo 1: Captura de memória sobre horários ===")
    memory_manager.create_user_memories(
        message=texto_interacao,
        user_id=user_id,
    )
    
    # Exemplo 2: Interesse em preços
    texto_interacao_2 = """
    Usuário: Vocês têm botox? Qual o preço?
    Agente: Sim, temos botox disponível. O valor é 1500 reais por 1ml.
    """
    
    print("=== Exemplo 2: Captura de memória sobre preços ===")
    memory_manager.create_user_memories(
        message=texto_interacao_2,
        user_id=user_id,
    )

def exemplo_captura_memoria_mensagens():
    """Exemplo de captura de memória a partir de lista de mensagens"""
    
    user_id = "cliente_exemplo_2@email.com"
    
    # Conversa sobre agendamento
    mensagens = [
        Message(role="user", content="Oi, gostaria de agendar uma consulta"),
        Message(role="assistant", content="Olá! Claro, posso ajudar com o agendamento."),
        Message(role="user", content="Que horários vocês têm disponíveis?"),
        Message(role="assistant", content="Temos horários disponíveis na terça-feira às 14h e na quinta-feira às 10h."),
        Message(role="user", content="Perfeito, quero a terça às 14h"),
        Message(role="assistant", content="Agendamento confirmado para terça-feira às 14h. Enviaremos uma confirmação por WhatsApp."),
    ]
    
    print("=== Exemplo 3: Captura de memória de conversa sobre agendamento ===")
    memory_manager.create_user_memories(
        messages=mensagens,
        user_id=user_id,
    )

def buscar_memorias_usuario(user_id: str):
    """Busca e exibe as memórias de um usuário"""
    
    print(f"\n=== Memórias do usuário {user_id} ===")
    memories = memory_manager.get_user_memories(user_id=user_id)
    pprint(memories)

def exemplo_busca_contextual(user_id: str, query: str):
    """Exemplo de busca contextual de memórias"""
    
    print(f"\n=== Busca contextual: '{query}' ===")
    # Nota: Este método pode variar dependendo da versão do Agno
    # Consulte a documentação oficial para o método correto de busca
    try:
        results = memory_manager.search_memories(query=query, user_id=user_id)
        pprint(results)
    except AttributeError:
        print("Método de busca não disponível nesta versão. Use get_user_memories() para ver todas as memórias.")

if __name__ == "__main__":
    print("🧠 Exemplo de MemoryManager do Agno com Instruções Personalizadas")
    print("=" * 70)
    
    # Executar exemplos
    exemplo_captura_memoria_texto()
    exemplo_captura_memoria_mensagens()
    
    # Buscar memórias criadas
    buscar_memorias_usuario("cliente_exemplo@email.com")
    buscar_memorias_usuario("cliente_exemplo_2@email.com")
    
    # Exemplo de busca contextual
    exemplo_busca_contextual("cliente_exemplo@email.com", "horário funcionamento")
    
    print("\n✅ Exemplos concluídos!")