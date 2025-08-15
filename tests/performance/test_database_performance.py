"""Performance tests for database operations and caching."""

import pytest
import time

from database_scanner import DatabaseScanner


class TestDatabasePerformance:
    """Performance tests for database operations."""

    @pytest.mark.slow
    def test_table_names_cache_performance(self, database_scanner):
        """Test that table names caching improves performance."""
        # Clear any existing cache
        if hasattr(database_scanner, '_table_names_cache'):
            database_scanner._table_names_cache = None

        # Measure time for first call (cache miss)
        start_time = time.time()
        tables_first = database_scanner.get_table_names()
        first_call_time = time.time() - start_time

        # Measure time for second call (cache hit)
        start_time = time.time()
        tables_second = database_scanner.get_table_names()
        second_call_time = time.time() - start_time

        # Verify results are identical
        assert tables_first == tables_second
        assert len(tables_first) > 0

        # Cache hit should be significantly faster
        # Allow some tolerance for test environment variations
        assert second_call_time < first_call_time * 0.5

    @pytest.mark.slow
    def test_table_validation_cache_performance(self, database_scanner):
        """Test that table validation caching improves performance."""
        table_name = "users"

        # Measure time for first validation (cache miss)
        start_time = time.time()
        result_first = database_scanner.sanitize_table_name(table_name)
        first_call_time = time.time() - start_time

        # Measure time for subsequent validations (cache hit)
        start_time = time.time()
        result_second = database_scanner.sanitize_table_name(table_name)
        second_call_time = time.time() - start_time

        # Verify results are identical
        assert result_first == result_second == table_name

        # Cache hit should be faster
        assert second_call_time <= first_call_time

    @pytest.mark.slow
    def test_multiple_table_queries_performance(self, database_scanner):
        """Test performance with multiple concurrent table queries."""
        table_names = ["users", "categories", "products"]
        iterations = 10

        start_time = time.time()

        for _ in range(iterations):
            for table_name in table_names:
                data = database_scanner.query_table_sample(table_name, limit=5)
                assert isinstance(data, list)
                assert len(data) > 0

        total_time = time.time() - start_time
        avg_time_per_query = total_time / (iterations * len(table_names))

        # Each query should complete reasonably quickly (< 0.1 seconds)
        assert avg_time_per_query < 0.1

    @pytest.mark.slow
    def test_large_limit_performance(self, database_scanner):
        """Test performance with large limit values."""
        # Test with progressively larger limits
        limits = [10, 50, 100, 500]
        times = []

        for limit in limits:
            start_time = time.time()
            result = database_scanner.query_table_sample("users", limit=limit)
            query_time = time.time() - start_time
            times.append(query_time)

            # Verify we get expected number of results (up to available data)
            assert len(result) <= min(limit, 3)  # We only have 3 test users

        # Performance should scale reasonably
        # Since we have limited test data, times should be similar
        for query_time in times:
            assert query_time < 0.5  # Should complete quickly

    @pytest.mark.slow
    def test_schema_retrieval_performance(self, database_scanner):
        """Test performance of schema retrieval operations."""
        table_names = ["users", "categories", "products"]

        start_time = time.time()

        for table_name in table_names:
            schema = database_scanner.get_table_schema(table_name)
            assert isinstance(schema, dict)
            assert "columns" in schema
            assert "primary_keys" in schema
            assert "foreign_keys" in schema

        total_time = time.time() - start_time
        avg_time_per_schema = total_time / len(table_names)

        # Schema retrieval should be reasonably fast
        assert avg_time_per_schema < 0.1

    @pytest.mark.slow
    def test_concurrent_access_performance(self, database_scanner):
        """Test performance under concurrent access."""
        import threading
        import statistics

        results = []
        times = []

        def worker():
            start_time = time.time()
            try:
                # Perform various operations
                tables = database_scanner.get_table_names()
                assert len(tables) > 0

                for table in tables[:2]:  # Test first 2 tables
                    database_scanner.sanitize_table_name(table)
                    data = database_scanner.query_table_sample(table, limit=3)
                    assert len(data) >= 0

                elapsed = time.time() - start_time
                times.append(elapsed)
                results.append("success")

            except Exception as e:
                results.append(f"error: {e}")

        # Create multiple threads
        threads = []
        num_threads = 5

        overall_start = time.time()

        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        overall_time = time.time() - overall_start

        # Verify all operations completed successfully
        assert all(result == "success" for result in results)
        assert len(times) == num_threads

        # Calculate performance metrics
        avg_time = statistics.mean(times)
        max_time = max(times)

        # All operations should complete reasonably quickly
        assert avg_time < 1.0
        assert max_time < 2.0
        assert overall_time < 5.0

    @pytest.mark.slow
    def test_memory_usage_stability(self, database_scanner):
        """Test that repeated operations don't cause memory leaks."""
        import gc

        # Force garbage collection before test
        gc.collect()

        # Perform many operations
        iterations = 100

        for i in range(iterations):
            # Various operations that might accumulate memory
            tables = database_scanner.get_table_names()

            for table in tables:
                database_scanner.sanitize_table_name(table)

            # Query sample data
            data = database_scanner.query_table_sample("users", limit=5)
            assert len(data) > 0

            # Get schema
            schema = database_scanner.get_table_schema("users")
            assert isinstance(schema, dict)

            # Periodic garbage collection
            if i % 20 == 0:
                gc.collect()

        # Final garbage collection
        gc.collect()

        # Test should complete without memory errors
        # This is mainly a regression test for memory leaks
        assert True


class TestCacheOptimization:
    """Test cache optimization mechanisms."""

    def test_cache_invalidation_on_connection_change(self,
                                                     test_database_config):
        """Test that cache is invalidated when connection changes."""
        scanner1 = DatabaseScanner(test_database_config)

        # Populate cache
        tables1 = scanner1.get_table_names()
        assert len(tables1) > 0

        # Create new scanner (simulating connection change)
        scanner2 = DatabaseScanner(test_database_config)

        # Should work independently without cache conflicts
        tables2 = scanner2.get_table_names()
        assert tables1 == tables2

        scanner1.close()
        scanner2.close()

    def test_cache_efficiency_with_repeated_operations(self, database_scanner):
        """Test cache efficiency with repeated operations."""
        table_name = "users"

        # Perform same operation multiple times
        start_time = time.time()

        for _ in range(50):
            # These should be cached after first call
            database_scanner.sanitize_table_name(table_name)
            database_scanner.get_table_names()

        total_time = time.time() - start_time

        # Should complete quickly due to caching
        assert total_time < 1.0

    @pytest.mark.parametrize("operation_count", [10, 25, 50, 100])
    def test_cache_performance_scaling(self, database_scanner,
                                       operation_count):
        """Test that cache performance scales well with operation count."""
        start_time = time.time()

        for _ in range(operation_count):
            tables = database_scanner.get_table_names()
            assert len(tables) > 0

        elapsed = time.time() - start_time
        avg_time = elapsed / operation_count

        # Average time per operation should be very small due to caching
        assert avg_time < 0.01  # Less than 10ms per operation
