#!/usr/bin/env python3
"""
Mock do VertexAIClient para demonstração do sistema
Este mock simula as respostas da API do Google AI para permitir testes completos
"""
import json
import time
import random
from typing import Dict, Any, List, Optional

class VertexAIClientMock:
    """Mock do cliente Vertex AI que simula respostas da API do Google AI"""
    
    def __init__(self, api_key: str = None):
        """Inicializa o mock do cliente"""
        self.api_key = api_key or "mock_api_key"
        self.model = "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Respostas pré-definidas para diferentes tipos de perguntas
        self.responses = {
            "saudacao": [
                "Olá! Como posso ajudá-lo hoje?",
                "Oi! Em que posso ser útil?",
                "Olá! Estou aqui para ajudar. O que você gostaria de saber?"
            ],
            "produto": [
                "Com base nas informações do manual do produto, posso ajudá-lo com questões técnicas.",
                "Consultando nossa base de conhecimento sobre o produto...",
                "Vou verificar as especificações do produto para você."
            ],
            "garantia": [
                "A garantia padrão do produto é de 12 meses e cobre defeitos de fabricação.",
                "Nossos produtos têm garantia de 12 meses contra defeitos de fábrica.",
                "A garantia é válida por 12 meses a partir da data de compra."
            ],
            "bateria": [
                "A bateria do dispositivo X dura 24 horas com uso moderado.",
                "Com uso normal, a bateria pode durar até 24 horas.",
                "A autonomia da bateria é de aproximadamente 24 horas."
            ],
            "modo_noturno": [
                "O modo noturno pode ser ativado no menu de configurações > tela.",
                "Para ativar o modo noturno, vá em configurações e depois em tela.",
                "Você encontra a opção de modo noturno nas configurações de tela."
            ],
            "reiniciar": [
                "Para reiniciar o dispositivo, pressione o botão de energia por 10 segundos.",
                "Mantenha o botão de energia pressionado por 10 segundos para reiniciar.",
                "O reset é feito pressionando o botão power por 10 segundos."
            ],
            "default": [
                "Entendo sua pergunta. Com base nas informações disponíveis, posso ajudá-lo.",
                "Vou processar sua solicitação e fornecer a melhor resposta possível.",
                "Analisando sua pergunta para fornecer uma resposta adequada."
            ]
        }
    
    def _detect_intent(self, prompt: str) -> str:
        """Detecta a intenção da pergunta para escolher uma resposta apropriada"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["olá", "oi", "hello", "bom dia", "boa tarde"]):
            return "saudacao"
        elif any(word in prompt_lower for word in ["garantia", "warranty"]):
            return "garantia"
        elif any(word in prompt_lower for word in ["bateria", "battery", "duração"]):
            return "bateria"
        elif any(word in prompt_lower for word in ["modo noturno", "dark mode", "escuro"]):
            return "modo_noturno"
        elif any(word in prompt_lower for word in ["reiniciar", "restart", "reset"]):
            return "reiniciar"
        elif any(word in prompt_lower for word in ["produto", "device", "aparelho"]):
            return "produto"
        else:
            return "default"
    
    def generate_content(self, messages=None, prompt=None, model=None, max_tokens=1000, temperature=0.7) -> Dict[str, Any]:
        """
        Simula a geração de conteúdo da API do Google AI
        
        Args:
            messages: Lista de mensagens (formato da API real)
            prompt: Prompt direto (compatibilidade)
            model: Modelo a usar (não usado no mock)
            max_tokens: Número máximo de tokens (não usado no mock)
            temperature: Temperatura para geração (não usado no mock)
            
        Returns:
            Dict com a resposta simulada
        """
        # Simula latência da API
        time.sleep(random.uniform(0.1, 0.3))
        
        # Extrai o texto do prompt
        if messages:
            # Se recebeu mensagens, extrai o conteúdo
            text_content = ""
            for msg in messages:
                text_content += msg.get("content", "")
        else:
            text_content = prompt or ""
        
        # Detecta intenção e escolhe resposta apropriada
        intent = self._detect_intent(text_content)
        responses = self.responses.get(intent, self.responses["default"])
        response_text = random.choice(responses)
        
        # Simula estatísticas de uso
        input_tokens = len(prompt.split()) * 1.3  # Aproximação
        output_tokens = len(response_text.split()) * 1.3
        
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": response_text
                            }
                        ]
                    },
                    "finishReason": "STOP",
                    "index": 0,
                    "safetyRatings": [
                        {
                            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            "probability": "NEGLIGIBLE"
                        },
                        {
                            "category": "HARM_CATEGORY_HATE_SPEECH",
                            "probability": "NEGLIGIBLE"
                        },
                        {
                            "category": "HARM_CATEGORY_HARASSMENT",
                            "probability": "NEGLIGIBLE"
                        },
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "probability": "NEGLIGIBLE"
                        }
                    ]
                }
            ],
            "usageMetadata": {
                "promptTokenCount": int(input_tokens),
                "candidatesTokenCount": int(output_tokens),
                "totalTokenCount": int(input_tokens + output_tokens)
            }
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Simula a listagem de modelos disponíveis"""
        return [
            {
                "name": "models/gemini-2.5-flash",
                "displayName": "Gemini 2.5 Flash",
                "description": "Fast and versatile performance across a diverse variety of tasks"
            },
            {
                "name": "models/gemini-2.5-pro",
                "displayName": "Gemini 2.5 Pro", 
                "description": "Complex reasoning tasks requiring more intelligence"
            }
        ]

# Instância global do mock (substitui a instância real)
_vertex_ai_client_mock = None

def get_vertex_ai_client(api_key: str) -> VertexAIClientMock:
    """
    Retorna uma instância do mock do VertexAIClient
    
    Args:
        api_key: Chave da API (não usada no mock)
        
    Returns:
        Instância do VertexAIClientMock
    """
    global _vertex_ai_client_mock
    if _vertex_ai_client_mock is None:
        _vertex_ai_client_mock = VertexAIClientMock(api_key)
    return _vertex_ai_client_mock