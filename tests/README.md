# Testing Guide

## 📋 Overview

This project uses a comprehensive testing strategy with organized test structure following best practices for maintainability and scalability.

## 🏗️ Test Structure

```
tests/
├── conftest.py                 # Global test configuration and fixtures
├── unit/                       # Unit tests
│   ├── test_database_scanner.py
│   └── test_config.py
├── integration/                # Integration tests
│   └── test_rag_system.py
├── security/                   # Security tests
│   └── test_sql_injection.py
├── performance/                # Performance tests
│   └── test_database_performance.py
├── fixtures/                   # Test data and fixtures
├── utils/                      # Test utilities and helpers
│   └── test_helpers.py
└── legacy/                     # Old test files (backup)
```

## 🏷️ Test Categories

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Fast execution
- Mock external dependencies
- **Marker**: `@pytest.mark.unit`

### Integration Tests (`tests/integration/`)
- Test component interactions
- End-to-end functionality
- Real database connections (when needed)
- **Marker**: `@pytest.mark.integration`

### Security Tests (`tests/security/`)
- SQL injection protection
- Input validation
- Data security measures
- **Marker**: `@pytest.mark.security`

### Performance Tests (`tests/performance/`)
- Caching efficiency
- Query performance
- Memory usage
- **Marker**: `@pytest.mark.performance` and `@pytest.mark.slow`

## 🚀 Running Tests

### Windows (PowerShell)

```powershell
# Install dependencies
.\run-tests.ps1 install-deps

# Run all tests
.\run-tests.ps1 test

# Run specific categories
.\run-tests.ps1 test-unit
.\run-tests.ps1 test-integration
.\run-tests.ps1 test-security
.\run-tests.ps1 test-performance

# Run fast tests only (exclude slow)
.\run-tests.ps1 test-fast

# Run with coverage
.\run-tests.ps1 test-coverage

# Run specific file
.\run-tests.ps1 test-file -File "tests\unit\test_database_scanner.py"

# Run tests matching pattern
.\run-tests.ps1 test-pattern -Pattern "sql_injection"

# Clean artifacts
.\run-tests.ps1 clean
```

### Linux/Mac (Make)

```bash
# Install dependencies
make -f Makefile.tests install-test-deps

# Run all tests
make -f Makefile.tests test

# Run specific categories
make -f Makefile.tests test-unit
make -f Makefile.tests test-integration
make -f Makefile.tests test-security
make -f Makefile.tests test-performance

# Run with coverage
make -f Makefile.tests test-coverage

# Run specific file
make -f Makefile.tests test-file FILE=tests/unit/test_database_scanner.py

# Run tests matching pattern
make -f Makefile.tests test-pattern PATTERN=sql_injection
```

### Direct pytest Commands

```bash
# Run all tests
pytest tests/ -v

# Run by marker
pytest -m unit -v
pytest -m integration -v
pytest -m security -v
pytest -m "performance and slow" -v

# Run without slow tests
pytest -m "not slow" -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/unit/test_database_scanner.py::TestDatabaseScanner::test_sanitize_table_name_valid -v
```

## 🎯 Test Markers

- `unit`: Unit tests
- `integration`: Integration tests
- `security`: Security tests
- `performance`: Performance tests
- `slow`: Slow running tests
- `requires_openai`: Tests requiring OpenAI API
- `requires_database`: Tests requiring database connection

## 🧪 Fixtures

### Global Fixtures (conftest.py)
- `temp_directory`: Temporary directory for test files
- `test_database_config`: Test database configuration
- `test_openai_config`: Test OpenAI configuration
- `test_rag_config`: Test RAG configuration
- `mock_openai_client`: Mocked OpenAI client
- `in_memory_database`: In-memory SQLite database with test data
- `database_scanner`: Configured database scanner instance
- `sample_documents`: Sample documents for vector store testing

## 📊 Coverage Reports

Coverage reports are generated in multiple formats:
- **HTML**: `htmlcov/index.html` (interactive report)
- **Terminal**: Summary in terminal output
- **XML**: `coverage.xml` (for CI/CD integration)

## 🔧 Configuration

### pytest.ini
- Test discovery patterns
- Marker definitions
- Coverage settings
- Warning filters

### Test Environment Variables
- `OPENAI_API_KEY`: For tests requiring OpenAI API
- `SKIP_DB_TESTS`: Skip database-dependent tests
- `TEST_DB_URL`: Override test database URL

## 🛡️ Security Testing

Security tests cover:
- SQL injection protection
- Input sanitization
- Path traversal prevention
- Checksum validation
- Malicious file protection

## ⚡ Performance Testing

Performance tests verify:
- Caching effectiveness
- Query response times
- Memory usage stability
- Concurrent access safety
- Scalability under load

## 📋 Best Practices

### Writing Tests
1. Use descriptive test names
2. Follow AAA pattern (Arrange, Act, Assert)
3. Test one thing per test
4. Use appropriate markers
5. Mock external dependencies
6. Clean up resources

### Test Data
1. Use fixtures for reusable test data
2. Create isolated test environments
3. Clean up after tests
4. Use parametrized tests for multiple scenarios

### Assertions
1. Use specific assertions
2. Include helpful error messages
3. Test both positive and negative cases
4. Verify edge cases

## 🔄 Continuous Integration

For CI/CD pipelines:
```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest tests/ --cov=. --cov-report=xml
```

## 📈 Quality Metrics

Maintain:
- **Coverage**: >90% for core modules
- **Performance**: Unit tests <100ms, Integration tests <5s
- **Security**: All injection attempts blocked
- **Reliability**: Tests pass consistently

## 🆘 Troubleshooting

### Common Issues
1. **Import errors**: Check PYTHONPATH and module structure
2. **Database errors**: Ensure test database is available
3. **OpenAI errors**: Check API key and mocks
4. **Permission errors**: Check file permissions on Windows
5. **Slow tests**: Use markers to separate fast/slow tests

### Debugging
```bash
# Run with verbose output
pytest -v -s

# Run specific test with debugging
pytest tests/unit/test_database_scanner.py::test_specific -v -s --pdb

# Show test coverage gaps
pytest --cov=. --cov-report=term-missing
```

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Python testing best practices](https://docs.python-guide.org/writing/tests/)

---

This testing framework provides a solid foundation for maintaining code quality and preventing regressions as the project evolves.
