#!/usr/bin/env python3
"""
Demonstração da refatoração de testes com assertions determinísticas
"""
import os
import tempfile
import sqlite3
from dotenv import load_dotenv

load_dotenv()

from config import DatabaseConfig
from database_scanner import DatabaseScanner


def test_sql_injection_old_style():
    """EXEMPLO ANTIGO: Com prints não determinísticos"""
    print("=== TESTE ANTIGO (COM PRINTS) ===")
    
    # Criar banco temporário
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
        # Setup banco
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE test_users (id INTEGER, name TEXT)')
        cursor.execute("INSERT INTO test_users VALUES (1, 'John')")
        conn.commit()
        conn.close()
        
        config = DatabaseConfig(url=f"sqlite:///{test_db_path}", type="sqlite")
        scanner = DatabaseScanner(config)
        
        # Teste 1: Query válida
        try:
            result = scanner.query_table_sample("test_users", 5)
            print(f"✅ Query válida: {len(result)} registros")
        except Exception as e:
            print(f"❌ Query válida falhou: {e}")
        
        # Teste 2: SQL injection
        try:
            scanner.query_table_sample("test_users; DROP TABLE test_users;--", 5)
            print("❌ SQL injection NÃO foi bloqueada!")
        except Exception:
            print("✅ SQL injection foi bloqueada")
        
        print("🎯 Teste 'passou' mas não sabemos detalhes")
        
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)


def test_sql_injection_new_style():
    """EXEMPLO NOVO: Com assertions determinísticas"""
    print("=== TESTE NOVO (COM ASSERTIONS) ===")
    
    # Criar banco temporário
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
        # Setup banco
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE test_users (id INTEGER, name TEXT)')
        cursor.execute("INSERT INTO test_users VALUES (1, 'John')")
        cursor.execute("INSERT INTO test_users VALUES (2, 'Jane')")
        conn.commit()
        conn.close()
        
        config = DatabaseConfig(url=f"sqlite:///{test_db_path}", type="sqlite")
        scanner = DatabaseScanner(config)
        
        # Teste 1: Query válida com validações específicas
        result = scanner.query_table_sample("test_users", 5)
        assert result is not None, "Query válida deve retornar resultado"
        assert len(result) > 0, "Deve retornar registros"
        assert len(result) == 2, "Deve retornar exatamente 2 registros"
        print("✅ Query válida - VALIDADA com assertions")
        
        # Teste 2: SQL injection com validação específica
        injection_blocked = False
        try:
            scanner.query_table_sample("test_users; DROP TABLE test_users;--", 5)
        except ValueError as e:
            assert "Tabela inválida" in str(e), "Erro deve mencionar tabela inválida"
            injection_blocked = True
        
        assert injection_blocked, "SQL injection deve ser bloqueada"
        print("✅ SQL injection - BLOQUEADA com validação específica")
        
        # Teste 3: Integridade dos dados
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_users")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 2, "Dados devem permanecer íntegros"
        print("✅ Integridade dos dados - VERIFICADA")
        
        # Teste 4: Parâmetros inválidos
        invalid_params_blocked = 0
        invalid_cases = [
            ("", 5),           # Nome vazio
            ("test_users", 0), # Limit zero
            ("test_users", -1) # Limit negativo
        ]
        
        for table, limit in invalid_cases:
            try:
                scanner.query_table_sample(table, limit)
            except ValueError:
                invalid_params_blocked += 1
        
        assert invalid_params_blocked == len(invalid_cases), "Todos os parâmetros inválidos devem ser bloqueados"
        print("✅ Parâmetros inválidos - TODOS BLOQUEADOS")
        
        print("🎯 Teste PASSOU com validações específicas e determinísticas!")
        
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)


def demonstrate_assertion_benefits():
    """Demonstra benefícios específicos das assertions"""
    print("\n" + "="*60)
    print("🔍 ANÁLISE DETALHADA DOS BENEFÍCIOS")
    print("="*60)
    
    benefits = [
        {
            "aspecto": "Determinismo",
            "antes": "Teste 'passa' mesmo se logica falha",
            "depois": "Teste falha imediatamente se condição não atendida"
        },
        {
            "aspecto": "Debugging",
            "antes": "print() mostra apenas saída visual",
            "depois": "assert fornece linha exata e condição específica"
        },
        {
            "aspecto": "Automação",
            "antes": "Humano precisa interpretar output visual",
            "depois": "CI/CD pode executar e detectar falhas automaticamente"
        },
        {
            "aspecto": "Cobertura",
            "antes": "Não sabemos o que realmente foi testado",
            "depois": "Cada assert verifica comportamento específico"
        },
        {
            "aspecto": "Regressão",
            "antes": "Mudanças podem quebrar sem detecção",
            "depois": "Qualquer mudança que quebre é detectada imediatamente"
        }
    ]
    
    for benefit in benefits:
        print(f"\n📋 {benefit['aspecto']}:")
        print(f"   ❌ Antes: {benefit['antes']}")
        print(f"   ✅ Depois: {benefit['depois']}")


def show_refactoring_checklist():
    """Mostra checklist para refatorar outros testes"""
    print("\n" + "="*60)
    print("📝 CHECKLIST PARA REFATORAÇÃO DE TESTES")
    print("="*60)
    
    checklist = [
        "1. Substituir print() por assert com mensagens descritivas",
        "2. Verificar condições específicas em vez de apenas execução",
        "3. Usar fixtures para setup/teardown limpos",
        "4. Testar tanto casos positivos quanto negativos",
        "5. Validar estado dos dados após operações",
        "6. Usar context managers (with pytest.raises) para exceções",
        "7. Agrupar testes relacionados em classes",
        "8. Usar parametrização para testar múltiplos casos",
        "9. Adicionar testes de edge cases",
        "10. Configurar integração com CI/CD"
    ]
    
    for item in checklist:
        print(f"   ✅ {item}")


if __name__ == "__main__":
    print("🔄 DEMONSTRAÇÃO: REFATORAÇÃO DE TESTES")
    print("="*60)
    
    try:
        # Executar teste antigo
        test_sql_injection_old_style()
        
        print()
        
        # Executar teste novo
        test_sql_injection_new_style()
        
        # Mostrar análise
        demonstrate_assertion_benefits()
        
        # Mostrar checklist
        show_refactoring_checklist()
        
        print("\n" + "="*60)
        print("🎉 REFATORAÇÃO DEMONSTRADA COM SUCESSO!")
        print("💡 Aplique este padrão aos outros testes:")
        print("   • test_vector_security.py")
        print("   • test_validation.py")
        print("   • test_env_validation.py")
        print("   • test_system_security.py")
        print("   • E todos os outros com print()")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()
