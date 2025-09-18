import requests
import json

# Configuração da API
API_BASE = "http://localhost:7777"
HEADERS = {"Content-Type": "application/json"}

def teste_memoria_completo():
    """Teste completo do sistema de memória com IDs corretos"""
    
    print("🧪 TESTE FINAL DE MEMÓRIA COM IDs CORRETOS")
    print("=" * 60)
    
    # 1. Criar agente
    print("\n1. Criando agente...")
    agent_data = {
        "name": "Assistente Memoria Final",
        "role": "Assistente Pessoal",
        "instructions": [
            "Você é um assistente pessoal que lembra de tudo sobre o usuário",
            "Sempre use informações pessoais quando relevante",
            "Seja amigável e personalizado"
        ],
        "user_id": "teste_final"
    }
    response = requests.post(f"{API_BASE}/agents", json=agent_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Erro ao criar agente: {response.text}")
        return
    
    agent_result = response.json()
    agent_name = agent_result['agent']['name']
    print(f"✅ Agente criado: {agent_name}")
    
    # 2. Criar time
    print("\n2. Criando time...")
    team_data = {
        "name": "Time Memoria Final",
        "description": "Time para teste final de memória",
        "agent_names": [agent_name],
        "user_id": "teste_final"
    }
    response = requests.post(f"{API_BASE}/teams", json=team_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Erro ao criar time: {response.text}")
        return
    
    team_result = response.json()
    print(f"✅ Time criado: {team_result['team']['name']}")
    
    # 3. Verificar se o time foi realmente criado (buscar na lista)
    print("\n3. Verificando times criados...")
    response = requests.get(f"{API_BASE}/teams?user_id=teste_final", headers=HEADERS)
    if response.status_code == 200:
        teams_data = response.json()
        print(f"Times encontrados: {teams_data['total']}")
        
        if teams_data['total'] > 0:
            # Pega o ID do primeiro time (que acabamos de criar)
            team_id = teams_data['teams'][0]['id']
            team_name = teams_data['teams'][0]['name']
            print(f"✅ Time encontrado - ID: {team_id}, Nome: {team_name}")
            
            # 4. Testar conversas com memória
            print("\n4. Testando conversas com memória...")
            
            conversas = [
                "Oi! Meu nome é Ana e sou médica pediatra. Tenho 35 anos e moro em São Paulo.",
                "Você pode me recomendar um livro de ficção científica? Adoro esse gênero!",
                "Qual é minha profissão mesmo?",
                "Em que cidade eu moro?",
                "Como você me chamaria?"
            ]
            
            respostas = []
            
            for i, mensagem in enumerate(conversas, 1):
                print(f"\n4.{i}. Enviando: {mensagem}")
                
                chat_data = {
                    "message": mensagem,
                    "user_id": "teste_final",
                    "team_id": team_id  # Usando o ID correto!
                }
                
                response = requests.post(f"{API_BASE}/teams/run", json=chat_data, headers=HEADERS)
                
                if response.status_code == 200:
                    result = response.json()
                    resposta = result.get('response', 'Sem resposta')
                    print(f"✅ Resposta: {resposta}")
                    respostas.append(resposta)
                else:
                    print(f"❌ Erro: {response.text}")
                    respostas.append(None)
            
            # 5. Análise dos resultados
            print("\n" + "=" * 60)
            print("📊 ANÁLISE DOS RESULTADOS")
            print("=" * 60)
            
            # Verificar se as informações pessoais foram lembradas
            score = 0
            total_checks = 4
            
            # Verificar menções nas respostas
            all_responses = " ".join([r for r in respostas if r])
            
            if "Ana" in all_responses:
                print("✅ Nome (Ana) foi lembrado")
                score += 1
            else:
                print("❌ Nome (Ana) NÃO foi lembrado")
            
            if any(word in all_responses.lower() for word in ["médica", "pediatra", "medicina"]):
                print("✅ Profissão (médica/pediatra) foi lembrada")
                score += 1
            else:
                print("❌ Profissão (médica/pediatra) NÃO foi lembrada")
            
            if "São Paulo" in all_responses:
                print("✅ Cidade (São Paulo) foi lembrada")
                score += 1
            else:
                print("❌ Cidade (São Paulo) NÃO foi lembrada")
            
            if any(word in all_responses.lower() for word in ["ficção", "científica"]):
                print("✅ Interesse (ficção científica) foi lembrado")
                score += 1
            else:
                print("❌ Interesse (ficção científica) NÃO foi lembrado")
            
            # Resultado final
            percentage = (score / total_checks) * 100
            print(f"\n🎯 SCORE DE MEMÓRIA: {score}/{total_checks} ({percentage:.0f}%)")
            
            if percentage >= 75:
                print("🎉 EXCELENTE! O sistema de memória está funcionando muito bem!")
            elif percentage >= 50:
                print("👍 BOM! O sistema de memória está funcionando parcialmente.")
            elif percentage >= 25:
                print("⚠️ REGULAR! O sistema de memória precisa de melhorias.")
            else:
                print("❌ RUIM! O sistema de memória não está funcionando adequadamente.")
            
            # 6. Verificar memórias salvas
            print("\n6. Verificando memórias salvas...")
            response = requests.get(f"{API_BASE}/memory/all?user_id=teste_final", headers=HEADERS)
            if response.status_code == 200:
                memory_data = response.json()
                print(f"Total de memórias salvas: {memory_data['total']}")
                if memory_data['total'] > 0:
                    print("Memórias encontradas:")
                    for memory in memory_data['memories'][:3]:  # Mostra apenas as 3 primeiras
                        print(f"- {memory.get('memory', 'N/A')}")
            else:
                print(f"❌ Erro ao buscar memórias: {response.text}")
                
        else:
            print("❌ Nenhum time foi encontrado após a criação")
    else:
        print(f"❌ Erro ao listar times: {response.text}")

if __name__ == "__main__":
    teste_memoria_completo()