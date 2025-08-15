"""Security tests for SQL injection protection."""

import pytest
from unittest.mock import patch
import os

from vector_store_manager import VectorStoreManager


class TestSQLInjectionProtection:
    """Test SQL injection protection mechanisms."""

    def test_sql_injection_attempts_blocked(self, database_scanner):
        """Test that common SQL injection attempts are blocked."""
        malicious_inputs = [
            "users; DROP TABLE users;",
            "users' OR '1'='1",
            "users UNION SELECT * FROM users",
            "users'; DELETE FROM users; --",
            "users/**/OR/**/1=1",
            "users\n; DROP TABLE users;",
            "users; INSERT INTO users VALUES (999, 'hacker', 'evil@hacker.com', 0);",  # noqa: E501
            "users WHERE 1=1; UPDATE users SET name='hacked'",
        ]

        for malicious_input in malicious_inputs:
            with pytest.raises(ValueError, match="Invalid table name"):
                database_scanner.sanitize_table_name(malicious_input)

    def test_sql_comments_blocked(self, database_scanner):
        """Test that SQL comments in table names are blocked."""
        comment_attempts = [
            "users--comment",
            "users/*comment*/",
            "users#comment",
            "users;--comment",
            "users/*evil comment*/more_sql"
        ]

        for attempt in comment_attempts:
            with pytest.raises(ValueError, match="Invalid table name"):
                database_scanner.sanitize_table_name(attempt)

    def test_whitespace_injection_blocked(self, database_scanner):
        """Test that whitespace-based injection attempts are blocked."""
        whitespace_attempts = [
            "users\tDROP TABLE",
            "users\nDROP TABLE",
            "users\rDROP TABLE",
            "users\x00DROP",
            "users\x0bDROP"
        ]

        for attempt in whitespace_attempts:
            with pytest.raises(ValueError, match="Invalid table name"):
                database_scanner.sanitize_table_name(attempt)

    def test_case_insensitive_keywords_blocked(self, database_scanner):
        """Test that SQL keywords are blocked regardless of case."""
        keyword_attempts = [
            "users; drop table",
            "users; DROP TABLE",
            "users; DrOp TaBlE",
            "users; DELETE from",
            "users; insert INTO",
            "users; UPDATE set",
            "users; SELECT from"
        ]

        for attempt in keyword_attempts:
            with pytest.raises(ValueError, match="Invalid table name"):
                database_scanner.sanitize_table_name(attempt)

    def test_encoded_injection_blocked(self, database_scanner):
        """Test that URL-encoded injection attempts are blocked."""
        encoded_attempts = [
            "users%3BDROP%20TABLE",  # URL encoded ';DROP TABLE'
            "users%27OR%271%27%3D%271",  # URL encoded 'OR'1'='1
            "users%2F%2A%2A%2FOR%2F%2A%2A%2F1%3D1"  # /**/OR/**/1=1
        ]

        # Note: Our current implementation doesn't decode URLs
        # but we should test if such inputs would be rejected
        for attempt in encoded_attempts:
            # These should be rejected due to invalid characters
            with pytest.raises(ValueError, match="Invalid table name"):
                database_scanner.sanitize_table_name(attempt)

    def test_valid_table_names_allowed(self, database_scanner):
        """Test that legitimate table names are allowed."""
        valid_names = [
            "users",
            "user_profiles",
            "UserData",
            "table123",
            "products",
            "categories"
        ]

        for name in valid_names:
            # These should not raise exceptions
            result = database_scanner.sanitize_table_name(name)
            assert result == name

    def test_data_integrity_maintained(self, database_scanner):
        """Test that legitimate queries don't affect data integrity."""
        # Get initial data
        initial_users = database_scanner.query_table_sample("users")
        initial_count = len(initial_users)

        # Perform legitimate operations
        legitimate_queries = ["users", "categories", "products"]

        for table_name in legitimate_queries:
            data = database_scanner.query_table_sample(table_name, limit=5)
            assert isinstance(data, list)

        # Verify data integrity maintained
        final_users = database_scanner.query_table_sample("users")
        assert len(final_users) == initial_count

        # Verify specific data hasn't changed
        for initial_user, final_user in zip(initial_users, final_users):
            assert initial_user == final_user

    def test_concurrent_safety(self, database_scanner):
        """Test that security measures work under concurrent access."""
        import threading

        results = []
        errors = []

        def worker(table_name):
            try:
                result = database_scanner.query_table_sample(table_name)
                results.append(result)
            except Exception as e:
                errors.append(e)

        def malicious_worker(malicious_input):
            try:
                database_scanner.sanitize_table_name(malicious_input)
                # Should not reach here
                results.append("SECURITY_BREACH")
            except ValueError:
                # Expected - security working correctly
                pass
            except Exception as e:
                errors.append(e)

        # Create threads for legitimate and malicious requests
        threads = []

        # Legitimate threads
        for _ in range(5):
            t = threading.Thread(target=worker, args=("users",))
            threads.append(t)

        # Malicious threads
        malicious_inputs = [
            "users; DROP TABLE users",
            "users' OR 1=1",
            "users UNION SELECT * FROM users"
        ]

        for malicious_input in malicious_inputs:
            t = threading.Thread(target=malicious_worker,
                                 args=(malicious_input,))
            threads.append(t)

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no security breaches occurred
        assert "SECURITY_BREACH" not in results
        # Should have 5 successful legitimate results
        assert len([r for r in results if isinstance(r, list)]) == 5


