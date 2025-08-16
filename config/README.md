# 📁 Pasta de Configuração

Esta pasta contém arquivos de configuração do projeto DB RAG API.

## 📋 Arquivos de Configuração

### **Ambientes e Exemplos**
- `.env.example` - Exemplo de configuração da API original
- `.env.multi-llm.example` - Exemplo de configuração Multi-LLM
- `setup.cfg` - Configuração de setup do Python

### **Testes e Qualidade de Código**
- `pytest.ini` - Configuração do pytest
- `.flake8` - Configuração do linter Flake8
- `Makefile.tests` - Makefile para execução de testes

## 🔧 Como Usar

### **Configurar Ambiente**
1. Copie `.env.example` ou `.env.multi-llm.example` para `.env` na raiz
2. Configure suas variáveis de ambiente

### **Executar Testes**
```bash
# Da raiz do projeto
pytest -c config/pytest.ini

# Ou usando o Makefile
make -f config/Makefile.tests test
```

### **Linting**
```bash
# Da raiz do projeto  
flake8 --config=config/.flake8
```

## 📖 Documentação

Para mais detalhes sobre configuração, consulte:
- `docs/` - Documentação completa
- `README.md` - Guia principal do projeto
