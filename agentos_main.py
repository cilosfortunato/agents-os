#!/usr/bin/env python3
"""
AgentOS - Sistema de Agentes Inteligentes usando Agno
Sistema modular com agentes, memória persistente e API REST
"""

import uvicorn
from fastapi import FastAPI
from config import Config
from api import create_api_app
from agents import get_all_agents

def main():
    """Função principal do sistema AgentOS usando Agno"""
    # Valida configurações
    Config.validate_keys()
    
    # Carrega agentes
    agents = get_all_agents()
    print(f"Agentes carregados: {[agent.config.name for agent in agents]}")
    
    # Cria aplicação FastAPI
    app = create_api_app()
    
    # Inicia servidor
    print("🚀 Iniciando AgentOS em http://0.0.0.0:8000")
    print("📚 Documentação disponível em http://0.0.0.0:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()