"""
Cliente para Google AI API (Gemini) com suporte a API Key e Service Account
Suporte ao modelo Gemini 2.5 Flash
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import google.generativeai as genai

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VertexAIClientReal:
    """Cliente para interagir com Google AI API (Gemini) usando API Key ou Service Account"""
    
    def __init__(self, api_key: str = None, credentials_path: str = None, project_id: str = None, location: str = None):
        """
        Inicializa o cliente Google AI API.
        
        Args:
            api_key: Chave da API do Google AI (opcional se usar Service Account)
            credentials_path: Caminho para o arquivo de credenciais do Service Account
            project_id: ID do projeto Google Cloud
            location: Localização (não usado na Google AI API)
        """
        self.project_id = project_id
        self.default_model = "gemini-2.5-flash"
        self.credentials = None
        
        # Configurar autenticação
        if api_key:
            # Usar API Key
            self.api_key = api_key
            genai.configure(api_key=api_key)
            self.auth_method = "api_key"
            print(f"Cliente Google AI inicializado com API Key - Modelo padrão: {self.default_model}")
            
        elif credentials_path and os.path.exists(credentials_path):
            # Usar Service Account
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            self.project_id = self.credentials.project_id
            
            # Obter token de acesso
            request = Request()
            self.credentials.refresh(request)
            
            # Configurar genai com token
            genai.configure(api_key=self.credentials.token)
            self.auth_method = "service_account"
            print(f"Cliente Google AI inicializado com Service Account - Projeto: {self.project_id}")
            
        elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            # Usar credenciais do ambiente
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            self.project_id = self.credentials.project_id
            
            # Obter token de acesso
            request = Request()
            self.credentials.refresh(request)
            
            # Configurar genai com token
            genai.configure(api_key=self.credentials.token)
            self.auth_method = "service_account_env"
            print(f"Cliente Google AI inicializado com Service Account (env) - Projeto: {self.project_id}")
            
        else:
            raise ValueError("É necessário fornecer api_key ou credentials_path, ou definir GOOGLE_APPLICATION_CREDENTIALS")
    
    def _refresh_token_if_needed(self):
        """Atualiza o token se estiver usando Service Account"""
        if self.credentials and hasattr(self.credentials, 'expired') and self.credentials.expired:
            request = Request()
            self.credentials.refresh(request)
            genai.configure(api_key=self.credentials.token)
            print("Token do Service Account atualizado")
    
    def generate_content(self, 
                        messages: List[Dict[str, str]] = None,
                        prompt: str = None,
                        model: str = None, 
                        temperature: float = 0.7, 
                        max_tokens: int = None,
                        system_instruction: str = None) -> Dict[str, Any]:
        """
        Gera conteúdo usando o modelo Gemini.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "texto"}]
            prompt: Prompt direto (alternativa a messages)
            model: Nome do modelo (padrão: gemini-2.5-flash)
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens na resposta
            system_instruction: Instrução do sistema
            
        Returns:
            Dict com a resposta do modelo
        """
        try:
            # Atualizar token se necessário
            self._refresh_token_if_needed()
            
            # Preparar o prompt
            if messages:
                # Extrair texto das mensagens
                text_parts = []
                for msg in messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'system':
                        system_instruction = content
                    else:
                        text_parts.append(content)
                prompt_text = '\n'.join(text_parts)
            else:
                prompt_text = prompt or "Olá"
            
            # Configurar o modelo
            model_name = model or self.default_model
            if model_name.startswith('gemini-'):
                model_name = model_name
            else:
                model_name = f"gemini-{model_name}"
            
            # Configurar parâmetros de geração
            generation_config = {
                'temperature': temperature,
                'max_output_tokens': max_tokens or 1000,
            }
            
            # Criar o modelo
            if system_instruction:
                genai_model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
            else:
                genai_model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config
                )
            
            # Gerar conteúdo
            response = genai_model.generate_content(prompt_text)
            
            # Formatar resposta
            result = {
                'candidates': [
                    {
                        'content': {
                            'parts': [{'text': response.text}]
                        },
                        'finishReason': 'STOP'
                    }
                ],
                'usageMetadata': {
                    'promptTokenCount': len(prompt_text.split()) * 1.3,  # Estimativa
                    'candidatesTokenCount': len(response.text.split()) * 1.3,  # Estimativa
                    'totalTokenCount': (len(prompt_text.split()) + len(response.text.split())) * 1.3
                },
                'modelVersion': model_name
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo: {e}")
            # Retornar resposta de erro compatível
            return {
                'candidates': [
                    {
                        'content': {
                            'parts': [{'text': f"Erro ao gerar resposta: {str(e)}"}]
                        },
                        'finishReason': 'ERROR'
                    }
                ],
                'usageMetadata': {
                    'promptTokenCount': 0,
                    'candidatesTokenCount': 0,
                    'totalTokenCount': 0
                },
                'modelVersion': model or self.default_model
            }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Lista os modelos disponíveis"""
        try:
            self._refresh_token_if_needed()
            
            models = []
            for model in genai.list_models():
                models.append({
                    'name': model.name,
                    'displayName': model.display_name,
                    'description': getattr(model, 'description', ''),
                    'inputTokenLimit': getattr(model, 'input_token_limit', 0),
                    'outputTokenLimit': getattr(model, 'output_token_limit', 0)
                })
            
            return models
            
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    def test_connection(self) -> Dict[str, Any]:
        """Testa a conexão com a API"""
        try:
            self._refresh_token_if_needed()
            
            # Teste simples de geração
            response = self.generate_content(prompt="Teste de conexão")
            
            return {
                'status': 'success',
                'message': 'Conexão estabelecida com sucesso',
                'auth_method': self.auth_method,
                'project_id': self.project_id,
                'response': response
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro na conexão: {str(e)}',
                'auth_method': getattr(self, 'auth_method', 'unknown'),
                'project_id': self.project_id
            }

# Instância global para compatibilidade
vertex_ai_client = None

def get_vertex_ai_client(api_key: str = None, credentials_path: str = None) -> VertexAIClientReal:
    """
    Retorna uma instância do cliente Vertex AI.
    
    Args:
        api_key: Chave da API (opcional)
        credentials_path: Caminho para credenciais (opcional)
    """
    global vertex_ai_client
    
    if vertex_ai_client is None:
        vertex_ai_client = VertexAIClientReal(
            api_key=api_key,
            credentials_path=credentials_path
        )
    
    return vertex_ai_client