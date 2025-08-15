"""
LLM Provider abstraction layer for supporting multiple LLM backends.

This module provides a flexible interface for integrating various LLM providers
including OpenAI, Anthropic, Ollama, Hugging Face, and custom enterprise models.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"  # For enterprise/custom endpoints


@dataclass
class LLMConfig:
    """Base configuration for LLM providers"""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    timeout: int = 30
    
    # Provider-specific configurations
    api_key: Optional[str] = None
    api_base: Optional[str] = None  # For custom endpoints
    api_version: Optional[str] = None
    
    # Custom headers for enterprise APIs
    custom_headers: Optional[Dict[str, str]] = None
    
    # Model-specific parameters
    extra_params: Optional[Dict[str, Any]] = None


@dataclass 
class EmbeddingConfig:
    """Configuration for embedding models"""
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    batch_size: int = 100
    extra_params: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the provider client"""
        pass
    
    @abstractmethod
    def generate_text(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text completion from prompt"""
        pass
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate chat completion from messages"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client = None
        
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the embedding provider"""
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents"""
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if embedding provider is available"""
        pass
    
    def get_embedding_dimension(self) -> Optional[int]:
        """Get the dimension of embeddings (if known)"""
        # This can be overridden by specific providers
        return None


class LLMProviderError(Exception):
    """Base exception for LLM provider errors"""
    pass


class LLMProviderNotAvailableError(LLMProviderError):
    """Raised when a provider is not available or misconfigured"""
    pass


class LLMProviderTimeoutError(LLMProviderError):
    """Raised when a provider request times out"""
    pass


class LLMProviderAPIError(LLMProviderError):
    """Raised when a provider API returns an error"""
    pass
