#!/usr/bin/env python3
"""
Script para testar a memória do agente entre mensagens.
Envia mensagens sequenciais para verificar se o agente lembra do contexto.
"""

import requests
import json
import time
import uuid

# Configurações
API_BASE = "http://localhost:80"
API_KEY = "151fb361-f295-4a4f-84c9-ec1f42599a67"
AGENT_ID = "08884777-c656-423a-9afb-ddb5c706a4cc"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# ID de usuário fixo para manter a memória
user_id = "test_memory_user_456"
session_id = str(uuid.uuid4())

def enviar_mensagem(mensagem, debounce=5000):
    """Envia uma mensagem para a API"""
    payload = {
        "mensagem": mensagem,
        "agent_id": AGENT_ID,
        "debounce": debounce,
        "session_id": session_id,
        "message_id": str(uuid.uuid4()),
        "cliente_id": "",
        "user_id": user_id,
        "id_conta": str(uuid.uuid4())
    }
    
    print(f"📤 Enviando: {mensagem}")
    response = requests.post(f"{API_BASE}/v1/messages", headers=headers, json=payload)
    print(f"✅ Status: {response.status_code}")
    return response

def main():
    print("🧠 Testando Memória do Agente")
    print("=" * 50)
    
    # Primeira mensagem - estabelecer contexto
    print("\n1️⃣ Primeira mensagem - estabelecendo contexto:")
    enviar_mensagem("Meu nome é João e eu tenho 30 anos. Lembre-se disso!")
    
    # Aguardar processamento
    print("⏳ Aguardando 8 segundos para processamento...")
    time.sleep(8)
    
    # Segunda mensagem - testar memória
    print("\n2️⃣ Segunda mensagem - testando memória:")
    enviar_mensagem("Qual é o meu nome e idade?")
    
    # Aguardar processamento
    print("⏳ Aguardando 8 segundos para processamento...")
    time.sleep(8)
    
    # Terceira mensagem - adicionar mais contexto
    print("\n3️⃣ Terceira mensagem - adicionando mais contexto:")
    enviar_mensagem("Eu trabalho como desenvolvedor Python. Adicione isso ao que você sabe sobre mim.")
    
    # Aguardar processamento
    print("⏳ Aguardando 8 segundos para processamento...")
    time.sleep(8)
    
    # Quarta mensagem - testar memória completa
    print("\n4️⃣ Quarta mensagem - testando memória completa:")
    enviar_mensagem("Me conte tudo que você sabe sobre mim.")
    
    print("\n✅ Teste de memória concluído!")
    print("🔍 Verifique os logs do webhook para ver as respostas do agente.")
    print(f"👤 User ID usado: {user_id}")
    print(f"🔗 Session ID usado: {session_id}")

if __name__ == "__main__":
    main()