#!/usr/bin/env python3
"""
Teste da correção de SQL injection no query_table_sample
"""
import os
import tempfile
import sqlite3
from dotenv import load_dotenv

# Carregar ambiente
load_dotenv()

from config import DatabaseConfig
from database_scanner import DatabaseScanner

def test_sql_injection_protection():
    """Testa proteção contra SQL injection"""
    print("=== TESTANDO PROTEÇÃO CONTRA SQL INJECTION ===\n")
    
    # Criar banco temporário para teste
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
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
        
        # Configurar scanner
        config = DatabaseConfig(url=f"sqlite:///{test_db_path}", type="sqlite")
        scanner = DatabaseScanner(config)
        
        print("1. Teste com nome de tabela válido:")
        try:
            result = scanner.query_table_sample("test_users", 5)
            print(f"   ✅ Query válida funcionou: {len(result)} registros retornados")
        except Exception as e:
            print(f"   ❌ Query válida falhou: {e}")
        
        print("\n2. Testes de SQL injection (devem falhar):")
        
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
        
        for attempt in injection_attempts:
            try:
                scanner.query_table_sample(attempt, 5)
                print(f"   ❌ VULNERABILIDADE: '{attempt[:30]}...' não foi bloqueada!")
            except ValueError as e:
                print(f"   ✅ Bloqueado: '{attempt[:30]}...' -> {str(e)[:50]}...")
            except Exception as e:
                print(f"   ⚠️  Erro inesperado em '{attempt[:30]}...': {e}")
        
        print("\n3. Teste com tabela inexistente:")
        try:
            scanner.query_table_sample("nonexistent_table", 5)
            print("   ❌ Tabela inexistente deveria falhar")
        except ValueError as e:
            print(f"   ✅ Tabela inexistente bloqueada: {str(e)[:50]}...")
        
        print("\n4. Teste com parâmetros inválidos:")
        invalid_params = [
            ("", "nome vazio"),
            ("   ", "nome só espaços"),
            (None, "nome None"),
            (123, "nome numérico")
        ]
        
        for param, description in invalid_params:
            try:
                scanner.query_table_sample(param, 5)
                print(f"   ❌ {description} deveria falhar")
            except (ValueError, TypeError) as e:
                print(f"   ✅ {description} bloqueado")
        
        # Verificar se os dados ainda existem (não foram corrompidos)
        print("\n5. Verificação de integridade dos dados:")
        try:
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_users")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 2:
                print("   ✅ Dados íntegros: nenhuma injeção SQL foi executada")
            else:
                print(f"   ❌ Dados comprometidos: {count} registros (esperados: 2)")
        except Exception as e:
            print(f"   ❌ Erro ao verificar integridade: {e}")
        
        scanner.close()
        
    finally:
        # Limpar arquivo temporário
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)
    
    print("\n🎯 Teste de segurança SQL injection concluído!")

if __name__ == "__main__":
    test_sql_injection_protection()
