import os
import requests
import json
from typing import Dict, Any, Optional

class SimpleOpenAIClient:
    """Cliente simples para API da OpenAI usando requests"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: list, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
        """Faz uma requisição de chat completion para a API da OpenAI"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"Erro na API OpenAI: {response.status_code} - {response.text}")
                return f"Erro na API: {response.status_code}"
                
        except Exception as e:
            print(f"Erro ao chamar OpenAI API: {e}")
            return f"Erro interno: {str(e)}"
    
    def generate_response(self, prompt: str, system_message: str = None) -> str:
        """Gera uma resposta baseada no prompt fornecido"""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(messages)