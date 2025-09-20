"""
Cliente para Google AI API (Gemini) usando API Key
Suporte ao modelo Gemini 2.5 Flash
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VertexAIClient:
    """Cliente para interagir com Google AI API (Gemini) usando API Key"""
    
    def __init__(self, api_key: str, project_id: str = None, location: str = None):
        """
        Inicializa o cliente Google AI API.
        
        Args:
            api_key: Chave da API do Google AI
            project_id: Não usado na Google AI API (mantido para compatibilidade)
            location: Não usado na Google AI API (mantido para compatibilidade)
        """
        self.api_key = api_key
        self.default_model = "gemini-2.5-flash"
        
        # URL base da Google AI API
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        print(f"Cliente Google AI inicializado - Modelo padrão: {self.default_model}")
    
    def generate_content(self, 
                        messages: List[Dict[str, str]], 
                        model: str = None, 
                        temperature: float = 0.7, 
                        max_tokens: int = None,
                        system_instruction: str = None) -> Dict[str, Any]:
        """
        Gera conteúdo usando o modelo Gemini via Vertex AI.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "texto"}]
            model: Nome do modelo (padrão: gemini-2.5-flash)
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens na resposta
            system_instruction: Instrução do sistema
            
        Returns:
            Dict com a resposta do modelo e metadados
        """
        try:
            if not model:
                model = self.default_model
            
            # Converter mensagens para o formato da Google AI API
            contents = []
            for msg in messages:
                if msg["role"] == "user":
                    contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
                elif msg["role"] == "assistant":
                    contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
            
            # Preparar o payload da requisição
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "candidateCount": 1,
                }
            }
            
            if max_tokens:
                payload["generationConfig"]["maxOutputTokens"] = max_tokens
            
            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }
            
            # Headers da requisição
            headers = {
                "Content-Type": "application/json",
            }
            
            # URL da Google AI API para o modelo específico
            url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"
            
            # Fazer a requisição HTTP
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Extrair texto da resposta
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    response_text = candidate["content"]["parts"][0].get("text", "")
                else:
                    response_text = "Erro: Formato de resposta inesperado"
            else:
                response_text = "Erro: Nenhum candidato na resposta"
            
            # Extrair informações de uso (tokens)
            usage_metadata = response_data.get("usageMetadata", {})
            usage_info = {
                "input_tokens": usage_metadata.get("promptTokenCount", 0),
                "output_tokens": usage_metadata.get("candidatesTokenCount", 0),
                "model": model
            }
            
            return {
                "text": response_text,
                "usage": usage_info,
                "raw_response": response_data
            }
            
        except Exception as e:
            logger.error(f"Erro na geração de conteúdo: {e}")
            raise Exception(f"Erro na geração de conteúdo: {e}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa a conexão com Vertex AI
        
        Returns:
            Dict com resultado do teste
        """
        try:
            test_messages = [
                {"role": "user", "content": "Diga apenas 'Olá' para testar a conexão."}
            ]
            
            result = self.generate_content(test_messages, temperature=0.1)
            
            return {
                "success": True,
                "model": result.get("usage", {}).get("model", self.default_model),
                "response": result.get("text", ""),
                "usage": result.get("usage", {}),
                "endpoint": f"Vertex AI - {self.location}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "endpoint": f"Vertex AI - {self.location}"
            }

def get_vertex_ai_client(api_key: str) -> VertexAIClient:
    """Retorna uma nova instância do cliente Google AI"""
    return VertexAIClient(api_key=api_key)