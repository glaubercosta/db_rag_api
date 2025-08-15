"""
Testes para o módulo de configuração
"""
import pytest
import os
from unittest.mock import patch

from config import DatabaseConfig, OpenAIConfig, RAGConfig


class TestDatabaseConfig:
    """Testes para DatabaseConfig"""
    
    def test_valid_config_creation(self):
        """Testa criação de configuração válida"""
        config = DatabaseConfig(
            url="postgresql://user:pass@localhost:5432/db",
            type="postgresql"
        )
        assert config.url == "postgresql://user:pass@localhost:5432/db"
        assert config.type == "postgresql"
    
    def test_invalid_db_type_raises_error(self):
        """Testa que tipo de BD inválido levanta erro"""
        with pytest.raises(ValueError, match="Tipo de SGBD não suportado"):
            DatabaseConfig(
                url="postgresql://user:pass@localhost:5432/db",
                type="invalid_type"
            )
    
    def test_empty_url_raises_error(self):
        """Testa que URL vazia levanta erro"""
        with pytest.raises(ValueError, match="URL do banco de dados não pode estar vazia"):
            DatabaseConfig(url="", type="postgresql")
    
    @patch.dict(os.environ, {
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
        'DATABASE_TYPE': 'postgresql'
    })
    def test_from_env_valid(self):
        """Testa criação válida a partir de variáveis de ambiente"""
        config = DatabaseConfig.from_env()
        assert config.url == 'postgresql://test:test@localhost:5432/test'
        assert config.type == 'postgresql'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_url_raises_error(self):
        """Testa que ausência de DATABASE_URL levanta erro"""
        with pytest.raises(ValueError, match="DATABASE_URL não encontrada"):
            DatabaseConfig.from_env()


class TestOpenAIConfig:
    """Testes para OpenAIConfig"""
    
    def test_valid_config_creation(self):
        """Testa criação de configuração válida"""
        config = OpenAIConfig(api_key="sk-test1234567890123456789")
        assert config.api_key == "sk-test1234567890123456789"
        assert config.model == "gpt-4"  # valor padrão
        assert config.embedding_model == "text-embedding-ada-002"  # valor padrão
    
    def test_empty_api_key_raises_error(self):
        """Testa que chave vazia levanta erro"""
        with pytest.raises(ValueError, match="Chave da API OpenAI não pode estar vazia"):
            OpenAIConfig(api_key="")
    
    def test_invalid_api_key_format_raises_error(self):
        """Testa que formato de chave inválido levanta erro"""
        with pytest.raises(ValueError, match="Chave da API OpenAI deve começar com 'sk-'"):
            OpenAIConfig(api_key="invalid-key-format")
    
    def test_short_api_key_raises_error(self):
        """Testa que chave muito curta levanta erro"""
        with pytest.raises(ValueError, match="Chave da API OpenAI muito curta"):
            OpenAIConfig(api_key="sk-123")
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test1234567890123456789',
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'OPENAI_EMBEDDING_MODEL': 'text-embedding-3-small'
    })
    def test_from_env_valid(self):
        """Testa criação válida a partir de variáveis de ambiente"""
        config = OpenAIConfig.from_env()
        assert config.api_key == 'sk-test1234567890123456789'
        assert config.model == 'gpt-3.5-turbo'
        assert config.embedding_model == 'text-embedding-3-small'


class TestRAGConfig:
    """Testes para RAGConfig"""
    
    def test_valid_config_creation(self):
        """Testa criação de configuração válida"""
        config = RAGConfig(
            vector_store_path="./vector_store",
            similarity_search_k=10,
            table_sample_limit=500
        )
        assert config.vector_store_path == "./vector_store"
        assert config.similarity_search_k == 10
        assert config.table_sample_limit == 500
    
    def test_invalid_similarity_search_k_raises_error(self):
        """Testa que valor inválido para similarity_search_k levanta erro"""
        with pytest.raises(ValueError, match="similarity_search_k deve ser maior que 0"):
            RAGConfig(similarity_search_k=0)
        
        with pytest.raises(ValueError, match="similarity_search_k muito alto"):
            RAGConfig(similarity_search_k=100)
    
    def test_invalid_table_sample_limit_raises_error(self):
        """Testa que valor inválido para table_sample_limit levanta erro"""
        with pytest.raises(ValueError, match="table_sample_limit deve ser maior que 0"):
            RAGConfig(table_sample_limit=0)
    
    @patch.dict(os.environ, {
        'VECTOR_STORE_PATH': './custom_vector_store',
        'SIMILARITY_SEARCH_K': '15',
        'TABLE_SAMPLE_LIMIT': '2000'
    })
    def test_from_env_valid(self):
        """Testa criação válida a partir de variáveis de ambiente"""
        config = RAGConfig.from_env()
        assert config.vector_store_path == './custom_vector_store'
        assert config.similarity_search_k == 15
        assert config.table_sample_limit == 2000
