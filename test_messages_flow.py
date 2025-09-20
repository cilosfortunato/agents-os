import os
import json
import uuid
import time
from typing import Any, Dict, List

import requests

BASE = os.environ.get("BASE_URL", "http://localhost:8002")
HEADERS = {
    "X-API-Key": "151fb361-f295-4a4f-84c9-ec1f42599a67",
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def pp(title: str, data: Any):
    print(f"\n== {title} ==")
    if isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)


def get_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return {"raw": resp.text}


def ensure_server():
    url = f"{BASE}/v1/health"
    r = requests.get(url, headers=HEADERS, timeout=15)
    pp("HEALTH", {"status": r.status_code, "body": get_json(r)})
    r.raise_for_status()


def list_agents() -> List[Dict[str, Any]]:
    url = f"{BASE}/v1/agents"
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = get_json(r)
    agents = data.get("agents") if isinstance(data, dict) else None
    if agents is None:
        # fallback: maybe API returns a list directly
        agents = data if isinstance(data, list) else []
    pp("AGENTS", agents)
    return agents


def create_agent_if_needed() -> str:
    agents = list_agents()
    if agents:
        return agents[0]["id"]
    # create one
    url = f"{BASE}/v1/agents"
    payload = {
        "name": "Agente Teste API",
        "role": "Atendimento",
        "instructions": [
            "Seja gentil e objetivo.",
            "Responda com base no conhecimento vinculado quando disponível."
        ],
        "model": "gemini-2.5-flash",
        "provider": "gemini",
        "account_id": None
    }
    r = requests.post(url, headers=HEADERS, data=json.dumps(payload), timeout=25)
    pp("CREATE_AGENT_RESP", {"status": r.status_code, "body": get_json(r)})
    r.raise_for_status()
    body = get_json(r)
    # body may be {"agent": {..}} or direct AgentResponse
    agent = body.get("agent") if isinstance(body, dict) else None
    if agent is None:
        agent = body
    return agent["id"]


def post_messages(agent_id: str):
    url = f"{BASE}/v1/messages"
    session_id = str(uuid.uuid4())
    payload = [
        {
            "mensagem": "Qual horário funciona?",
            "agent_id": agent_id,
            "debounce": 15000,
            "session_id": session_id,
            "message_id": str(uuid.uuid4()),
            "cliente_id": "",
            "user_id": "116883357474955@lid",
            "id_conta": "f7dae33c-6364-4d88-908f-f5f64426a5c9"
        }
    ]
    r = requests.post(url, headers=HEADERS, data=json.dumps(payload), timeout=45)
    body = get_json(r)
    pp("POST_MESSAGES_STATUS", r.status_code)
    pp("POST_MESSAGES_BODY", body)
    try:
        agent_usage = body.get("agent_usage") if isinstance(body, dict) else None
        pp("AGENT_USAGE", agent_usage)
    except Exception:
        pass


def main():
    ensure_server()
    agent_id = create_agent_if_needed()
    print(f"\nagent_id selecionado: {agent_id}")
    post_messages(agent_id)


if __name__ == "__main__":
    main()