"""
Custom LLM Provider for enterprise/custom API endpoints
"""
import requests
import json
from typing import List, Dict, Optional, Any
from langchain.llms.base import LLM
from langchain_core.embeddings import Embeddings

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


class CustomLLM(LLM):
    """LangChain-compatible wrapper for custom LLM APIs"""
    
    def __init__(self, provider: 'CustomProvider'):
        super().__init__()
        self.provider = provider
    
    @property
    def _llm_type(self) -> str:
        return "custom"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        return self.provider.generate_text(prompt, **kwargs)


class CustomEmbeddings(Embeddings):
    """LangChain-compatible wrapper for custom embedding APIs"""
    
    def __init__(self, provider: 'CustomEmbeddingProvider'):
        super().__init__()
        self.provider = provider
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.provider.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        return self.provider.embed_query(text)


class CustomProvider(BaseLLMProvider):
    """Custom/Enterprise LLM provider for proprietary APIs"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.headers = {
            "Content-Type": "application/json"
        }
        if config.custom_headers:
            self.headers.update(config.custom_headers)
        self.langchain_llm = None
        
    def initialize(self) -> None:
        """Initialize custom provider"""
        if not self.config.api_base:
            raise LLMProviderNotAvailableError(
                "API base URL is required for custom provider"
            )
            
        try:
            # Test connection to the API
            health_endpoint = f"{self.config.api_base}/health"
            test_response = requests.get(
                health_endpoint,
                headers=self.headers,
                timeout=5
            )
            
            # If health endpoint doesn't exist, try a minimal request
            if test_response.status_code == 404:
                self._test_minimal_request()
            elif test_response.status_code not in [200, 201]:
                print(f"Warning: Health check returned {test_response.status_code}")
            
            # Create LangChain wrapper
            self.langchain_llm = CustomLLM(self)
            self.client = True
            
        except requests.exceptions.ConnectionError:
            raise LLMProviderNotAvailableError(
                f"Cannot connect to custom API at {self.config.api_base}"
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize custom provider: {e}")
    
    def _test_minimal_request(self) -> None:
        """Test API with minimal request"""
        test_payload = {
            "model": self.config.model_name,
            "prompt": "Hello",
            "max_tokens": 5,
            "temperature": 0
        }
        
        # Try different common endpoints
        endpoints = ["/generate", "/completions", "/v1/completions", "/api/generate"]
        
        for endpoint in endpoints:
            try:
                response = requests.post(
                    f"{self.config.api_base}{endpoint}",
                    json=test_payload,
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    return
            except requests.exceptions.RequestException:
                continue
        
        # If no endpoint worked, we'll still proceed but with a warning
        print("Warning: Could not verify custom API endpoint. Proceeding anyway.")
    
    def generate_text(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using custom API"""
        if not self.client:
            raise LLMProviderNotAvailableError("Custom provider not initialized")
            
        # Build payload based on configuration
        payload = {
            "model": self.config.model_name,
            "temperature": self.config.temperature
        }
        
        # Handle different API formats
        if self.config.extra_params and self.config.extra_params.get("format") == "openai":
            # OpenAI-compatible format
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            payload["messages"] = messages
            endpoint = "/v1/chat/completions"
        else:
            # Simple prompt format (like Ollama)
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            payload["prompt"] = full_prompt
            endpoint = self.config.extra_params.get("endpoint", "/generate")
        
        if self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens
            
        # Add any extra parameters
        if self.config.extra_params:
            for key, value in self.config.extra_params.items():
                if key not in ["format", "endpoint"]:
                    payload[key] = value
        
        try:
            response = requests.post(
                f"{self.config.api_base}{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=self.config.timeout
            )
            
            if response.status_code not in [200, 201]:
                raise LLMProviderAPIError(
                    f"Custom API error ({response.status_code}): {response.text}"
                )
            
            result = response.json()
            
            # Handle different response formats
            if "choices" in result:  # OpenAI-like format
                return result["choices"][0]["message"]["content"]
            elif "response" in result:  # Ollama-like format
                return result["response"]
            elif "text" in result:  # Simple text format
                return result["text"]
            else:
                # Try to extract any string response
                for key in ["output", "completion", "generated_text", "content"]:
                    if key in result:
                        return str(result[key])
                
                raise LLMProviderError(f"Unknown response format: {result}")
            
        except requests.exceptions.Timeout:
            raise LLMProviderTimeoutError("Custom API request timeout")
        except requests.exceptions.RequestException as e:
            raise LLMProviderAPIError(f"Custom API request error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Custom API generation error: {e}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate chat completion using custom API"""
        # For custom APIs, we'll convert to a single prompt if needed
        if self.config.extra_params and self.config.extra_params.get("format") == "openai":
            # Use OpenAI-compatible chat endpoint
            payload = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": self.config.temperature
            }
            
            if self.config.max_tokens:
                payload["max_tokens"] = self.config.max_tokens
            
            endpoint = "/v1/chat/completions"
        else:
            # Convert messages to single prompt
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.title()}: {content}")
            
            full_prompt = "\n\n".join(prompt_parts)
            return self.generate_text(full_prompt, **kwargs)
        
        try:
            response = requests.post(
                f"{self.config.api_base}{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=self.config.timeout
            )
            
            if response.status_code not in [200, 201]:
                raise LLMProviderAPIError(
                    f"Custom API error ({response.status_code}): {response.text}"
                )
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            raise LLMProviderTimeoutError("Custom API request timeout")
        except requests.exceptions.RequestException as e:
            raise LLMProviderAPIError(f"Custom API request error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Custom API chat completion error: {e}")
    
    def is_available(self) -> bool:
        """Check if custom provider is available"""
        return self.client is not None and self.config.api_base is not None
    
    def get_langchain_llm(self):
        """Get LangChain compatible LLM instance"""
        if not self.langchain_llm:
            raise LLMProviderNotAvailableError("Custom provider not initialized")
        return self.langchain_llm


