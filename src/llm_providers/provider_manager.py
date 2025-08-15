"""
LLM Provider Manager for coordinating multiple LLM providers
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from . import (
    LLMProvider, 
    LLMConfig, 
    EmbeddingConfig,
    BaseLLMProvider,
    BaseEmbeddingProvider,
    LLMProviderError,
    LLMProviderNotAvailableError
)
from .openai_provider import OpenAIProvider, OpenAIEmbeddingProvider
from .ollama_provider import OllamaProvider, OllamaEmbeddingProvider
from .custom_provider import CustomProvider, CustomEmbeddingProvider


@dataclass
class ProviderPreferences:
    """Configuration for provider selection preferences"""
    preferred_llm_provider: Optional[LLMProvider] = None
    preferred_embedding_provider: Optional[LLMProvider] = None
    fallback_providers: List[LLMProvider] = None
    auto_detect: bool = True
    
    def __post_init__(self):
        if self.fallback_providers is None:
            self.fallback_providers = [
                LLMProvider.OPENAI,
                LLMProvider.OLLAMA,
                LLMProvider.CUSTOM
            ]


class LLMProviderManager:
    """Manages multiple LLM providers and handles fallbacks"""
    
    def __init__(self, preferences: Optional[ProviderPreferences] = None):
        self.preferences = preferences or ProviderPreferences()
        self.llm_providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self.embedding_providers: Dict[LLMProvider, BaseEmbeddingProvider] = {}
        self.active_llm_provider: Optional[BaseLLMProvider] = None
        self.active_embedding_provider: Optional[BaseEmbeddingProvider] = None
        
    def add_llm_provider(self, provider_type: LLMProvider, config: LLMConfig) -> None:
        """Add an LLM provider with configuration"""
        provider_classes = {
            LLMProvider.OPENAI: OpenAIProvider,
            LLMProvider.OLLAMA: OllamaProvider,
            LLMProvider.CUSTOM: CustomProvider
        }
        
        if provider_type not in provider_classes:
            raise LLMProviderError(f"Unsupported LLM provider: {provider_type}")
        
        provider_class = provider_classes[provider_type]
        provider = provider_class(config)
        
        try:
            provider.initialize()
            self.llm_providers[provider_type] = provider
            print(f"✅ LLM Provider {provider_type.value} initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize LLM provider {provider_type.value}: {e}")
            # Store the provider anyway for potential later retry
            self.llm_providers[provider_type] = provider
    
    def add_embedding_provider(self, provider_type: LLMProvider, config: EmbeddingConfig) -> None:
        """Add an embedding provider with configuration"""
        provider_classes = {
            LLMProvider.OPENAI: OpenAIEmbeddingProvider,
            LLMProvider.OLLAMA: OllamaEmbeddingProvider,
            LLMProvider.CUSTOM: CustomEmbeddingProvider
        }
        
        if provider_type not in provider_classes:
            raise LLMProviderError(f"Unsupported embedding provider: {provider_type}")
        
        provider_class = provider_classes[provider_type]
        provider = provider_class(config)
        
        try:
            provider.initialize()
            self.embedding_providers[provider_type] = provider
            print(f"✅ Embedding Provider {provider_type.value} initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize embedding provider {provider_type.value}: {e}")
            # Store the provider anyway for potential later retry
            self.embedding_providers[provider_type] = provider
    
    def select_active_llm_provider(self) -> Optional[BaseLLMProvider]:
        """Select the best available LLM provider based on preferences"""
        # Try preferred provider first
        if self.preferences.preferred_llm_provider:
            preferred = self.llm_providers.get(self.preferences.preferred_llm_provider)
            if preferred and preferred.is_available():
                self.active_llm_provider = preferred
                print(f"🎯 Using preferred LLM provider: {self.preferences.preferred_llm_provider.value}")
                return preferred
        
        # Try fallback providers
        for provider_type in self.preferences.fallback_providers:
            provider = self.llm_providers.get(provider_type)
            if provider and provider.is_available():
                self.active_llm_provider = provider
                print(f"🔄 Using fallback LLM provider: {provider_type.value}")
                return provider
        
        print("❌ No available LLM providers found")
        return None
    
    def select_active_embedding_provider(self) -> Optional[BaseEmbeddingProvider]:
        """Select the best available embedding provider based on preferences"""
        # Try preferred provider first
        if self.preferences.preferred_embedding_provider:
            preferred = self.embedding_providers.get(self.preferences.preferred_embedding_provider)
            if preferred and preferred.is_available():
                self.active_embedding_provider = preferred
                print(f"🎯 Using preferred embedding provider: {self.preferences.preferred_embedding_provider.value}")
                return preferred
        
        # Try fallback providers
        for provider_type in self.preferences.fallback_providers:
            provider = self.embedding_providers.get(provider_type)
            if provider and provider.is_available():
                self.active_embedding_provider = provider
                print(f"🔄 Using fallback embedding provider: {provider_type.value}")
                return provider
        
        print("❌ No available embedding providers found")
        return None
    
    def get_active_llm_provider(self) -> BaseLLMProvider:
        """Get the currently active LLM provider"""
        if not self.active_llm_provider:
            provider = self.select_active_llm_provider()
            if not provider:
                raise LLMProviderNotAvailableError("No LLM providers available")
        return self.active_llm_provider
    
    def get_active_embedding_provider(self) -> BaseEmbeddingProvider:
        """Get the currently active embedding provider"""
        if not self.active_embedding_provider:
            provider = self.select_active_embedding_provider()
            if not provider:
                raise LLMProviderNotAvailableError("No embedding providers available")
        return self.active_embedding_provider
    
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text using the active LLM provider"""
        provider = self.get_active_llm_provider()
        return provider.generate_text(prompt, system_prompt, **kwargs)
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat completion using the active LLM provider"""
        provider = self.get_active_llm_provider()
        return provider.chat_completion(messages, **kwargs)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents using the active provider"""
        provider = self.get_active_embedding_provider()
        return provider.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for query using the active provider"""
        provider = self.get_active_embedding_provider()
        return provider.embed_query(text)
    
    def get_langchain_llm(self):
        """Get LangChain compatible LLM instance"""
        provider = self.get_active_llm_provider()
        return provider.get_langchain_llm()
    
    def get_langchain_embeddings(self):
        """Get LangChain compatible embeddings instance"""
        provider = self.get_active_embedding_provider()
        return provider.get_langchain_embeddings()
    
    def list_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers and their status"""
        status = {
            "llm_providers": {},
            "embedding_providers": {}
        }
        
        for provider_type, provider in self.llm_providers.items():
            status["llm_providers"][provider_type.value] = {
                "available": provider.is_available(),
                "model_info": provider.get_model_info() if provider.is_available() else None,
                "active": provider == self.active_llm_provider
            }
        
        for provider_type, provider in self.embedding_providers.items():
            status["embedding_providers"][provider_type.value] = {
                "available": provider.is_available(),
                "embedding_dimension": provider.get_embedding_dimension() if provider.is_available() else None,
                "active": provider == self.active_embedding_provider
            }
        
        return status
    
    def switch_llm_provider(self, provider_type: LLMProvider) -> bool:
        """Switch to a different LLM provider"""
        provider = self.llm_providers.get(provider_type)
        if provider and provider.is_available():
            self.active_llm_provider = provider
            print(f"🔄 Switched to LLM provider: {provider_type.value}")
            return True
        else:
            print(f"❌ Cannot switch to LLM provider {provider_type.value}: not available")
            return False
    
    def switch_embedding_provider(self, provider_type: LLMProvider) -> bool:
        """Switch to a different embedding provider"""
        provider = self.embedding_providers.get(provider_type)
        if provider and provider.is_available():
            self.active_embedding_provider = provider
            print(f"🔄 Switched to embedding provider: {provider_type.value}")
            return True
        else:
            print(f"❌ Cannot switch to embedding provider {provider_type.value}: not available")
            return False


