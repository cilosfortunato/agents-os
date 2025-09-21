#!/usr/bin/env python3
"""
Script para testar o fluxo completo de memórias:
1. Fazer várias interações de chat
2. Verificar se as memórias são salvas
3. Testar se as memórias são recuperadas corretamente
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_interaction(user_id: str, agent_id: str, session_id: str, message: str, message_id: str):
    """Testa uma interação de chat"""
    url = f"{BASE_URL}/v1/chat"
    payload = [{
        "mensagem": message,
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": agent_id,
        "message_id": message_id,
        "id_conta": "test-account-001"
    }]
    
    print(f"🗣️ Enviando: '{message}'")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Resposta: {data['messages'][0][:100]}...")
        return True
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
        return False

def check_memories(user_id: str):
    """Verifica as memórias salvas para um usuário específico"""
    url = f"{BASE_URL}/v1/memory/list/{user_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        memories = data.get('memories', [])
        print(f"📚 Total de memórias: {len(memories)}")
        for i, memory in enumerate(memories[:3]):  # Mostra apenas as 3 primeiras
            print(f"  {i+1}. {memory.get('text', memory.get('content', 'N/A'))[:80]}...")
        return len(memories)
    else:
        print(f"❌ Erro ao buscar memórias: {response.status_code} - {response.text}")
        return 0

def main():
    print("🧪 Testando fluxo completo de memórias...")
    
    # Configurações do teste
    user_id = "test-memory-user-456"
    agent_id = "test-agent-789"
    session_id = "test-memory-session-789"
    
    # Verificar memórias iniciais
    print("\n📊 Estado inicial das memórias:")
    initial_count = check_memories(user_id)
    
    # Fazer várias interações
    interactions = [
        ("Olá, preciso de informações sobre consultas", "msg-001"),
        ("Qual o valor de uma consulta nutricional?", "msg-002"),
        ("Vocês atendem aos sábados?", "msg-003"),
        ("Gostaria de agendar uma consulta", "msg-004")
    ]
    
    print("\n🗣️ Fazendo interações de teste...")
    successful_interactions = 0
    
    for message, msg_id in interactions:
        if test_chat_interaction(user_id, agent_id, session_id, message, msg_id):
            successful_interactions += 1
        time.sleep(1)  # Pequena pausa entre interações
    
    print(f"\n✅ {successful_interactions}/{len(interactions)} interações bem-sucedidas")
    
    # Verificar memórias após as interações
    print("\n📊 Estado final das memórias:")
    final_count = check_memories(user_id)
    
    # Análise dos resultados
    print(f"\n📈 Análise:")
    print(f"  • Memórias iniciais: {initial_count}")
    print(f"  • Memórias finais: {final_count}")
    print(f"  • Novas memórias criadas: {final_count - initial_count}")
    print(f"  • Interações realizadas: {successful_interactions}")
    
    if final_count > initial_count:
        print("🎉 Sistema de memórias funcionando corretamente!")
    else:
        print("⚠️ Possível problema no salvamento de memórias")

if __name__ == "__main__":
    main()