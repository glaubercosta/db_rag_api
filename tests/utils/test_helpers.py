"""Test utilities and helper functions."""

import os
import tempfile
import shutil
from contextlib import contextmanager
from unittest.mock import Mock, patch


class MockOpenAIClient:
    """Mock OpenAI client for testing."""
    
    def __init__(self):
        self.chat = Mock()
        self.embeddings = Mock()
        
        # Setup default responses
        self.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="SELECT * FROM test_table;"))]
        )
        
        self.embeddings.create.return_value = Mock(
            data=[Mock(embedding=[0.1] * 1536)]
        )


@contextmanager
def temporary_directory():
    """Create a temporary directory that gets cleaned up."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def mock_openai_environment():
    """Mock OpenAI environment for testing."""
    with patch('openai.OpenAI') as mock_openai:
        mock_client = MockOpenAIClient()
        mock_openai.return_value = mock_client
        yield mock_client


def create_test_vector_store_files(base_path):
    """Create test vector store files."""
    # Create dummy vector store files
    vector_file = base_path
    checksum_file = base_path + "_checksum.txt"
    metadata_file = base_path + "_metadata.json"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(vector_file), exist_ok=True)
    
    # Create dummy files
    with open(vector_file, 'wb') as f:
        f.write(b"dummy_vector_data")
    
    with open(checksum_file, 'w') as f:
        f.write("dummy_checksum")
    
    with open(metadata_file, 'w') as f:
        f.write('{"test": "metadata"}')
    
    return vector_file, checksum_file, metadata_file


def cleanup_test_files(*file_paths):
    """Clean up test files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass


def assert_sql_security(scanner, malicious_inputs):
    """Assert that malicious SQL inputs are blocked."""
    import pytest
    
    for malicious_input in malicious_inputs:
        with pytest.raises(ValueError, match="Invalid table name"):
            scanner.sanitize_table_name(malicious_input)


def assert_performance_within_limits(operation, max_time_seconds=1.0):
    """Assert that an operation completes within time limits."""
    import time
    
    start_time = time.time()
    result = operation()
    elapsed = time.time() - start_time
    
    assert elapsed < max_time_seconds, \
        f"Operation took {elapsed:.3f}s, expected < {max_time_seconds}s"
    
    return result


def create_sample_database_data():
    """Create sample database data for testing."""
    return {
        'users': [
            {'id': 1, 'name': 'João Silva', 'email': 'joao@email.com', 'age': 30},
            {'id': 2, 'name': 'Maria Santos', 'email': 'maria@email.com', 'age': 25},
            {'id': 3, 'name': 'Pedro Costa', 'email': 'pedro@email.com', 'age': 35}
        ],
        'categories': [
            {'id': 1, 'name': 'Eletrônicos', 'description': 'Dispositivos eletrônicos'},
            {'id': 2, 'name': 'Livros', 'description': 'Livros físicos e digitais'},
            {'id': 3, 'name': 'Roupas', 'description': 'Vestuário e acessórios'}
        ],
        'products': [
            {'id': 1, 'name': 'Smartphone', 'price': 299.99, 'category_id': 1},
            {'id': 2, 'name': 'Notebook', 'price': 899.99, 'category_id': 1},
            {'id': 3, 'name': 'Python Book', 'price': 49.99, 'category_id': 2}
        ]
    }


def validate_test_environment():
    """Validate that test environment is properly set up."""
    required_modules = ['pytest', 'sqlalchemy', 'openai']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        raise ImportError(f"Missing required modules: {missing_modules}")
    
    return True


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def sql_injection_attempts():
        """Generate SQL injection test cases."""
        return [
            "users; DROP TABLE users;",
            "users' OR '1'='1",
            "users UNION SELECT * FROM users",
            "users'; DELETE FROM users; --",
            "users/**/OR/**/1=1",
            "users\n; DROP TABLE users;",
            "users WHERE 1=1; UPDATE users SET name='hacked'",
            "users; INSERT INTO malicious_table VALUES (1, 'hacker')",
        ]
    
    @staticmethod
    def valid_table_names():
        """Generate valid table name test cases."""
        return [
            "users",
            "user_profiles", 
            "UserData",
            "table123",
            "products",
            "categories",
            "order_items",
            "inventory_2024"
        ]
    
    @staticmethod
    def performance_test_queries():
        """Generate queries for performance testing."""
        return [
            ("users", 5),
            ("users", 10),
            ("categories", 3),
            ("products", 15),
            ("users", 1),
        ]
    
    @staticmethod
    def sample_documents():
        """Generate sample documents for vector store testing."""
        return [
            "This database contains user information including names and emails.",
            "Product catalog with categories and pricing information.",
            "Order management system with relationships between users and products.",
            "Inventory tracking with stock levels and product details.",
            "Customer data analysis for business intelligence purposes.",
            "Foreign key relationships maintain data integrity across tables.",
            "SQL queries can retrieve complex information from multiple tables."
        ]


def skip_if_no_openai_key():
    """Skip test if OpenAI API key is not available."""
    import pytest
    
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("OpenAI API key not available")


def skip_if_no_database():
    """Skip test if database connection is not available."""
    import pytest
    
    # This would check for actual database availability
    # For now, we'll skip based on environment variable
    if os.getenv('SKIP_DB_TESTS'):
        pytest.skip("Database tests disabled")


class DatabaseTestHelper:
    """Helper class for database testing operations."""
    
    @staticmethod
    def verify_table_exists(scanner, table_name):
        """Verify that a table exists in the database."""
        tables = scanner.get_table_names()
        assert table_name in tables, f"Table {table_name} not found in {tables}"
    
    @staticmethod
    def verify_data_integrity(scanner, table_name, expected_count=None):
        """Verify data integrity for a table."""
        data = scanner.query_table_sample(table_name, limit=1000)
        assert isinstance(data, list)
        
        if expected_count is not None:
            assert len(data) == expected_count
        
        return data
    
    @staticmethod
    def verify_schema_structure(scanner, table_name, expected_columns=None):
        """Verify schema structure for a table."""
        schema = scanner.get_table_schema(table_name)
        
        assert isinstance(schema, dict)
        assert "columns" in schema
        assert "primary_keys" in schema
        assert "foreign_keys" in schema
        
        if expected_columns:
            column_names = [col["name"] for col in schema["columns"]]
            for expected_col in expected_columns:
                assert expected_col in column_names
        
        return schema