def create_provider_manager_from_env() -> LLMProviderManager:
    """Create provider manager from environment variables"""
    manager = LLMProviderManager()
    
    # OpenAI configuration
    if os.getenv("OPENAI_API_KEY"):
        openai_llm_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")) if os.getenv("OPENAI_MAX_TOKENS") else None,
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE"),
        )
        manager.add_llm_provider(LLMProvider.OPENAI, openai_llm_config)
        
        openai_embedding_config = EmbeddingConfig(
            provider=LLMProvider.OPENAI,
            model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE"),
        )
        manager.add_embedding_provider(LLMProvider.OPENAI, openai_embedding_config)
    
    # Ollama configuration
    if os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_MODEL"):
        ollama_llm_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name=os.getenv("OLLAMA_MODEL", "llama2"),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.0")),
            api_base=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
        manager.add_llm_provider(LLMProvider.OLLAMA, ollama_llm_config)
        
        if os.getenv("OLLAMA_EMBEDDING_MODEL"):
            ollama_embedding_config = EmbeddingConfig(
                provider=LLMProvider.OLLAMA,
                model_name=os.getenv("OLLAMA_EMBEDDING_MODEL"),
                api_base=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
            manager.add_embedding_provider(LLMProvider.OLLAMA, ollama_embedding_config)
    
    # Custom/Enterprise configuration
    if os.getenv("CUSTOM_LLM_API_BASE"):
        custom_headers = {}
        if os.getenv("CUSTOM_LLM_API_KEY"):
            custom_headers["Authorization"] = f"Bearer {os.getenv('CUSTOM_LLM_API_KEY')}"
        
        custom_llm_config = LLMConfig(
            provider=LLMProvider.CUSTOM,
            model_name=os.getenv("CUSTOM_LLM_MODEL", "custom-model"),
            temperature=float(os.getenv("CUSTOM_LLM_TEMPERATURE", "0.0")),
            api_base=os.getenv("CUSTOM_LLM_API_BASE"),
            custom_headers=custom_headers,
            extra_params={
                "format": os.getenv("CUSTOM_LLM_FORMAT", "openai"),
                "endpoint": os.getenv("CUSTOM_LLM_ENDPOINT", "/v1/chat/completions")
            }
        )
        manager.add_llm_provider(LLMProvider.CUSTOM, custom_llm_config)
        
        if os.getenv("CUSTOM_EMBEDDING_API_BASE"):
            custom_embedding_config = EmbeddingConfig(
                provider=LLMProvider.CUSTOM,
                model_name=os.getenv("CUSTOM_EMBEDDING_MODEL", "custom-embedding"),
                api_base=os.getenv("CUSTOM_EMBEDDING_API_BASE"),
                custom_headers=custom_headers,
                extra_params={
                    "endpoint": os.getenv("CUSTOM_EMBEDDING_ENDPOINT", "/v1/embeddings")
                }
            )
            manager.add_embedding_provider(LLMProvider.CUSTOM, custom_embedding_config)
    
    # Select active providers
    manager.select_active_llm_provider()
    manager.select_active_embedding_provider()
    
    return manager
