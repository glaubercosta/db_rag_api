"""
Application configuration
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    type: str = "postgresql"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create config from environment variables"""
        url = os.getenv("DATABASE_URL")
        if not url:
            raise ValueError("DATABASE_URL not found in environment variables")
        db_type = os.getenv("DATABASE_TYPE", "postgresql")
        return cls(url=url, type=db_type)


@dataclass
class OpenAIConfig:
    """OpenAI configuration"""
    api_key: str
    model: str = "gpt-4"
    embedding_model: str = "text-embedding-ada-002"

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        """Create config from environment variables"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables"
            )
        # Trim whitespace/newlines that may come from secret files
        api_key = api_key.strip()
    # Remove UTF-8 BOM if file saved with BOM (common on Windows Notepad)
        if api_key.startswith("\ufeff"):
            api_key = api_key.lstrip("\ufeff")
        # Remove surrounding quotes if user wrapped the key
        quoted_double = (
            api_key.startswith('"') and api_key.endswith('"')
            and len(api_key) > 2
        )
        quoted_single = (
            api_key.startswith("'") and api_key.endswith("'")
            and len(api_key) > 2
        )
        if quoted_double or quoted_single:
            api_key = api_key[1:-1]
        # Validate API key is ASCII-only to avoid downstream httpx header
        # encoding errors
    # Simple ASCII check (OpenAI keys are ASCII, often start with 'sk-')
        non_ascii = [i for i, ch in enumerate(api_key) if ord(ch) > 127]
        if non_ascii:
            pos_info = non_ascii[0]
            raise ValueError(
                "OPENAI_API_KEY contains non-ASCII characters at position "
                f"{pos_info}. Re-create the secret file without accents or "
                "BOM."
            )
        if not api_key.startswith("sk-"):
            # Warn but don't fail – pattern may change
            print(
                "[config] Warning: OPENAI_API_KEY does not start with 'sk-'"
                "; verify key correctness."
            )
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        embedding_model = os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
        )
        return cls(
            api_key=api_key,
            model=model,
            embedding_model=embedding_model,
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
            
        return cls(
            vector_store_path=vector_store_path,
            similarity_search_k=similarity_search_k,
            table_sample_limit=table_sample_limit,
        )
