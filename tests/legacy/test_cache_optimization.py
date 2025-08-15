"""
Test para verificar a otimização de cache em DatabaseScanner
"""
import time
import pytest
from unittest.mock import Mock, patch
from database_scanner import DatabaseScanner
from config import DatabaseConfig


def test_table_names_cache_optimization():
    """Test que verifica se o cache de table names reduz chamadas redundantes"""
    
    # Mock config
    config = DatabaseConfig(
        url="postgresql://test:test@localhost:5432/test"
    )
    
    with patch('database_scanner.create_engine') as mock_engine, \
         patch('database_scanner.inspect') as mock_inspect:
        
        # Mock inspector
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = [
            'users', 'orders', 'products', 'categories', 'order_items'
        ]
        mock_inspect.return_value = mock_inspector
        
        # Create scanner
        scanner = DatabaseScanner(config)
        
        # Call get_table_names multiple times
        tables1 = scanner.get_table_names()
        tables2 = scanner.get_table_names()
        tables3 = scanner.get_table_names()
        
        # Should be the same result
        assert tables1 == tables2 == tables3
        assert len(tables1) == 5
        
        # Inspector should only be called once (during first call)
        assert mock_inspector.get_table_names.call_count == 1
        
        print("✅ Cache funcionando: inspector.get_table_names() chamado apenas 1 vez")


def test_sanitize_table_name_cache_efficiency():
    """Test que verifica eficiência do cache em múltiplas validações"""
    
    config = DatabaseConfig(
        url="postgresql://test:test@localhost:5432/test"
    )
    
    with patch('database_scanner.create_engine') as mock_engine, \
         patch('database_scanner.inspect') as mock_inspect:
        
        # Mock inspector
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = [
            'users', 'orders', 'products'
        ]
        mock_inspect.return_value = mock_inspector
        
        scanner = DatabaseScanner(config)
        
        # Multiple table validations
        start_time = time.time()
        
        valid_table1 = scanner._sanitize_table_name('users')
        valid_table2 = scanner._sanitize_table_name('orders')
        valid_table3 = scanner._sanitize_table_name('products')
        valid_table4 = scanner._sanitize_table_name('users')  # Repeat
        
        elapsed_time = time.time() - start_time
        
        # All should be valid
        assert valid_table1 == 'users'
        assert valid_table2 == 'orders'
        assert valid_table3 == 'products'
        assert valid_table4 == 'users'
        
        # Inspector should be called only once despite 4 validations
        assert mock_inspector.get_table_names.call_count == 1
        
        print(f"✅ 4 validações executadas em {elapsed_time:.4f}s com apenas 1 chamada ao inspector")


def test_cache_invalidation():
    """Test que verifica invalidação e refresh do cache"""
    
    config = DatabaseConfig(
        url="postgresql://test:test@localhost:5432/test"
    )
    
    with patch('database_scanner.create_engine') as mock_engine, \
         patch('database_scanner.inspect') as mock_inspect:
        
        # Mock inspector with changing results
        mock_inspector = Mock()
        mock_inspector.get_table_names.side_effect = [
            ['users', 'orders'],           # First call
            ['users', 'orders', 'products']  # After refresh
        ]
        mock_inspect.return_value = mock_inspector
        
        scanner = DatabaseScanner(config)
        
        # First call - should cache result
        tables1 = scanner.get_table_names()
        assert len(tables1) == 2
        assert mock_inspector.get_table_names.call_count == 1
        
        # Second call - should use cache
        tables2 = scanner.get_table_names()
        assert len(tables2) == 2
        assert mock_inspector.get_table_names.call_count == 1  # Still 1
        
        # Refresh schema - should invalidate cache and call inspector again
        tables3 = scanner.refresh_schema()
        assert len(tables3) == 3  # New result
        assert mock_inspector.get_table_names.call_count == 2  # Called again
        
        print("✅ Cache invalidation funcionando corretamente")


def test_invalid_table_validation_with_cache():
    """Test validação de tabela inválida com cache"""
    
    config = DatabaseConfig(
        url="postgresql://test:test@localhost:5432/test"
    )
    
    with patch('database_scanner.create_engine') as mock_engine, \
         patch('database_scanner.inspect') as mock_inspect:
        
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = ['users', 'orders']
        mock_inspect.return_value = mock_inspector
        
        scanner = DatabaseScanner(config)
        
        # Valid table should work
        valid_table = scanner._sanitize_table_name('users')
        assert valid_table == 'users'
        
        # Invalid table should raise error
        with pytest.raises(ValueError, match="Tabela inválida"):
            scanner._sanitize_table_name('invalid_table')
        
        # Another valid table should work (using cached table names)
        valid_table2 = scanner._sanitize_table_name('orders')
        assert valid_table2 == 'orders'
        
        # Should have called inspector only once for all validations
        assert mock_inspector.get_table_names.call_count == 1
        
        print("✅ Validação de tabelas inválidas funcionando com cache")


if __name__ == "__main__":
    test_table_names_cache_optimization()
    test_sanitize_table_name_cache_efficiency()
    test_cache_invalidation()
    test_invalid_table_validation_with_cache()
    
    print("\n🎉 TODOS OS TESTES DE CACHE PASSARAM!")
    print("📊 Otimização implementada com sucesso:")
    print("   • Cache elimina chamadas redundantes ao inspector")
    print("   • Múltiplas validações usam uma única consulta")
    print("   • Cache pode ser invalidado quando necessário")
    print("   • Performance significativamente melhorada")
