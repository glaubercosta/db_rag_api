"""Unit tests for database scanner functionality."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from database_scanner import DatabaseScanner
from config import DatabaseConfig


class TestDatabaseScanner:
    """Test cases for DatabaseScanner class."""

    def test_get_table_names(self, database_scanner_with_shared_engine):
        """Test getting list of table names."""
        scanner = database_scanner_with_shared_engine
        
        table_names = scanner.get_table_names()
        assert isinstance(table_names, list)
        assert "users" in table_names
        assert "posts" in table_names

    def test_private_sanitize_table_name_valid(self, database_scanner_with_shared_engine):
        """Test private sanitization method with valid table names."""
        scanner = database_scanner_with_shared_engine
        
        # Test with existing table
        result = scanner._sanitize_table_name("users")
        assert result == "users"

    def test_private_sanitize_table_name_invalid_empty(self, database_scanner_with_shared_engine):
        """Test private sanitization method with empty names."""
        scanner = database_scanner_with_shared_engine
        
        with pytest.raises(ValueError, match="Table name must be a non-empty string"):
            scanner._sanitize_table_name("")

        with pytest.raises(ValueError, match="Table name must be a non-empty string"):
            scanner._sanitize_table_name("   ")

    def test_private_sanitize_table_name_invalid_none(self, database_scanner_with_shared_engine):
        """Test private sanitization method with None."""
        scanner = database_scanner_with_shared_engine
        
        with pytest.raises(ValueError, match="Table name must be a non-empty string"):
            scanner._sanitize_table_name(None)

    def test_private_sanitize_table_name_nonexistent(self, database_scanner_with_shared_engine):
        """Test private sanitization method with non-existent table."""
        scanner = database_scanner_with_shared_engine
        
        with pytest.raises(ValueError, match="Invalid table"):
            scanner._sanitize_table_name("nonexistent_table")

    def test_query_table_sample_valid(self, database_scanner_with_shared_engine):
        """Test querying sample data from valid table."""
        scanner = database_scanner_with_shared_engine
        
        result = scanner.query_table_sample("users", limit=2)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 2
        assert len(result) > 0
        
        # Check columns exist
        assert "id" in result.columns
        assert "name" in result.columns

    def test_query_table_sample_invalid_limit(self, database_scanner_with_shared_engine):
        """Test querying with invalid limit."""
        scanner = database_scanner_with_shared_engine
        
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            scanner.query_table_sample("users", limit=0)
        
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            scanner.query_table_sample("users", limit=-1)

    def test_query_table_sample_invalid_table(self, database_scanner_with_shared_engine):
        """Test querying non-existent table."""
        scanner = database_scanner_with_shared_engine
        
        with pytest.raises(ValueError, match="Invalid table"):
            scanner.query_table_sample("nonexistent", limit=10)

    def test_get_table_stats(self, database_scanner_with_shared_engine):
        """Test getting table statistics."""
        scanner = database_scanner_with_shared_engine
        
        stats = scanner.get_table_stats("users")
        assert isinstance(stats, dict)
        assert "row_count" in stats

    def test_scan_database(self, database_scanner_with_shared_engine):
        """Test scanning complete database schema."""
        scanner = database_scanner_with_shared_engine
        
        schema = scanner.scan_database()
        assert hasattr(schema, 'tables')
        assert len(schema.tables) > 0
        
        # Check if users table is in the schema
        table_names = [table.name for table in schema.tables]
        assert "users" in table_names

    def test_refresh_schema(self, database_scanner_with_shared_engine):
        """Test schema refresh functionality."""
        scanner = database_scanner_with_shared_engine
        
        # Get initial table names
        initial_tables = scanner.get_table_names()
        
        # Refresh schema
        scanner.refresh_schema()
        
        # Get tables again
        refreshed_tables = scanner.get_table_names()
        
        # Should be the same since we didn't change the schema
        assert initial_tables == refreshed_tables

    @pytest.mark.performance
    def test_table_name_caching(self, database_scanner_with_shared_engine):
        """Test that table names are cached for performance."""
        scanner = database_scanner_with_shared_engine
        
        # First call should populate cache
        tables1 = scanner.get_table_names()
        
        # Second call should use cache
        tables2 = scanner.get_table_names()
        
        assert tables1 == tables2
        assert scanner._cached_table_names is not None

    @pytest.mark.performance
    def test_cache_invalidation(self, database_scanner_with_shared_engine):
        """Test cache invalidation."""
        scanner = database_scanner_with_shared_engine
        
        # Populate cache
        scanner.get_table_names()
        assert scanner._cached_table_names is not None
        
        # Invalidate cache
        scanner._invalidate_table_cache()
        assert scanner._cached_table_names is None

    def test_error_handling_connection_failure(self):
        """Test error handling for connection failures."""
        # Use an invalid URL format that will definitely fail
        config = DatabaseConfig(url="invalid://invalid.db")
        
        with pytest.raises(Exception):  # Could be RuntimeError or other SQLAlchemy error
            scanner = DatabaseScanner(config)
            # This should fail when trying to get table names
            scanner.get_table_names()
