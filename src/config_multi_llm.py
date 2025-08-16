"""
Configuração Multi-LLM para o Database RAG System
=================================================

Este módulo fornece configurações para múltiplos provedores de LLM,
incluindo OpenAI, Ollama e APIs customizadas.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()


class LLMProvider(Enum):
    """Enum dos provedores de LLM suportados"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class EmbeddingProvider(Enum):
    """Enum dos provedores de embedding suportados"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class DatabaseConfig:
    """Configuração do banco de dados"""
    database_type: str = "sqlite"
    database_url: Optional[str] = None
    database_path: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Criar configuração a partir das variáveis de ambiente"""
        return cls(
            database_type=os.getenv('DATABASE_TYPE', 'sqlite'),
            database_url=os.getenv('DATABASE_URL'),
            database_path=os.getenv('DATABASE_PATH', './data/example.db')
        )


@dataclass
class RAGConfig:
    """RAG system configuration"""
    vector_store_path: Optional[str] = None
    similarity_search_k: int = 5
    table_sample_limit: int = 1000

    def __post_init__(self):
        """Validate configuration parameters"""
        # Validate similarity_search_k
        if not isinstance(self.similarity_search_k, int):
            raise TypeError(
                f"similarity_search_k must be an integer, got "
                f"{type(self.similarity_search_k).__name__}"
            )
        if self.similarity_search_k <= 0:
            raise ValueError(
                f"similarity_search_k must be positive, got "
                f"{self.similarity_search_k}"
            )
        if self.similarity_search_k > 100:
            raise ValueError(
                f"similarity_search_k must be <= 100 for performance, got "
                f"{self.similarity_search_k}"
            )

        # Validate table_sample_limit
        if not isinstance(self.table_sample_limit, int):
            raise TypeError(
                f"table_sample_limit must be an integer, got "
                f"{type(self.table_sample_limit).__name__}"
            )
        if self.table_sample_limit <= 0:
            raise ValueError(
                f"table_sample_limit must be positive, got "
                f"{self.table_sample_limit}"
            )
        if self.table_sample_limit > 10000:
            raise ValueError(
                f"table_sample_limit must be <= 10000 for performance, got "
                f"{self.table_sample_limit}"
            )

        # Validate vector_store_path if provided
        if self.vector_store_path is not None:
            if not isinstance(self.vector_store_path, str):
                raise TypeError(
                    f"vector_store_path must be a string or None, got "
                    f"{type(self.vector_store_path).__name__}"
                )
            if not self.vector_store_path.strip():
                raise ValueError(
                    "vector_store_path cannot be empty string"
                )

    @classmethod
    def from_env(cls) -> "RAGConfig":
        """Create config from environment variables"""
        vector_store_path = os.getenv("VECTOR_STORE_PATH")
        
        try:
            similarity_search_k = int(os.getenv("SIMILARITY_SEARCH_K", "5"))
        except ValueError as e:
            raise ValueError(
                f"Invalid SIMILARITY_SEARCH_K in environment: {e}"
            )
        
        try:
            table_sample_limit = int(os.getenv("TABLE_SAMPLE_LIMIT", "1000"))
        except ValueError as e:
            raise ValueError(
                f"Invalid TABLE_SAMPLE_LIMIT in environment: {e}"
            )
        
        config = cls(
            vector_store_path=vector_store_path,
            similarity_search_k=similarity_search_k,
            table_sample_limit=table_sample_limit
        )
        
        # Trigger validation
        config.__post_init__()
        
        return config


