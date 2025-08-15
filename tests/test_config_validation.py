"""
Tests for configuration validation
"""
import pytest
from config import RAGConfig


class TestRAGConfigValidation:
    """Test RAGConfig validation logic"""

    def test_valid_default_config(self):
        """Test that default config is valid"""
        config = RAGConfig()
        assert config.similarity_search_k == 5
        assert config.table_sample_limit == 1000
        assert config.vector_store_path is None

    def test_valid_custom_config(self):
        """Test valid custom configuration"""
        config = RAGConfig(
            similarity_search_k=10,
            table_sample_limit=500,
            vector_store_path="./data/vector_store"
        )
        assert config.similarity_search_k == 10
        assert config.table_sample_limit == 500
        assert config.vector_store_path == "./data/vector_store"

    def test_similarity_search_k_validation(self):
        """Test similarity_search_k validation"""
        # Test negative value
        with pytest.raises(ValueError, match="similarity_search_k must be positive"):
            RAGConfig(similarity_search_k=-1)

        # Test zero value
        with pytest.raises(ValueError, match="similarity_search_k must be positive"):
            RAGConfig(similarity_search_k=0)

        # Test too large value
        with pytest.raises(ValueError, match="similarity_search_k must be <= 100"):
            RAGConfig(similarity_search_k=101)

        # Test non-integer type
        with pytest.raises(TypeError, match="similarity_search_k must be an integer"):
            RAGConfig(similarity_search_k="5")

        with pytest.raises(TypeError, match="similarity_search_k must be an integer"):
            RAGConfig(similarity_search_k=5.5)

    def test_table_sample_limit_validation(self):
        """Test table_sample_limit validation"""
        # Test negative value
        with pytest.raises(ValueError, match="table_sample_limit must be positive"):
            RAGConfig(table_sample_limit=-1)

        # Test zero value
        with pytest.raises(ValueError, match="table_sample_limit must be positive"):
            RAGConfig(table_sample_limit=0)

        # Test too large value
        with pytest.raises(ValueError, match="table_sample_limit must be <= 10000"):
            RAGConfig(table_sample_limit=10001)

        # Test non-integer type
        with pytest.raises(TypeError, match="table_sample_limit must be an integer"):
            RAGConfig(table_sample_limit="1000")

        with pytest.raises(TypeError, match="table_sample_limit must be an integer"):
            RAGConfig(table_sample_limit=1000.0)

    def test_vector_store_path_validation(self):
        """Test vector_store_path validation"""
        # Test empty string
        with pytest.raises(ValueError, match="vector_store_path cannot be empty string"):
            RAGConfig(vector_store_path="")

        # Test whitespace-only string
        with pytest.raises(ValueError, match="vector_store_path cannot be empty string"):
            RAGConfig(vector_store_path="   ")

        # Test non-string type
        with pytest.raises(TypeError, match="vector_store_path must be a string or None"):
            RAGConfig(vector_store_path=123)

        # Test None is valid
        config = RAGConfig(vector_store_path=None)
        assert config.vector_store_path is None

    def test_boundary_values(self):
        """Test boundary values"""
        # Test minimum valid values
        config = RAGConfig(similarity_search_k=1, table_sample_limit=1)
        assert config.similarity_search_k == 1
        assert config.table_sample_limit == 1

        # Test maximum valid values
        config = RAGConfig(similarity_search_k=100, table_sample_limit=10000)
        assert config.similarity_search_k == 100
        assert config.table_sample_limit == 10000

    def test_from_env_validation_errors(self, monkeypatch):
        """Test that from_env properly handles validation errors"""
        # Test invalid SIMILARITY_SEARCH_K
        monkeypatch.setenv("SIMILARITY_SEARCH_K", "not_a_number")
        with pytest.raises(ValueError, match="Invalid SIMILARITY_SEARCH_K"):
            RAGConfig.from_env()

        # Test invalid TABLE_SAMPLE_LIMIT
        monkeypatch.setenv("SIMILARITY_SEARCH_K", "5")
        monkeypatch.setenv("TABLE_SAMPLE_LIMIT", "not_a_number")
        with pytest.raises(ValueError, match="Invalid TABLE_SAMPLE_LIMIT"):
            RAGConfig.from_env()

    def test_from_env_valid_values(self, monkeypatch):
        """Test that from_env works with valid environment values"""
        monkeypatch.setenv("SIMILARITY_SEARCH_K", "10")
        monkeypatch.setenv("TABLE_SAMPLE_LIMIT", "2000")
        monkeypatch.setenv("VECTOR_STORE_PATH", "./test/path")

        config = RAGConfig.from_env()
        assert config.similarity_search_k == 10
        assert config.table_sample_limit == 2000
        assert config.vector_store_path == "./test/path"

    def test_from_env_boundary_validation(self, monkeypatch):
        """Test that from_env validates boundary conditions"""
        # Test negative similarity_search_k from environment
        monkeypatch.setenv("SIMILARITY_SEARCH_K", "-1")
        with pytest.raises(ValueError, match="similarity_search_k must be positive"):
            RAGConfig.from_env()

        # Test too large table_sample_limit from environment
        monkeypatch.setenv("SIMILARITY_SEARCH_K", "5")
        monkeypatch.setenv("TABLE_SAMPLE_LIMIT", "20000")
        with pytest.raises(ValueError, match="table_sample_limit must be <= 10000"):
            RAGConfig.from_env()
