"""
Testes para o scanner de banco de dados
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from database_scanner import DatabaseScanner
from config import DatabaseConfig


class TestDatabaseScanner:
    """Testes para DatabaseScanner"""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture com configuração mock"""
        return DatabaseConfig(
            url="sqlite:///test.db",
            type="sqlite"
        )
    
    @pytest.fixture
    def scanner(self, mock_config):
        """Fixture com scanner mock"""
        with patch('database_scanner.create_engine'):
            return DatabaseScanner(mock_config)
    
    def test_sanitize_table_name_valid(self, scanner):
        """Testa sanitização de nome válido"""
        with patch.object(scanner, 'get_table_names', return_value=['users', 'orders']):
            result = scanner._sanitize_table_name('users')
            assert result == 'users'
    
    def test_sanitize_table_name_invalid_characters(self, scanner):
        """Testa sanitização com caracteres perigosos"""
        with patch.object(scanner, 'get_table_names', return_value=['users']):
            with pytest.raises(ValueError, match="caracteres não permitidos"):
                scanner._sanitize_table_name("users; DROP TABLE users;--")
    
    def test_sanitize_table_name_empty(self, scanner):
        """Testa sanitização com string vazia"""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            scanner._sanitize_table_name("")
    
    def test_sanitize_table_name_not_exists(self, scanner):
        """Testa sanitização com tabela inexistente"""
        with patch.object(scanner, 'get_table_names', return_value=['users', 'orders']):
            with pytest.raises(ValueError, match="Invalid table"):
                scanner._sanitize_table_name("nonexistent_table")
    
    def test_query_table_sample_valid(self, scanner):
        """Testa consulta de amostra válida"""
        mock_df = pd.DataFrame({'id': [1, 2], 'name': ['John', 'Jane']})
        
        with patch.object(scanner, '_sanitize_table_name', return_value='users'), \
             patch.object(scanner.engine, 'connect') as mock_connect, \
             patch('pandas.read_sql', return_value=mock_df):
            
            mock_conn = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            result = scanner.query_table_sample('users', 10)
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
    
    def test_query_table_sample_invalid_table(self, scanner):
        """Testa consulta com tabela inválida"""
        with patch.object(scanner, '_sanitize_table_name', side_effect=ValueError("Invalid table")):
            with pytest.raises(ValueError, match="Erro de validação"):
                scanner.query_table_sample('invalid_table', 10)
    
    def test_get_table_names_sqlite(self, scanner):
        """Testa obtenção de nomes de tabelas SQLite"""
        mock_result = Mock()
        mock_result.fetchall.return_value = [('users',), ('orders',)]
        
        with patch.object(scanner.engine, 'connect') as mock_connect:
            mock_conn = Mock()
            mock_conn.execute.return_value = mock_result
            mock_connect.return_value.__enter__.return_value = mock_conn
            
            result = scanner.get_table_names()
            
            assert result == ['users', 'orders']
    
    def test_close_disposes_engine(self, scanner):
        """Testa que close() descarta o engine"""
        mock_engine = Mock()
        scanner.engine = mock_engine
        
        scanner.close()
        
        mock_engine.dispose.assert_called_once()
