import requests
import json
import time

# Configuração da API
API_BASE = "http://localhost:7777"
HEADERS = {"Content-Type": "application/json"}

def criar_agente_memoria():
    """Cria um agente específico para teste de memória"""
    agent_data = {
        "name": "assistente_memoria",
        "role": "Assistente Pessoal com Memória",
        "description": "Assistente que deve lembrar de informações pessoais dos usuários",
        "instructions": [
            "Você é um assistente pessoal que SEMPRE deve usar as informações do contexto de conversas anteriores para personalizar suas respostas.",
            "Se você receber informações sobre o usuário no contexto, SEMPRE mencione essas informações em sua resposta para mostrar que você lembra.",
            "Por exemplo, se souber o nome do usuário, sempre o chame pelo nome.",
            "Seja caloroso e pessoal em suas respostas, demonstrando que você lembra das informações compartilhadas."
        ],
        "model": "google/gemini-2.0-flash-exp",
        "temperature": 0.1
    }
    
    response = requests.post(f"{API_BASE}/agents", json=agent_data, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        agent = result.get('agent', {})
        agent_name = agent.get('name', 'N/A')
        print(f"✅ Agente criado: {agent_name}")
        return agent_name  # Retorna o nome do agente em vez do ID
    else:
        print(f"❌ Erro ao criar agente: {response.text}")
        return None

def criar_time_memoria(agent_id):
    """Cria um time com o agente de memória"""
    team_data = {
        "name": "time_memoria_teste",
        "description": "Time para testar funcionalidade de memória",
        "agent_names": ["assistente_principal"]
    }
    
    response = requests.post(f"{API_BASE}/teams", json=team_data, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        team = result.get('team', {})
        team_name = team.get('name', 'N/A')
        team_id = team.get('id', 'N/A')
        print(f"✅ Time criado: {team_name} (ID: {team_id})")
        return team_id
    else:
        print(f"❌ Erro ao criar time: {response.text}")
        return None

def conversar_com_time(team_id, message, user_id="teste_memoria_detalhado"):
    """Envia mensagem para o time"""
    chat_data = {
        "message": message,
        "user_id": user_id,
        "team_id": team_id if team_id != "N/A" else "time_memoria_teste"
    }
    
    print(f"[DEBUG] Enviando para: {API_BASE}/teams/run")
    print(f"[DEBUG] Payload: {chat_data}")
    
    endpoint = f"{API_BASE}/teams/run"
    
    response = requests.post(endpoint, json=chat_data, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        return result.get('response', 'Sem resposta')
    else:
        print(f"❌ Erro na conversa: {response.text}")
        return None

def main():
    print("🧪 TESTE DETALHADO DE MEMÓRIA")
    print("=" * 50)
    
    # Usar agente padrão existente
    agent_name = "Assistente Principal"
    print(f"✅ Usando agente padrão: {agent_name}")
    
    # 2. Criar time
    team_id = criar_time_memoria(agent_name)
    if not team_id:
        return
    
    user_id = "teste_memoria_detalhado_user"
    
    print("\n📝 FASE 1: Estabelecendo informações pessoais")
    print("-" * 50)
    
    # 3. Primeira conversa - estabelecer informações
    mensagem1 = "Olá! Meu nome é Maria Silva e sou médica pediatra. Trabalho no Hospital São Lucas há 5 anos."
    resposta1 = conversar_com_time(team_id, mensagem1, user_id)
    print(f"👤 Usuário: {mensagem1}")
    print(f"🤖 Assistente: {resposta1}")
    
    time.sleep(2)
    
    # 4. Segunda conversa - mais informações
    mensagem2 = "Tenho 32 anos e moro em São Paulo. Gosto muito de ler livros de ficção científica nas horas vagas."
    resposta2 = conversar_com_time(team_id, mensagem2, user_id)
    print(f"\n👤 Usuário: {mensagem2}")
    print(f"🤖 Assistente: {resposta2}")
    
    time.sleep(2)
    
    print("\n🧠 FASE 2: Testando recuperação de memória")
    print("-" * 50)
    
    # 5. Terceira conversa - teste de memória
    mensagem3 = "Você pode me recomendar um livro?"
    resposta3 = conversar_com_time(team_id, mensagem3, user_id)
    print(f"👤 Usuário: {mensagem3}")
    print(f"🤖 Assistente: {resposta3}")
    
    time.sleep(2)
    
    # 6. Quarta conversa - teste específico
    mensagem4 = "Qual é minha profissão mesmo?"
    resposta4 = conversar_com_time(team_id, mensagem4, user_id)
    print(f"\n👤 Usuário: {mensagem4}")
    print(f"🤖 Assistente: {resposta4}")
    
    time.sleep(2)
    
    # 7. Quinta conversa - teste de nome
    mensagem5 = "Como você me chamaria?"
    resposta5 = conversar_com_time(team_id, mensagem5, user_id)
    print(f"\n👤 Usuário: {mensagem5}")
    print(f"🤖 Assistente: {resposta5}")
    
    print("\n📊 ANÁLISE DOS RESULTADOS")
    print("=" * 50)
    
    # Verificar se o assistente usou as informações
    nome_mencionado = any("Maria" in resp for resp in [resposta3, resposta4, resposta5] if resp)
    profissao_mencionada = any("médica" in resp.lower() or "pediatra" in resp.lower() for resp in [resposta3, resposta4, resposta5] if resp)
    cidade_mencionada = any("São Paulo" in resp for resp in [resposta3, resposta4, resposta5] if resp)
    hobby_mencionado = any("ficção científica" in resp.lower() for resp in [resposta3, resposta4, resposta5] if resp)
    
    print(f"✅ Nome (Maria) mencionado: {'SIM' if nome_mencionado else 'NÃO'}")
    print(f"✅ Profissão (médica/pediatra) mencionada: {'SIM' if profissao_mencionada else 'NÃO'}")
    print(f"✅ Cidade (São Paulo) mencionada: {'SIM' if cidade_mencionada else 'NÃO'}")
    print(f"✅ Hobby (ficção científica) mencionado: {'SIM' if hobby_mencionado else 'NÃO'}")
    
    score = sum([nome_mencionado, profissao_mencionada, cidade_mencionada, hobby_mencionado])
    print(f"\n🎯 SCORE DE MEMÓRIA: {score}/4 ({score*25}%)")
    
    if score >= 3:
        print("🎉 EXCELENTE! O sistema de memória está funcionando muito bem!")
    elif score >= 2:
        print("👍 BOM! O sistema de memória está funcionando parcialmente.")
    elif score >= 1:
        print("⚠️ REGULAR! O sistema de memória precisa de melhorias.")
    else:
        print("❌ RUIM! O sistema de memória não está funcionando adequadamente.")

if __name__ == "__main__":
    main()