@dataclass
class LLMConfig:
    """Configuração base para provedores de LLM"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        if isinstance(self.provider, str):
            self.provider = LLMProvider(self.provider)


@dataclass
class EmbeddingConfig:
    """Configuração base para provedores de embedding"""
    provider: EmbeddingProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    dimension: Optional[int] = None
    
    def __post_init__(self):
        if isinstance(self.provider, str):
            self.provider = EmbeddingProvider(self.provider)


@dataclass
class OpenAIConfig:
    """Configuração específica do OpenAI"""
    api_key: str
    model: str = "gpt-4"
    embedding_model: str = "text-embedding-ada-002"
    base_url: str = "https://api.openai.com/v1"
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> Optional['OpenAIConfig']:
        """Criar configuração OpenAI a partir do ambiente"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        return cls(
            api_key=api_key,
            model=os.getenv('OPENAI_MODEL', 'gpt-4'),
            embedding_model=os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-ada-002'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            timeout=int(os.getenv('HTTP_TIMEOUT', 30)),
            max_retries=int(os.getenv('MAX_RETRIES', 3))
        )


@dataclass
class OllamaConfig:
    """Configuração específica do Ollama"""
    base_url: str = "http://localhost:11434"
    model: str = "llama2"
    embedding_model: str = "llama2"
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> Optional['OllamaConfig']:
        """Criar configuração Ollama a partir do ambiente"""
        model = os.getenv('OLLAMA_MODEL')
        if not model:
            return None
        
        return cls(
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            model=model,
            embedding_model=os.getenv('OLLAMA_EMBEDDING_MODEL', model),
            timeout=int(os.getenv('HTTP_TIMEOUT', 30)),
            max_retries=int(os.getenv('MAX_RETRIES', 3))
        )


@dataclass
class CustomConfig:
    """Configuração para APIs customizadas"""
    api_base: str
    model: str
    api_key: Optional[str] = None
    format: str = "openai"  # "openai" ou "ollama"
    endpoint: Optional[str] = None
    embedding_endpoint: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> Optional['CustomConfig']:
        """Criar configuração customizada a partir do ambiente"""
        api_base = os.getenv('CUSTOM_LLM_API_BASE')
        model = os.getenv('CUSTOM_LLM_MODEL')
        
        if not api_base or not model:
            return None
        
        # Coletar headers customizados
        extra_headers = {}
        for key, value in os.environ.items():
            if key.startswith('CUSTOM_LLM_HEADER_'):
                header_name = key.replace('CUSTOM_LLM_HEADER_', '').replace('_', '-')
                extra_headers[header_name] = value
        
        format_type = os.getenv('CUSTOM_LLM_FORMAT', 'openai')
        
        # Endpoints padrão baseados no formato
        if format_type == "openai":
            default_endpoint = "/v1/chat/completions"
            default_embedding_endpoint = "/v1/embeddings"
        else:  # ollama
            default_endpoint = "/api/generate"
            default_embedding_endpoint = "/api/embeddings"
        
        return cls(
            api_base=api_base,
            model=model,
            api_key=os.getenv('CUSTOM_LLM_API_KEY'),
            format=format_type,
            endpoint=os.getenv('CUSTOM_LLM_ENDPOINT', default_endpoint),
            embedding_endpoint=os.getenv('CUSTOM_LLM_EMBEDDING_ENDPOINT', default_embedding_endpoint),
            extra_headers=extra_headers,
            timeout=int(os.getenv('HTTP_TIMEOUT', 30)),
            max_retries=int(os.getenv('MAX_RETRIES', 3))
        )


