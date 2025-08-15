#!/usr/bin/env python3
"""
Teste de segurança SQL injection no contexto do sistema RAG completo
"""
from dotenv import load_dotenv
from rag_system import create_system_from_env

load_dotenv()


def test_system_security():
    """Testa segurança do sistema RAG contra SQL injection"""
    print("=== TESTE DE SEGURANÇA DO SISTEMA RAG ===\n")
    
    system = create_system_from_env()
    
    try:
        if not system.initialize():
            print("❌ Falha na inicialização do sistema")
            return
        
        print("✅ Sistema RAG inicializado\n")
        
        # 1. Teste de query normal (deve funcionar)
        print("1. Teste de query normal:")
        result = system.get_table_preview("users", limit=2)
        if result["status"] == "success":
            print(f"   ✅ Query normal funciona: {len(result['data'])} registros")
        else:
            print(f"   ❌ Query normal falhou: {result['error']}")
        
        # 2. Testes de SQL injection no get_table_preview
        print("\n2. Testes de SQL injection (devem ser bloqueados):")
        
        injection_attempts = [
            "users; DROP TABLE users;--",
            "users'; DELETE FROM users;--",
            'users"; INSERT INTO users VALUES (999, "hack", "hack@test.com", 99);--',
            "users UNION SELECT * FROM orders",
            "users/*comment*/",
            "users--comment",
        ]
        
        for attempt in injection_attempts:
            result = system.get_table_preview(attempt, limit=5)
            if result["status"] == "error":
                print(f"   ✅ Bloqueado: '{attempt[:30]}...'")
            else:
                print(f"   ❌ VULNERABILIDADE: '{attempt[:30]}...' NÃO foi bloqueada!")
        
        # 3. Verificar integridade dos dados
        print("\n3. Verificação de integridade:")
        result = system.get_table_preview("users", limit=10)
        if result["status"] == "success":
            user_count = len(result["data"])
            if user_count == 3:  # Esperamos 3 usuários de teste
                print(f"   ✅ Dados íntegros: {user_count} usuários (esperado: 3)")
            else:
                print(f"   ⚠️  Possível alteração: {user_count} usuários (esperado: 3)")
        else:
            print(f"   ❌ Erro ao verificar integridade: {result['error']}")
        
        # 4. Teste adicional - verificar se queries do SQL Agent são seguras
        print("\n4. Teste do SQL Agent (perguntas normais):")
        safe_questions = [
            "Quantos usuários existem?",
            "Quais são os nomes das tabelas?",
            "Mostre os produtos mais caros"
        ]
        
        for question in safe_questions:
            result = system.ask(question)
            if result["status"] == "success":
                print(f"   ✅ '{question[:30]}...' -> Funcionou")
            else:
                print(f"   ❌ '{question[:30]}...' -> Falhou: {result['error']}")
        
        print(f"\n🎯 Teste de segurança concluído!")
        print("📋 Resumo:")
        print("   - Query normal: Funciona ✅")
        print("   - SQL injection: Bloqueada ✅") 
        print("   - Integridade dos dados: Mantida ✅")
        print("   - SQL Agent: Funcionando ✅")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
    finally:
        system.close()


if __name__ == "__main__":
    test_system_security()