class CustomEmbeddingProvider(BaseEmbeddingProvider):
    """Custom embedding provider for enterprise APIs"""
    
    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.headers = {
            "Content-Type": "application/json"
        }
        if config.custom_headers:
            self.headers.update(config.custom_headers)
        self.langchain_embeddings = None
        
    def initialize(self) -> None:
        """Initialize custom embedding provider"""
        if not self.config.api_base:
            raise LLMProviderNotAvailableError(
                "API base URL is required for custom embedding provider"
            )
        
        # Create LangChain wrapper
        self.langchain_embeddings = CustomEmbeddings(self)
        self.client = True
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents"""
        if not self.client:
            raise LLMProviderNotAvailableError("Custom embedding provider not initialized")
        
        try:
            payload = {
                "model": self.config.model_name,
                "input": texts
            }
            
            # Add extra parameters if specified
            if self.config.extra_params:
                payload.update(self.config.extra_params)
            
            endpoint = "/v1/embeddings"  # Default to OpenAI-like endpoint
            if self.config.extra_params and "endpoint" in self.config.extra_params:
                endpoint = self.config.extra_params["endpoint"]
            
            response = requests.post(
                f"{self.config.api_base}{endpoint}",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code not in [200, 201]:
                raise LLMProviderAPIError(
                    f"Custom embedding API error ({response.status_code}): {response.text}"
                )
            
            result = response.json()
            
            # Handle different response formats
            if "data" in result:  # OpenAI-like format
                return [item["embedding"] for item in result["data"]]
            elif "embeddings" in result:  # Direct embeddings array
                return result["embeddings"]
            else:
                raise LLMProviderError(f"Unknown embedding response format: {result}")
            
        except requests.exceptions.Timeout:
            raise LLMProviderTimeoutError("Custom embedding API request timeout")
        except requests.exceptions.RequestException as e:
            raise LLMProviderAPIError(f"Custom embedding API request error: {e}")
        except Exception as e:
            raise LLMProviderError(f"Custom embedding error: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for query"""
        embeddings = self.embed_documents([text])
        return embeddings[0]
    
    def is_available(self) -> bool:
        """Check if custom embedding provider is available"""
        return self.client is not None and self.config.api_base is not None
    
    def get_langchain_embeddings(self):
        """Get LangChain compatible embeddings instance"""
        if not self.langchain_embeddings:
            raise LLMProviderNotAvailableError("Custom embedding provider not initialized")
        return self.langchain_embeddings
