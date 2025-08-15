"""Unit tests for database scanner functionality."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from database_scanner import DatabaseScanner
from config import DatabaseConfig


class TestDatabaseScanner:
    """Test cases for DatabaseScanner class."""

    def test_get_table_names(self, in_memory_database):
        """Test getting list of table names."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        table_names = scanner.get_table_names()
        assert isinstance(table_names, list)
        assert "users" in table_names
        assert "posts" in table_names

    def test_private_sanitize_table_name_valid(self, in_memory_database):
        """Test private sanitization method with valid table names."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        # Test with existing table
        result = scanner._sanitize_table_name("users")
        assert result == "users"

    def test_private_sanitize_table_name_invalid_empty(self, in_memory_database):
        """Test private sanitization method with empty names."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        with pytest.raises(ValueError, match="Table name must be a non-empty string"):
            scanner._sanitize_table_name("")

        with pytest.raises(ValueError, match="Table name must be a non-empty string"):
            scanner._sanitize_table_name("   ")

    def test_private_sanitize_table_name_invalid_none(self, in_memory_database):
        """Test private sanitization method with None."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        with pytest.raises(ValueError, match="Table name must be a non-empty string"):
            scanner._sanitize_table_name(None)

    def test_private_sanitize_table_name_nonexistent(self, in_memory_database):
        """Test private sanitization method with non-existent table."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        with pytest.raises(ValueError, match="Invalid table"):
            scanner._sanitize_table_name("nonexistent_table")

    def test_query_table_sample_valid(self, in_memory_database):
        """Test querying sample data from valid table."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        result = scanner.query_table_sample("users", limit=2)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 2
        assert len(result) > 0
        
        # Check columns exist
        assert "id" in result.columns
        assert "name" in result.columns

    def test_query_table_sample_invalid_limit(self, in_memory_database):
        """Test querying with invalid limit."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            scanner.query_table_sample("users", limit=0)
        
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            scanner.query_table_sample("users", limit=-1)

    def test_query_table_sample_invalid_table(self, in_memory_database):
        """Test querying non-existent table."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        with pytest.raises(ValueError, match="Invalid table"):
            scanner.query_table_sample("nonexistent", limit=10)

    def test_get_table_stats(self, in_memory_database):
        """Test getting table statistics."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        stats = scanner.get_table_stats("users")
        assert isinstance(stats, dict)
        assert "row_count" in stats

    def test_scan_database(self, in_memory_database):
        """Test scanning complete database schema."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        schema = scanner.scan_database()
        assert hasattr(schema, 'tables')
        assert len(schema.tables) > 0
        
        # Check if users table is in the schema
        table_names = [table.name for table in schema.tables]
        assert "users" in table_names

    def test_refresh_schema(self, in_memory_database):
        """Test schema refresh functionality."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        # Get initial table names
        initial_tables = scanner.get_table_names()
        
        # Refresh schema
        scanner.refresh_schema()
        
        # Get tables again
        refreshed_tables = scanner.get_table_names()
        
        # Should be the same since we didn't change the schema
        assert initial_tables == refreshed_tables

    @pytest.mark.performance
    def test_table_name_caching(self, in_memory_database):
        """Test that table names are cached for performance."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        # First call should populate cache
        tables1 = scanner.get_table_names()
        
        # Second call should use cache
        tables2 = scanner.get_table_names()
        
        assert tables1 == tables2
        assert scanner._cached_table_names is not None

    @pytest.mark.performance
    def test_cache_invalidation(self, in_memory_database):
        """Test cache invalidation."""
        config, engine = in_memory_database
        scanner = DatabaseScanner(config)
        
        # Populate cache
        scanner.get_table_names()
        assert scanner._cached_table_names is not None
        
        # Invalidate cache
        scanner._invalidate_table_cache()
        assert scanner._cached_table_names is None

    def test_error_handling_connection_failure(self):
        """Test error handling for connection failures."""
        config = DatabaseConfig(url="sqlite:///nonexistent.db")
        
        with pytest.raises(RuntimeError):
            scanner = DatabaseScanner(config)
            # This should fail when trying to get table names
            scanner.get_table_names()
