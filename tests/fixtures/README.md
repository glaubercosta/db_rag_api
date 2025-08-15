# 🧪 Test Fixtures

Dados e utilitários para criação de fixtures de teste.

## 📋 Arquivos

### `create_test_data.py`
Script para criar dados de teste no SQLite para desenvolvimento e testes manuais.

**Funcionalidade:**
- Cria banco SQLite de teste (`test.db`)
- Popula com dados de usuários, produtos, categorias e pedidos
- Útil para desenvolvimento e debugging

**Uso:**
```bash
cd tests/fixtures
python create_test_data.py
```

## 📝 Notas

- Este arquivo cria dados manualmente (não integrado aos testes automatizados)
- Para testes automatizados, use as fixtures do pytest em `conftest.py`
- O banco criado (`test.db`) é usado para desenvolvimento e testes manuais

## 🔗 Relacionados

- `tests/conftest.py` - Fixtures automáticas do pytest
- `tests/utils/test_helpers.py` - Helpers para testes
