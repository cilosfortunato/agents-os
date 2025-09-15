import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configurações centralizadas do sistema AgentOS"""
    
    # Chaves de API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    MEM0_API_KEY = os.getenv("MEM0_API_KEY")
    ZEP_API_KEY = os.getenv("ZEP_API_KEY")
    
    # Configurações do servidor
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 7777))
    
    # Configurações dos modelos
    DEFAULT_MODEL_ID = "openai/gpt-4o-mini"
    DEFAULT_TEMPERATURE = 0.7
    
    # Configurações de memória
    MEMORY_COLLECTION = "agno_memories"
    
    # Configurações do Pinecone
    PINECONE_INDEX = "agno-knowledge-base"
    PINECONE_ENVIRONMENT = "gcp-starter"
    
    @classmethod
    def validate_keys(cls):
        """Valida se as chaves de API necessárias estão configuradas"""
        required_keys = {
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "MEM0_API_KEY": cls.MEM0_API_KEY
        }
        
        missing_keys = [key for key, value in required_keys.items() if not value]
        
        if missing_keys:
            raise ValueError(f"Chaves de API obrigatórias não encontradas: {', '.join(missing_keys)}")
        
        return True
    
    @classmethod
    def get_model_config(cls):
        """Retorna configuração padrão do modelo"""
        return {
            "model_id": cls.DEFAULT_MODEL_ID,
            "temperature": cls.DEFAULT_TEMPERATURE
        }
    
    @classmethod
    def get_server_config(cls):
        """Retorna configuração do servidor"""
        return {
            "host": cls.HOST,
            "port": cls.PORT
        }