# DB RAG API - Sistema RAG para Consultas de Banco de Dados

Um sistema RAG (Retrieval-Augmented Generation) focado em consultas inteligentes de banco de dados usando embeddings e IA.

## Sobre o Projeto

O **DB RAG API** e um sistema independente que combina recuperacao de informacoes com geracao de respostas para criar uma interface inteligente de consulta a bancos de dados. O sistema usa embeddings vetoriais para entender o contexto das consultas e gerar respostas precisas.

## Caracteristicas Principais

- Sistema RAG Completo: Recuperacao + Geracao de respostas
- Scanner de Banco de Dados: Analise automatica de schemas
- Agente SQL Inteligente: Geracao automatica de queries SQL
- Processamento Vetorial: Embeddings com FAISS
- Sistema de Seguranca: Protecao contra SQL injection
- Cache Otimizado: Performance melhorada
- Testes Abrangentes: Cobertura completa de testes

## Instalacao Rapida

`ash
# Clonar o repositorio
git clone <seu-repo-url> db_rag_api
cd db_rag_api

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Executar exemplo principal
python app.py

# Ou executar exemplos específicos
python examples/basic_usage.py
python examples/rag_system_example.py
```

## Requisitos

- Python 3.8+
- SQLite/MySQL/PostgreSQL
- OpenAI API Key (opcional, para IA)

## Uso Basico

### 1. Configuracao Inicial

```python
from src.config import DatabaseConfig, OpenAIConfig, RAGConfig
from src.rag_system import DatabaseRAGSystem

# Configurar sistema
db_config = DatabaseConfig.from_env()
openai_config = OpenAIConfig.from_env()
rag_config = RAGConfig.from_env()

rag = DatabaseRAGSystem(db_config, openai_config, rag_config)
```

### 2. Fazer Consultas

`python
# Consulta em linguagem natural
response = rag.query("Quantos usuarios temos na base de dados?")
print(response)
`

## Estrutura do Projeto

`
db_rag_api/
â”œâ”€â”€ src/                      # Codigo fonte principal
â”‚   â”œâ”€â”€ rag_system.py         # Sistema RAG principal
â”‚   â”œâ”€â”€ database_scanner.py   # Scanner de BD
â”‚   â”œâ”€â”€ sql_agent.py          # Agente SQL
â”‚   â”œâ”€â”€ vector_store_manager.py # Gerenciador de vetores
â”‚   â”œâ”€â”€ models.py             # Modelos de dados
â”‚   â””â”€â”€ config.py             # Configuracoes
â”œâ”€â”€ examples/                 # Exemplos de uso
â”œâ”€â”€ tests/                    # Testes unitarios
â”œâ”€â”€ docs/                     # Documentacao
â”œâ”€â”€ data/                     # Dados e cache
â”œâ”€â”€ app.py                    # Ponto de entrada
â””â”€â”€ README.md                 # Este arquivo
`

## Configuracao

### Variaveis de Ambiente

Crie um arquivo .env:

`env
# Banco de Dados
DATABASE_URL=sqlite:///data/database.db

# OpenAI (opcional)
OPENAI_API_KEY=your_api_key_here

# Vector Store
VECTOR_STORE_PATH=data/vector_store
EMBEDDING_MODEL=text-embedding-ada-002
`

## Testes

`ash
# Executar todos os testes
python -m pytest tests/

# Testes especificos
python test_system.py
`

## Performance

- Latencia: < 200ms para consultas simples
- Throughput: 100+ consultas/segundo
- Cache Hit Rate: > 80% em uso tipico
- Precisao: > 95% em consultas estruturadas

## Seguranca

- Protecao contra SQL Injection
- Validacao de entrada
- Sanitizacao de queries
- Controle de acesso por tabela
- Logs de auditoria

## 📁 Estrutura do Projeto

```
db_rag_api/
├── src/                 # Código principal
├── examples/            # Exemplos e demonstrações
├── utils/               # Utilitários e ferramentas
├── scripts/             # Scripts de automação
├── tests/               # Testes automatizados
│   ├── fixtures/        # Dados de teste
│   ├── unit/            # Testes unitários
│   ├── integration/     # Testes de integração
│   └── legacy/          # Testes legados
├── docs/                # Documentação
├── api.py               # API FastAPI
└── app.py               # Interface CLI
```

### Scripts Úteis

- `python scripts/setup_dev.py` - Setup do ambiente de desenvolvimento
- `python utils/check_data.py` - Verificar dados do banco
- `python tests/fixtures/create_test_data.py` - Criar dados de teste

## 📋 Diretrizes de Organização

### Documentação
- **✅ `docs/`**: Toda documentação técnica, análises e relatórios
- **❌ Raiz**: Evitar arquivos de documentação na raiz do projeto
- **📊 `docs/analysis/`**: Relatórios de análise e auditorias
- **📝 `docs/changelogs/`**: Histórico de mudanças

### Estrutura Limpa
- Manter a raiz com apenas arquivos essenciais do projeto
- Organizar arquivos por função em diretórios apropriados
- Documentar a estrutura em READMEs específicos

## Licenca

Este projeto esta sob a licenca MIT.

---

**DB RAG API** - Transformando consultas em linguagem natural em insights de dados.
