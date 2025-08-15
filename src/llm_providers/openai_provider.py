"""
OpenAI LLM Provider implementation
"""
import openai
from typing import List, Dict, Optional, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

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


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT models provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.langchain_llm = None
        
    def initialize(self) -> None:
        """Initialize OpenAI client"""
        if not self.config.api_key:
            raise LLMProviderNotAvailableError("OpenAI API key not provided")
            
        try:
            # Initialize OpenAI client
            openai.api_key = self.config.api_key
            if self.config.api_base:
                openai.api_base = self.config.api_base
            if self.config.api_version:
                openai.api_version = self.config.api_version
                
            self.client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base,
                timeout=self.config.timeout
            )
            
            # Create LangChain ChatOpenAI instance
            self.langchain_llm = ChatOpenAI(
                model=self.config.model_name,
                api_key=self.config.api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                base_url=self.config.api_base,
                timeout=self.config.timeout
            )
            
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize OpenAI provider: {e}")
    
    def generate_text(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API"""
        if not self.client:
            raise LLMProviderNotAvailableError("OpenAI provider not initialized")
            
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except openai.APITimeoutError as e:
            raise LLMProviderTimeoutError(f"OpenAI request timeout: {e}")
        except openai.APIError as e:
            raise LLMProviderAPIError(f"OpenAI API error: {e}")
        except Exception as e:
            raise LLMProviderError(f"OpenAI generation error: {e}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Generate chat completion using OpenAI API"""
        if not self.client:
            raise LLMProviderNotAvailableError("OpenAI provider not initialized")
            
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except openai.APITimeoutError as e:
            raise LLMProviderTimeoutError(f"OpenAI request timeout: {e}")
        except openai.APIError as e:
            raise LLMProviderAPIError(f"OpenAI API error: {e}")
        except Exception as e:
            raise LLMProviderError(f"OpenAI chat completion error: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return (
            self.config.api_key is not None 
            and self.client is not None
        )
    
    def get_langchain_llm(self):
        """Get LangChain compatible LLM instance"""
        if not self.langchain_llm:
            raise LLMProviderNotAvailableError("OpenAI provider not initialized")
        return self.langchain_llm


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embeddings provider"""
    
    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.langchain_embeddings = None
        
    def initialize(self) -> None:
        """Initialize OpenAI embeddings"""
        if not self.config.api_key:
            raise LLMProviderNotAvailableError("OpenAI API key not provided")
            
        try:
            self.client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base
            )
            
            # Create LangChain OpenAIEmbeddings instance
            self.langchain_embeddings = OpenAIEmbeddings(
                api_key=self.config.api_key,
                model=self.config.model_name,
                openai_api_base=self.config.api_base
            )
            
        except Exception as e:
            raise LLMProviderError(f"Failed to initialize OpenAI embeddings: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents"""
        if not self.langchain_embeddings:
            raise LLMProviderNotAvailableError("OpenAI embeddings not initialized")
            
        try:
            return self.langchain_embeddings.embed_documents(texts)
        except Exception as e:
            raise LLMProviderError(f"OpenAI embedding error: {e}")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for query"""
        if not self.langchain_embeddings:
            raise LLMProviderNotAvailableError("OpenAI embeddings not initialized")
            
        try:
            return self.langchain_embeddings.embed_query(text)
        except Exception as e:
            raise LLMProviderError(f"OpenAI query embedding error: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI embeddings are available"""
        return (
            self.config.api_key is not None 
            and self.langchain_embeddings is not None
        )
    
    def get_embedding_dimension(self) -> Optional[int]:
        """Get OpenAI embedding dimension"""
        model_dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
        return model_dimensions.get(self.config.model_name)
    
    def get_langchain_embeddings(self):
        """Get LangChain compatible embeddings instance"""
        if not self.langchain_embeddings:
            raise LLMProviderNotAvailableError("OpenAI embeddings not initialized")
        return self.langchain_embeddings
