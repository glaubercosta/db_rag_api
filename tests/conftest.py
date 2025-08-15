"""Global pytest configuration and fixtures."""

import os
import sys
import tempfile
import pytest
from unittest.mock import Mock, patch
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import StaticPool

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import after path setup
try:
    from config import DatabaseConfig, OpenAIConfig, RAGConfig  # noqa: E402
    from database_scanner import DatabaseScanner  # noqa: E402
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Project root: {project_root}")
    raise


@pytest.fixture(scope="session")
def temp_directory():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="session")
def test_database_config():
    """Provide a test database configuration."""
    return DatabaseConfig(
        url="sqlite:///:memory:",
        type="sqlite"
    )


@pytest.fixture(scope="session")
def test_openai_config():
    """Provide a test OpenAI configuration."""
    return OpenAIConfig(
        api_key="test-key-" + "x" * 40,
        model="gpt-3.5-turbo",
        embedding_model="text-embedding-ada-002"
    )


@pytest.fixture(scope="session")
def test_rag_config(temp_directory):
    """Provide a test RAG configuration."""
    return RAGConfig(
        similarity_search_k=3,
        table_sample_limit=5,
        vector_store_path=os.path.join(temp_directory, "test_vectors")
    )


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock.return_value = mock_client

        # Mock chat completions
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="SELECT * FROM test_table;"))]
        )

        # Mock embeddings
        mock_client.embeddings.create.return_value = Mock(
            data=[Mock(embedding=[0.1] * 1536)]
        )

        yield mock_client


@pytest.fixture
def in_memory_database():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )

    # Create test tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                age INTEGER,
                created_at TIMESTAMP
            )
        """))

        conn.execute(text("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))

        conn.execute(text("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description TEXT
            )
        """))

        conn.execute(text("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                category_id INTEGER,
                created_at TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """))

        # Insert sample data
        conn.execute(text("""
            INSERT INTO users (name, email, age) VALUES
            ('João Silva', 'joao@email.com', 30),
            ('Maria Santos', 'maria@email.com', 25),
            ('Pedro Costa', 'pedro@email.com', 35)
        """))

        conn.execute(text("""
            INSERT INTO posts (title, content, user_id) VALUES
            ('Post 1', 'Content of post 1', 1),
            ('Post 2', 'Content of post 2', 2),
            ('Post 3', 'Content of post 3', 1)
        """))

        conn.execute(text("""
            INSERT INTO categories (name, description) VALUES
            ('Eletrônicos', 'Dispositivos eletrônicos em geral'),
            ('Livros', 'Livros físicos e digitais'),
            ('Roupas', 'Vestuário e acessórios')
        """))

        conn.execute(text("""
            INSERT INTO products (name, description, price, category_id) VALUES
            ('Smartphone', 'Smartphone Android', 299.99, 1),
            ('Notebook', 'Notebook para trabalho', 899.99, 1),
            ('Python Cookbook', 'Livro de programação', 49.99, 2)
        """))

        conn.commit()

    yield engine
    engine.dispose()


@pytest.fixture
def database_scanner_with_shared_engine(in_memory_database):
    """Create a database scanner instance that shares the test database engine."""
    config = DatabaseConfig(url="sqlite:///:memory:", type="sqlite")
    scanner = DatabaseScanner(config)
    # Replace the scanner's engine with our test engine
    scanner.engine = in_memory_database
    # Invalidate the inspector cache so it uses the new engine
    scanner.inspector = inspect(in_memory_database)
    yield scanner


@pytest.fixture
def database_scanner(database_scanner_with_shared_engine):
    """Alias for backwards compatibility."""
    yield database_scanner_with_shared_engine


@pytest.fixture
def sample_documents():
    """Provide sample documents for vector store testing."""
    return [
        "This is a test document about databases.",
        "Another document about SQL queries and tables.",
        "Information about foreign keys and relationships.",
        "Data about users, products, and categories."
    ]


# Mark configuration for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers",
                            "requires_openai: Tests requiring OpenAI API")
    config.addinivalue_line("markers",
                            "requires_database: Tests requiring database "
                            "connection")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark tests based on directory structure
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)

        # Mark tests that require external services
        if "openai" in item.name.lower() or "rag" in item.name.lower():
            item.add_marker(pytest.mark.requires_openai)
        if "database" in item.name.lower() or "scanner" in item.name.lower():
            item.add_marker(pytest.mark.requires_database)