@dataclass
class MultiLLMConfig:
    """Configuração completa do sistema Multi-LLM"""
    database: DatabaseConfig
    openai: Optional[OpenAIConfig] = None
    ollama: Optional[OllamaConfig] = None
    custom: Optional[CustomConfig] = None
    preferred_llm_provider: Optional[LLMProvider] = None
    preferred_embedding_provider: Optional[EmbeddingProvider] = None
    api_key: str = "dev-multi-llm-key-12345"
    log_level: str = "INFO"
    enable_provider_logging: bool = False
    
    @classmethod
    def from_env(cls) -> 'MultiLLMConfig':
        """Criar configuração completa a partir das variáveis de ambiente"""
        # Configurar provedores
        openai_config = OpenAIConfig.from_env()
        ollama_config = OllamaConfig.from_env()
        custom_config = CustomConfig.from_env()
        
        # Preferências de provedor
        preferred_llm = os.getenv('PREFERRED_LLM_PROVIDER')
        preferred_embedding = os.getenv('PREFERRED_EMBEDDING_PROVIDER')
        
        # Converter strings para enums se fornecidas
        preferred_llm_provider = None
        if preferred_llm:
            try:
                preferred_llm_provider = LLMProvider(preferred_llm)
            except ValueError:
                pass
        
        preferred_embedding_provider = None
        if preferred_embedding:
            try:
                preferred_embedding_provider = EmbeddingProvider(preferred_embedding)
            except ValueError:
                pass
        
        return cls(
            database=DatabaseConfig.from_env(),
            openai=openai_config,
            ollama=ollama_config,
            custom=custom_config,
            preferred_llm_provider=preferred_llm_provider,
            preferred_embedding_provider=preferred_embedding_provider,
            api_key=os.getenv('API_KEY', 'dev-multi-llm-key-12345'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            enable_provider_logging=os.getenv('ENABLE_PROVIDER_LOGGING', 'false').lower() == 'true'
        )
    
    def get_available_llm_providers(self) -> List[LLMProvider]:
        """Retorna lista de provedores LLM disponíveis"""
        providers = []
        if self.openai:
            providers.append(LLMProvider.OPENAI)
        if self.ollama:
            providers.append(LLMProvider.OLLAMA)
        if self.custom:
            providers.append(LLMProvider.CUSTOM)
        return providers
    
    def get_available_embedding_providers(self) -> List[EmbeddingProvider]:
        """Retorna lista de provedores de embedding disponíveis"""
        providers = []
        if self.openai:
            providers.append(EmbeddingProvider.OPENAI)
        if self.ollama:
            providers.append(EmbeddingProvider.OLLAMA)
        if self.custom:
            providers.append(EmbeddingProvider.CUSTOM)
        return providers
    
    def has_any_provider(self) -> bool:
        """Verifica se há pelo menos um provedor configurado"""
        return bool(self.openai or self.ollama or self.custom)
    
    def __str__(self) -> str:
        """Representação string da configuração"""
        available_llm = [p.value for p in self.get_available_llm_providers()]
        available_embedding = [p.value for p in self.get_available_embedding_providers()]
        
        return (
            f"MultiLLMConfig("
            f"llm_providers={available_llm}, "
            f"embedding_providers={available_embedding}, "
            f"preferred_llm={self.preferred_llm_provider.value if self.preferred_llm_provider else None}, "
            f"preferred_embedding={self.preferred_embedding_provider.value if self.preferred_embedding_provider else None}"
            f")"
        )


# Função de conveniência para obter configuração padrão
def get_multi_llm_config() -> MultiLLMConfig:
    """Obter configuração Multi-LLM a partir das variáveis de ambiente"""
    return MultiLLMConfig.from_env()


# Validação de configuração
def validate_config(config: MultiLLMConfig) -> List[str]:
    """Validar configuração e retornar lista de erros/avisos"""
    issues = []
    
    if not config.has_any_provider():
        issues.append("ERRO: Nenhum provedor de LLM configurado")
    
    if config.preferred_llm_provider:
        available = config.get_available_llm_providers()
        if config.preferred_llm_provider not in available:
            issues.append(
                f"AVISO: Provedor LLM preferido '{config.preferred_llm_provider.value}' "
                f"não está disponível. Disponíveis: {[p.value for p in available]}"
            )
    
    if config.preferred_embedding_provider:
        available_embedding = config.get_available_embedding_providers()
        if config.preferred_embedding_provider not in available_embedding:
            issues.append(
                f"AVISO: Provedor de embedding preferido '{config.preferred_embedding_provider.value}' "
                f"não está disponível. Disponíveis: {[p.value for p in available_embedding]}"
            )
    
    return issues
