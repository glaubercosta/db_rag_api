"""
Ollama LLM Provider implementation for local models
"""
import requests
import json
from typing import List, Dict, Optional, Any
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

from . import (
    BaseLLMProvider, 
    BaseEmbeddingProvider, 
    LLMConfig, 
    EmbeddingConfig,
    LLMProviderError,
    LLMProviderAPIError,
    LLMProviderTimeoutError,
    LLMProviderNotAvailableError
)


class OllamaProvider(BaseLLMProvider):
    """Ollama local models provider"""
    
    def __init__(self, config):
        # Aceitar tanto LLMConfig quanto OllamaConfig
        if hasattr(config, 'base_url'):
            # OllamaConfig
            self.config = config
            self.base_url = config.base_url
            self.model = config.model_name  # Corrigido para model_name
        else:
            # LLMConfig
            super().__init__(config)
            self.base_url = config.api_base or "http://localhost:11434"
            self.model = config.model_name
        
        self.langchain_llm = None
        
    def initialize(self) -> None:
        """Initialize Ollama client"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise LLMProviderNotAvailableError(
                    f"Ollama server not accessible at {self.base_url}"
                )
            
            # Check if model exists
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if self.config.model_name not in model_names:
                available_models = ", ".join(model_names) if model_names else "None"
                raise LLMProviderNotAvailableError(
                    f"Model '{self.config.model_name}' not found in Ollama. "
                    f"Available models: {available_models}"
                )
            
            # Create LangChain Ollama instance
            self.langchain_llm = Ollama(
                model=self.config.model_name,
                base_url=self.base_url,
                temperature=self.config.temperature,
                timeout=self.config.timeout
            )
            
            self.client = True  # Mark as initialized
            
        except requests.exceptions.ConnectionError:
            raise LLMProviderNotAvailableError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running."
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize Ollama provider: {e}")
    
    def generate_text(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using Ollama API"""
        if not self.client:
            raise LLMProviderNotAvailableError("Ollama provider not initialized")
            
        try:
            # Prepare the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
            # Use requests directly for more control
            payload = {
                "model": self.config.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                }
            }
            
            if self.config.max_tokens:
                payload["options"]["num_predict"] = self.config.max_tokens
                
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                raise LLMProviderAPIError(f"Ollama API error: {response.text}")
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.Timeout:
            raise LLMProviderTimeoutError("Ollama request timeout")
        except requests.exceptions.RequestException as e:
            raise LLMProviderAPIError(f"Ollama request error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Ollama generation error: {e}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate chat completion using Ollama API"""
        if not self.client:
            raise LLMProviderNotAvailableError("Ollama provider not initialized")
            
        try:
            payload = {
                "model": self.config.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                }
            }
            
            if self.config.max_tokens:
                payload["options"]["num_predict"] = self.config.max_tokens
                
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                raise LLMProviderAPIError(f"Ollama API error: {response.text}")
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except requests.exceptions.Timeout:
            raise LLMProviderTimeoutError("Ollama request timeout")
        except requests.exceptions.RequestException as e:
            raise LLMProviderAPIError(f"Ollama request error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Ollama chat completion error: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200 and self.client is not None
        except:
            return False
    
    def get_langchain_llm(self):
        """Get LangChain compatible LLM instance"""
        if not self.langchain_llm:
            raise LLMProviderNotAvailableError("Ollama provider not initialized")
        return self.langchain_llm
    
    def list_available_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except:
            pass
        return []


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Ollama embeddings provider"""
    
    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.base_url = config.api_base or "http://localhost:11434"
        self.langchain_embeddings = None
        
    def initialize(self) -> None:
        """Initialize Ollama embeddings"""
        try:
            # Check if Ollama is running and model exists
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise LLMProviderNotAvailableError(
                    f"Ollama server not accessible at {self.base_url}"
                )
                
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            if self.config.model_name not in model_names:
                available_models = ", ".join(model_names) if model_names else "None"
                raise LLMProviderNotAvailableError(
                    f"Embedding model '{self.config.model_name}' not found in Ollama. "
                    f"Available models: {available_models}"
                )
            
            # Create LangChain OllamaEmbeddings instance
            self.langchain_embeddings = OllamaEmbeddings(
                model=self.config.model_name,
                base_url=self.base_url
            )
            
            self.client = True
            
        except requests.exceptions.ConnectionError:
            raise LLMProviderNotAvailableError(
                f"Cannot connect to Ollama at {self.base_url}"
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize Ollama embeddings: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents"""
        if not self.langchain_embeddings:
            raise LLMProviderNotAvailableError("Ollama embeddings not initialized")
            
        try:
            return self.langchain_embeddings.embed_documents(texts)
        except Exception as e:
            raise LLMProviderError(f"Ollama embedding error: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for query"""
        if not self.langchain_embeddings:
            raise LLMProviderNotAvailableError("Ollama embeddings not initialized")
            
        try:
            return self.langchain_embeddings.embed_query(text)
        except Exception as e:
            raise LLMProviderError(f"Ollama query embedding error: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama embeddings are available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200 and self.client is not None
        except:
            return False
    
    def get_langchain_embeddings(self):
        """Get LangChain compatible embeddings instance"""
        if not self.langchain_embeddings:
            raise LLMProviderNotAvailableError("Ollama embeddings not initialized")
        return self.langchain_embeddings