class TestVectorStoreSecurityProtection:
    """Test vector store security protections."""

    def test_checksum_validation(self, test_rag_config, sample_documents):
        """Test that checksum validation protects against tampering."""
        with patch('openai.OpenAI'):
            manager = VectorStoreManager(test_rag_config)

            # Create legitimate vector store
            manager.create_vector_store(sample_documents)

            # Verify checksum file exists
            checksum_file = test_rag_config.vector_store_path + "_checksum.txt"
            assert os.path.exists(checksum_file)

            # Tamper with the checksum file
            with open(checksum_file, 'w') as f:
                f.write("tampered_checksum")

            # Loading should fail due to invalid checksum
            with pytest.raises(ValueError, match="Security validation failed"):
                manager.load_vector_store()

    def test_malicious_file_protection(self, test_rag_config):
        """Test protection against malicious pickle files."""
        with patch('openai.OpenAI'):
            manager = VectorStoreManager(test_rag_config)

            # Create a malicious pickle file
            malicious_content = b"malicious_pickle_content"
            os.makedirs(os.path.dirname(test_rag_config.vector_store_path),
                        exist_ok=True)

            with open(test_rag_config.vector_store_path, 'wb') as f:
                f.write(malicious_content)

            # Loading should fail
            with pytest.raises(Exception):
                manager.load_vector_store()

    def test_path_traversal_protection(self, temp_directory):
        """Test protection against path traversal attacks."""
        from config import RAGConfig

        # Attempt path traversal in vector store path
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "../malicious_dir/vectors"
        ]

        for malicious_path in malicious_paths:
            config = RAGConfig(
                similarity_search_k=3,
                table_sample_limit=5,
                vector_store_path=malicious_path
            )

            with patch('openai.OpenAI'):
                manager = VectorStoreManager(config)

                # Should not be able to create vector store outside temp dir
                with pytest.raises(Exception):
                    manager.create_vector_store(["test document"])

    @pytest.mark.parametrize("dangerous_filename", [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "/root/.ssh/id_rsa",
        "C:\\Users\\Administrator\\Documents\\secret.txt"
    ])
    def test_filename_sanitization(self, dangerous_filename, temp_directory):
        """Test that dangerous filenames are rejected."""
        from config import RAGConfig

        config = RAGConfig(
            similarity_search_k=3,
            table_sample_limit=5,
            vector_store_path=dangerous_filename
        )

        with patch('openai.OpenAI'):
            manager = VectorStoreManager(config)

            # Should reject dangerous paths
            with pytest.raises(Exception):
                manager.create_vector_store(["test"])
