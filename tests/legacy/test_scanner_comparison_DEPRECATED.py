#!/usr/bin/env python3
"""
DEPRECATED - Test file for scanner comparison

⚠️  STATUS: OBSOLETO/DEPRECATED

Este arquivo originalmente comparava diferentes implementações de scanner
que não existem mais no codebase atual. Foi mantido apenas como referência
histórica.

SUBSTITUÍDO POR:
- tests/unit/test_database_scanner.py - Testes unitários do scanner atual
- tests/integration/ - Testes de integração modernos

ARQUIVOS QUE ERAM REFERENCIADOS (REMOVIDOS):
- database_scanner_old.py
- database_scanner_sqlalchemy.py
"""

def deprecated_notice():
    """Aviso sobre arquivo obsoleto"""
    print("=" * 70)
    print("⚠️  ARQUIVO DEPRECATED - test_scanner_comparison.py")
    print("=" * 70)
    print()
    print("Este arquivo de teste está obsoleto porque:")
    print("• Refere arquivos que não existem mais (database_scanner_old.py)")
    print("• Compara implementações que foram consolidadas")
    print("• Usa padrões de teste antigos (print ao invés de assert)")
    print()
    print("📋 Use os testes modernos:")
    print("• tests/unit/test_database_scanner.py")
    print("• tests/integration/test_rag_system.py")
    print()
    print("🔧 Para executar testes atuais:")
    print("   pytest tests/unit/test_database_scanner.py -v")
    print("=" * 70)

if __name__ == "__main__":
    deprecated_notice()
