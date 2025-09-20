"""
Cliente para Google Vertex AI usando a nova API google-genai
Suporte ao modelo Gemini 2.5 Flash com thinking_config
"""

import os
import logging
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VertexAIClientNew:
    """Cliente para interagir com Google Vertex AI usando a nova API google-genai"""
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o cliente Google Vertex AI.
        
        Args:
            api_key: Chave da API do Google Cloud (GOOGLE_CLOUD_API_KEY)
        """
        self.api_key = api_key or os.environ.get("GOOGLE_CLOUD_API_KEY")
        self.default_model = "gemini-2.5-flash"
        
        if not self.api_key:
            raise ValueError("API Key é obrigatória. Defina GOOGLE_CLOUD_API_KEY ou passe api_key.")
        
        # Inicializar cliente
        self.client = genai.Client(
            vertexai=True,
            api_key=self.api_key
        )
        
        logger.info(f"Cliente Google Vertex AI inicializado - Modelo padrão: {self.default_model}")
    
    def generate_content(self, 
                        messages: List[Dict[str, str]] = None,
                        prompt: str = None,
                        model: str = None, 
                        temperature: float = 0.7, 
                        max_tokens: int = 1000,
                        system_instruction: str = None) -> Dict[str, Any]:
        """
        Gera conteúdo usando o modelo Gemini.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "texto"}]
            prompt: Prompt direto (alternativa a messages)
            model: Modelo a usar (padrão: gemini-2.5-flash)
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta
            system_instruction: Instrução do sistema
            
        Returns:
            Dict com 'text' e 'usage'
        """
        try:
            model_name = model or self.default_model
            
            # Preparar conteúdo
            if messages:
                # Converter mensagens para o formato da nova API
                contents = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=content)]
                    ))
            elif prompt:
                # Usar prompt direto
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ]
            else:
                raise ValueError("É necessário fornecer 'messages' ou 'prompt'")
            
            # Configurar geração
            config = types.GenerateContentConfig(
                temperature=temperature,
                top_p=1,
                max_output_tokens=min(max_tokens, 65535),
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="OFF"
                    )
                ],
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                )
            )
            
            # Adicionar system_instruction se fornecido
            if system_instruction:
                config.system_instruction = [types.Part.from_text(text=system_instruction)]
            
            # Gerar conteúdo
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            
            # Extrair texto da resposta
            response_text = ""
            if hasattr(response, 'text') and response.text:
                # Resposta direta com atributo text
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                # Resposta com candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text
                    elif hasattr(candidate.content, 'text') and candidate.content.text:
                        response_text = candidate.content.text
                elif hasattr(candidate, 'text') and candidate.text:
                    response_text = candidate.text
            
            # Debug: log da estrutura da resposta se não conseguir extrair texto
            if not response_text:
                logger.warning(f"Não foi possível extrair texto da resposta. Estrutura: {type(response)}")
                if hasattr(response, '__dict__'):
                    logger.warning(f"Atributos da resposta: {list(response.__dict__.keys())}")
                # Tentar converter para string como fallback
                response_text = str(response) if response else "Resposta vazia"
            
            # Calcular usage (estimativa)
            input_tokens = sum(len(str(content).split()) for content in contents)
            output_tokens = len(response_text.split())
            
            return {
                "text": response_text,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "model": model_name
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo: {e}")
            return {
                "text": f"Erro ao gerar resposta: {str(e)[:100]}...",
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "model": model or self.default_model
                }
            }
    
    def generate_content_stream(self, 
                               messages: List[Dict[str, str]] = None,
                               prompt: str = None,
                               model: str = None, 
                               temperature: float = 0.7, 
                               max_tokens: int = 1000,
                               system_instruction: str = None):
        """
        Gera conteúdo em streaming usando o modelo Gemini.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "texto"}]
            prompt: Prompt direto (alternativa a messages)
            model: Modelo a usar (padrão: gemini-2.5-flash)
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Máximo de tokens na resposta
            system_instruction: Instrução do sistema
            
        Yields:
            Chunks de texto conforme são gerados
        """
        try:
            model_name = model or self.default_model
            
            # Preparar conteúdo
            if messages:
                contents = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=content)]
                    ))
            elif prompt:
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ]
            else:
                raise ValueError("É necessário fornecer 'messages' ou 'prompt'")
            
            # Configurar geração
            config = types.GenerateContentConfig(
                temperature=temperature,
                top_p=1,
                max_output_tokens=min(max_tokens, 65535),
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="OFF"
                    )
                ],
                thinking_config=types.ThinkingConfig(
                    thinking_budget=-1,
                )
            )
            
            # Adicionar system_instruction se fornecido
            if system_instruction:
                config.system_instruction = [types.Part.from_text(text=system_instruction)]
            
            # Gerar conteúdo em streaming
            for chunk in self.client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=config
            ):
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo em streaming: {e}")
            yield f"Erro: {str(e)}"
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Lista modelos disponíveis"""
        try:
            # A nova API não tem um método direto para listar modelos
            # Retornamos os modelos conhecidos
            return [
                {
                    "name": "gemini-2.5-flash",
                    "display_name": "Gemini 2.5 Flash",
                    "description": "Modelo rápido e eficiente para tarefas gerais"
                },
                {
                    "name": "gemini-1.5-pro",
                    "display_name": "Gemini 1.5 Pro",
                    "description": "Modelo avançado para tarefas complexas"
                }
            ]
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    def test_connection(self) -> Dict[str, Any]:
        """Testa a conexão com a API"""
        try:
            # Teste simples de geração
            result = self.generate_content(
                prompt="Teste de conexão",
                max_tokens=10
            )
            
            if result["text"] and "Erro" not in result["text"]:
                return {
                    "status": "success",
                    "message": "Conexão estabelecida com sucesso",
                    "model": self.default_model
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro na resposta: {result['text']}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro de conexão: {str(e)}"
            }

# Instância global
vertex_ai_client_new = None

def get_vertex_ai_client_new(api_key: str = None) -> VertexAIClientNew:
    """Função para obter instância singleton do cliente"""
    global vertex_ai_client_new
    
    if vertex_ai_client_new is None:
        vertex_ai_client_new = VertexAIClientNew(api_key=api_key)
    
    return vertex_ai_client_new