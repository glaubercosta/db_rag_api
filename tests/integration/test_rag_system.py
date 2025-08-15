"""Integration tests for the complete RAG system."""

import pytest
from unittest.mock import patch

from rag_system import DatabaseRAGSystem


class TestRAGSystemIntegration:
    """Integration tests for the complete RAG system."""

    @pytest.mark.integration
    def test_rag_system_initialization(self, test_database_config,
                                       test_openai_config, test_rag_config):
        """Test that RAG system initializes correctly."""
        with patch('openai.OpenAI'):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            assert rag_system.db_scanner is not None
            assert rag_system.vector_manager is not None
            assert rag_system.sql_agent is not None

    @pytest.mark.integration
    @pytest.mark.requires_openai
    def test_end_to_end_query_processing(self, test_database_config,
                                         test_openai_config, test_rag_config,
                                         mock_openai_client):
        """Test end-to-end query processing."""
        with patch('openai.OpenAI', return_value=mock_openai_client):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Test natural language query
            question = "How many users are in the database?"
            
            # Mock the response to return a valid SQL query
            mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "SELECT COUNT(*) FROM users;"  # noqa: E501

            result = rag_system.query(question)

            assert result is not None
            assert isinstance(result, dict)
            assert "sql_query" in result
            assert "result" in result

    @pytest.mark.integration
    def test_database_scanning_integration(self, test_database_config,
                                          test_openai_config, test_rag_config):
        """Test database scanning integration."""
        with patch('openai.OpenAI'):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Test database scanning
            tables = rag_system.db_scanner.get_table_names()
            assert len(tables) >= 3
            assert "users" in tables
            assert "categories" in tables
            assert "products" in tables

            # Test schema retrieval
            for table in tables:
                schema = rag_system.db_scanner.get_table_schema(table)
                assert isinstance(schema, dict)
                assert "columns" in schema

    @pytest.mark.integration
    def test_vector_store_integration(self, test_database_config,
                                     test_openai_config, test_rag_config,
                                     sample_documents):
        """Test vector store integration."""
        with patch('openai.OpenAI') as mock_openai:
            # Setup mock
            mock_client = mock_openai.return_value
            mock_client.embeddings.create.return_value.data = [
                type('obj', (object,), {'embedding': [0.1] * 1536})()
                for _ in sample_documents
            ]

            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Create vector store
            rag_system.vector_manager.create_vector_store(sample_documents)

            # Test similarity search
            query = "database information"
            results = rag_system.vector_manager.similarity_search(query, k=2)

            assert isinstance(results, list)
            assert len(results) <= 2

    @pytest.mark.integration
    def test_sql_agent_integration(self, test_database_config,
                                  test_openai_config, test_rag_config,
                                  mock_openai_client):
        """Test SQL agent integration."""
        with patch('openai.OpenAI', return_value=mock_openai_client):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Test SQL generation
            question = "What are the names of all users?"
            context = "Database contains users table with name column"

            # Mock response
            mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "SELECT name FROM users;"  # noqa: E501

            sql_query = rag_system.sql_agent.generate_sql(question, context)

            assert isinstance(sql_query, str)
            assert "SELECT" in sql_query.upper()
            assert "users" in sql_query

    @pytest.mark.integration
    def test_security_integration(self, test_database_config,
                                 test_openai_config, test_rag_config):
        """Test security measures integration."""
        with patch('openai.OpenAI'):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Test SQL injection protection
            malicious_inputs = [
                "users; DROP TABLE users;",
                "users' OR '1'='1",
                "users UNION SELECT password FROM users"
            ]

            for malicious_input in malicious_inputs:
                with pytest.raises(ValueError):
                    rag_system.db_scanner.sanitize_table_name(malicious_input)

    @pytest.mark.integration
    def test_error_handling_integration(self, test_database_config,
                                       test_openai_config, test_rag_config,
                                       mock_openai_client):
        """Test error handling across components."""
        with patch('openai.OpenAI', return_value=mock_openai_client):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Test invalid table name handling
            with pytest.raises(ValueError):
                rag_system.db_scanner.query_table_sample("nonexistent_table")

            # Test invalid SQL handling
            mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "INVALID SQL QUERY"  # noqa: E501

            with pytest.raises(Exception):
                rag_system.query("invalid question")

    @pytest.mark.integration
    def test_configuration_integration(self, test_database_config,
                                      test_openai_config, test_rag_config):
        """Test configuration handling across components."""
        with patch('openai.OpenAI'):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Verify configurations are properly passed
            assert rag_system.db_scanner.config == test_database_config
            assert rag_system.rag_config == test_rag_config

            # Test configuration limits
            data = rag_system.db_scanner.query_table_sample(
                "users",
                limit=test_rag_config.table_sample_limit
            )
            assert len(data) <= test_rag_config.table_sample_limit

    @pytest.mark.integration
    @pytest.mark.slow
    def test_performance_integration(self, test_database_config,
                                    test_openai_config, test_rag_config):
        """Test performance across integrated components."""
        import time

        with patch('openai.OpenAI'):
            start_time = time.time()

            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            initialization_time = time.time() - start_time

            # Initialization should be reasonably fast
            assert initialization_time < 5.0

            # Test multiple operations
            start_time = time.time()

            for _ in range(10):
                tables = rag_system.db_scanner.get_table_names()
                assert len(tables) > 0

                for table in tables[:2]:  # Test first 2 tables
                    rag_system.db_scanner.sanitize_table_name(table)
                    data = rag_system.db_scanner.query_table_sample(
                        table, limit=3
                    )
                    assert isinstance(data, list)

            operations_time = time.time() - start_time

            # Operations should complete quickly
            assert operations_time < 2.0

    @pytest.mark.integration
    def test_cleanup_integration(self, test_database_config,
                                test_openai_config, test_rag_config):
        """Test proper cleanup of resources."""
        with patch('openai.OpenAI'):
            rag_system = DatabaseRAGSystem(
                db_config=test_database_config,
                openai_config=test_openai_config,
                rag_config=test_rag_config
            )

            # Use the system
            tables = rag_system.db_scanner.get_table_names()
            assert len(tables) > 0

            # Test cleanup
            rag_system.close()

            # Verify database scanner is closed
            assert rag_system.db_scanner.engine is None or \
                   rag_system.db_scanner.engine.pool.status() == 'disposed'
