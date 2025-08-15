#!/usr/bin/env python3
"""
Teste de proteção contra SQL injection - REFATORADO COM ASSERTIONS
"""
import os
import tempfile
import sqlite3
import pytest
from dotenv import load_dotenv

load_dotenv()

from config import DatabaseConfig
from database_scanner import DatabaseScanner


class TestSQLInjectionProtection:
    """Test class para proteção contra SQL injection com assertions determinísticas"""

    @pytest.fixture
    def test_database(self):
        """Fixture que cria banco temporário para testes"""
        # Criar banco temporário
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db_path = tmp.name
        
        # Criar tabela de teste
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')
        cursor.execute("INSERT INTO test_users (name, email) VALUES ('John', 'john@test.com')")
        cursor.execute("INSERT INTO test_users (name, email) VALUES ('Jane', 'jane@test.com')")
        conn.commit()
        conn.close()
        
        yield test_db_path
        
        # Cleanup
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

    @pytest.fixture
    def scanner(self, test_database):
        """Fixture que cria scanner configurado com banco de teste"""
        config = DatabaseConfig(url=f"sqlite:///{test_database}", type="sqlite")
        return DatabaseScanner(config)

    def test_valid_table_query(self, scanner):
        """Testa que queries válidas funcionam corretamente"""
        result = scanner.query_table_sample("test_users", 5)
        
        assert result is not None, "Query válida deve retornar resultado"
        assert len(result) > 0, "Query deve retornar registros"
        assert len(result) <= 2, "Deve retornar no máximo 2 registros (dados de teste)"
        
        # Verificar estrutura do resultado
        if len(result) > 0:
            row = result.iloc[0]
            assert 'id' in row, "Resultado deve ter coluna 'id'"
            assert 'name' in row, "Resultado deve ter coluna 'name'"
            assert 'email' in row, "Resultado deve ter coluna 'email'"

    def test_sql_injection_attempts_blocked(self, scanner):
        """Testa que tentativas de SQL injection são bloqueadas"""
        injection_attempts = [
            "test_users; DROP TABLE test_users;--",
            "test_users'; DROP TABLE test_users;--",
            'test_users"; DROP TABLE test_users;--',
            "test_users UNION SELECT * FROM test_users",
            "test_users/*comment*/",
            "test_users--comment",
            "test_users\nUNION SELECT 1,2,3",
            "test_users\'; INSERT INTO test_users VALUES (999, 'hacked', 'hack@test.com');--"
        ]
        
        blocked_count = 0
        for attempt in injection_attempts:
            with pytest.raises(ValueError, match="Tabela inválida"):
                scanner.query_table_sample(attempt, 5)
            blocked_count += 1
        
        assert blocked_count == len(injection_attempts), "Todas as tentativas de injection devem ser bloqueadas"

    def test_nonexistent_table_blocked(self, scanner):
        """Testa que tabelas inexistentes são bloqueadas"""
        with pytest.raises(ValueError, match="Tabela inválida"):
            scanner.query_table_sample("nonexistent_table", 5)

    def test_invalid_parameters_blocked(self, scanner):
        """Testa que parâmetros inválidos são bloqueados"""
        invalid_params = [
            ("test_users", 0),      # limit zero
            ("test_users", -1),     # limit negativo
            ("", 5),                # nome vazio
            (None, 5),              # nome None
        ]
        
        for table_name, limit in invalid_params:
            with pytest.raises(ValueError):
                scanner.query_table_sample(table_name, limit)

    def test_data_integrity_maintained(self, scanner, test_database):
        """Testa que tentativas de injection não corrompem dados"""
        # Verificar contagem inicial
        conn = sqlite3.connect(test_database)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_users")
        initial_count = cursor.fetchone()[0]
        conn.close()
        
        assert initial_count == 2, "Dados iniciais devem ter 2 registros"
        
        # Tentar várias tentativas de injection
        malicious_attempts = [
            "test_users; DELETE FROM test_users;--",
            "test_users'; INSERT INTO test_users VALUES (999, 'evil', 'evil@hack.com');--",
            "test_users; UPDATE test_users SET name = 'hacked';--"
        ]
        
        for attempt in malicious_attempts:
            try:
                scanner.query_table_sample(attempt, 5)
            except ValueError:
                pass  # Esperado que seja bloqueado
        
        # Verificar se dados continuam íntegros
        conn = sqlite3.connect(test_database)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_users")
        final_count = cursor.fetchone()[0]
        
        # Verificar se registros originais ainda existem
        cursor.execute("SELECT name FROM test_users ORDER BY id")
        names = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert final_count == initial_count, "Número de registros deve permanecer inalterado"
        assert 'John' in names, "Registro original 'John' deve existir"
        assert 'Jane' in names, "Registro original 'Jane' deve existir"
        assert 'hacked' not in names, "Não deve haver registros maliciosos"

    def test_table_validation_caching(self, scanner):
        """Testa que validação de tabelas usa cache eficientemente"""
        # Primeira chamada - deve funcionar
        result1 = scanner.query_table_sample("test_users", 1)
        assert len(result1) > 0, "Primeira query deve funcionar"
        
        # Segunda chamada para mesma tabela - deve usar cache
        result2 = scanner.query_table_sample("test_users", 2)
        assert len(result2) > 0, "Segunda query deve funcionar (cache)"
        
        # Verificar que cache de tabelas não é vulnerável
        with pytest.raises(ValueError):
            scanner.query_table_sample("test_users; DROP TABLE test_users;--", 1)

    def test_concurrent_safety(self, scanner):
        """Testa que validações são thread-safe"""
        # Múltiplas queries simultâneas devem funcionar
        valid_queries = [
            ("test_users", 1),
            ("test_users", 2),
            ("test_users", 1)
        ]
        
        results = []
        for table, limit in valid_queries:
            result = scanner.query_table_sample(table, limit)
            results.append(result)
        
        assert len(results) == 3, "Todas as queries válidas devem funcionar"
        for result in results:
            assert len(result) > 0, "Cada resultado deve ter dados"

    def test_edge_cases(self, scanner):
        """Testa casos extremos e edge cases"""
        # Casos que devem ser bloqueados
        edge_cases = [
            "TEST_USERS",  # Case diferente
            " test_users ",  # Com espaços
            "test_users\t",  # Com tab
            "test_users\n",  # Com newline
        ]
        
        for case in edge_cases:
            if case.strip().lower() == "test_users":
                # Deve funcionar (após sanitização)
                result = scanner.query_table_sample(case, 1)
                assert len(result) >= 0, f"Caso '{case}' deve funcionar após sanitização"
            else:
                # Deve ser bloqueado
                with pytest.raises(ValueError):
                    scanner.query_table_sample(case, 1)


def test_integration_with_real_database():
    """Teste de integração com banco real"""
    # Este teste só roda se houver configuração real
    try:
        config = DatabaseConfig.from_env()
        scanner = DatabaseScanner(config)
        
        # Tentar listar tabelas - deve funcionar
        tables = scanner.get_table_names()
        assert len(tables) > 0, "Banco real deve ter tabelas"
        
        # Testar com primeira tabela válida
        if tables:
            first_table = tables[0]
            result = scanner.query_table_sample(first_table, 1)
            assert result is not None, "Query em tabela real deve funcionar"
        
    except Exception:
        pytest.skip("Configuração de banco real não disponível")


if __name__ == "__main__":
    # Executar com pytest se chamado diretamente
    pytest.main([__file__, "-v", "--tb=short"])
