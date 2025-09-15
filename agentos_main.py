#!/usr/bin/env python3
"""
AgentOS - Sistema de Agentes Inteligentes
Sistema modular com agentes, memória persistente e API REST
"""

import logging
import uvicorn
from config import Config
from api import create_api_app
from agents import get_all_agents

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal do sistema AgentOS"""
    try:
        # Valida configurações
        logger.info("Validando configurações...")
        Config.validate_keys()
        
        # Carrega agentes
        logger.info("Carregando agentes...")
        agents = get_all_agents()
        logger.info(f"Agentes carregados: {[agent.config.name for agent in agents]}")
        
        # Cria aplicação FastAPI
        logger.info("Inicializando API...")
        app = create_api_app()
        
        # Configurações do servidor
        server_config = Config.get_server_config()
        
        logger.info(f"🚀 Iniciando AgentOS em http://{server_config['host']}:{server_config['port']}")
        logger.info(f"📚 Documentação disponível em http://{server_config['host']}:{server_config['port']}/docs")
        
        # Inicia o servidor
        uvicorn.run(
            app,
            host=server_config['host'],
            port=server_config['port']
        )
        
    except Exception as e:
        logger.error(f"Erro ao iniciar o sistema: {e}")
        raise

if __name__ == "__main__":
    main()