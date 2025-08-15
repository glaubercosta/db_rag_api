# 🤖 Multi-LLM Database RAG System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com)
[![Multi-LLM](https://img.shields.io/badge/Multi--LLM-OpenAI%20%7C%20Ollama%20%7C%20Custom-purple)](https://github.com)

Um sistema RAG (Retrieval-Augmented Generation) de última geração que suporta **múltiplos provedores de LLM** para consultas inteligentes de banco de dados.

## 🎯 Visão Geral

O **Multi-LLM Database RAG System** revoluciona a forma como você interage com seus dados, oferecendo:

### 🧠 **Flexibilidade de IA**
- **OpenAI**: GPT-4, GPT-3.5 (precisão e qualidade)
- **Ollama**: Modelos locais (privacidade e controle)
- **APIs Customizadas**: Modelos proprietários da empresa

### 🔄 **Adaptabilidade Total**
- Alternância dinâmica entre provedores
- Fallback automático em caso de falha
- Configuração por ambiente (dev/prod)
- Preferências por tipo (LLM/Embeddings)

### 🏢 **Pronto para Empresa**
- Suporte a APIs internas
- Headers customizados
- Autenticação flexível
- Logs de auditoria

## 🚀 Início em 3 Minutos

### 1️⃣ **Instalação**

```bash
git clone <seu-repo> && cd db_rag_api
python -m venv venv && venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2️⃣ **Configuração Rápida**

```bash
# Copie o template de configuração
cp .env.multi-llm.example .env

# Configure pelo menos UM provedor:
```

**Opção A - OpenAI (Mais Fácil):**
```bash
echo "OPENAI_API_KEY=sk-sua-chave-aqui" >> .env
```

**Opção B - Ollama (Gratuito, Local):**
```bash
# Instale Ollama: https://ollama.ai
ollama serve & ollama pull llama2
echo "OLLAMA_MODEL=llama2" >> .env
echo "PREFERRED_LLM_PROVIDER=ollama" >> .env
```

**Opção C - API da Empresa:**
```bash
echo "CUSTOM_LLM_API_BASE=https://sua-empresa.com/api" >> .env
echo "CUSTOM_LLM_MODEL=seu-modelo" >> .env
echo "PREFERRED_LLM_PROVIDER=custom" >> .env
```

### 3️⃣ **Executar e Testar**

```bash
# Teste rápido do sistema
python quick_test.py

# Executar API Multi-LLM
python multi_llm_api.py

# ✅ API disponível em: http://localhost:9000
```

## 💡 Exemplos Práticos

### 🔍 **Consulta Via API**

```bash
curl -X POST http://localhost:9000/query \\
  -H "Authorization: Bearer dev-multi-llm-key-12345" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Quantos usuários ativos temos este mês?"}'
```

### 🐍 **Uso Direto em Python**

```python
from src.multi_llm_rag_system import create_multi_llm_rag_system_from_env

# Criar sistema a partir das variáveis de ambiente
rag = create_multi_llm_rag_system_from_env()

# Inicializar
if rag.initialize():
    # Consultar
    result = rag.query("Mostre as vendas por região")
    print(result["answer"])
    
    # Trocar provedor dinamicamente
    rag.switch_llm_provider("ollama")
    
    # Nova consulta com provedor diferente
    result2 = rag.query("Análise de performance")
    print(f"Resposta via {result2['provider_used']}: {result2['answer']}")
```

### ⚡ **Alternância de Provedor**

```bash
# Mudar para Ollama (local)
curl -X POST http://localhost:9000/switch-provider \\
  -H "Authorization: Bearer dev-multi-llm-key-12345" \\
  -H "Content-Type: application/json" \\
  -d '{"provider": "ollama", "type": "llm"}'

# Consulta específica com provedor
curl -X POST http://localhost:9000/query \\
  -H "Authorization: Bearer dev-multi-llm-key-12345" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Análise de dados", "provider": "openai"}'
```

## 🎛️ Cenários de Uso

### 🏗️ **Desenvolvimento vs Produção**

```bash
# Desenvolvimento: Grátis e rápido
OLLAMA_MODEL=llama2
PREFERRED_LLM_PROVIDER=ollama

# Produção: Máxima qualidade
OPENAI_API_KEY=sk-prod-key
PREFERRED_LLM_PROVIDER=openai
```

### 🔐 **Dados Sensíveis**

```bash
# Apenas modelos internos/locais
OLLAMA_MODEL=llama2
CUSTOM_LLM_API_BASE=https://internal-api.company.com
PREFERRED_LLM_PROVIDER=custom
PREFERRED_EMBEDDING_PROVIDER=ollama
```

### 💰 **Otimização de Custos**

```bash
# LLM local (barato) + Embeddings OpenAI (precisos)
OLLAMA_MODEL=llama2
OPENAI_API_KEY=sk-key
PREFERRED_LLM_PROVIDER=ollama
PREFERRED_EMBEDDING_PROVIDER=openai
```

### 🚀 **Alta Disponibilidade**

```bash
# Configure múltiplos provedores para fallback
OPENAI_API_KEY=sk-key
OLLAMA_MODEL=llama2
CUSTOM_LLM_API_BASE=https://backup-api.com
# Sistema alterna automaticamente se um falhar
```

## 🏗️ Arquitetura

```mermaid
graph TB
    A[Multi-LLM RAG System] --> B[Provider Manager]
    B --> C[OpenAI Provider]
    B --> D[Ollama Provider]
    B --> E[Custom Provider]
    
    A --> F[Database Scanner]
    A --> G[Vector Store Manager]
    A --> H[SQL Agent]
    
    F --> I[Schema Analysis]
    G --> J[FAISS Index]
    H --> K[Query Generation]
    
    C --> L[GPT-4/3.5]
    D --> M[Llama2/Mistral]
    E --> N[Company APIs]
```

## 📊 Funcionalidades Avançadas

### 🔄 **Provider Management**
- Auto-detecção de provedores disponíveis
- Fallback inteligente
- Health checks automáticos
- Métricas de performance

### 🛡️ **Segurança**
- Proteção SQL injection
- Sanitização de queries
- Headers customizados
- Logs de auditoria

### ⚡ **Performance**
- Cache de embeddings
- Pool de conexões
- Retry automático
- Timeout configurável

### 📈 **Monitoramento**
- Status de todos os provedores
- Métricas de uso
- Logs estruturados
- Health endpoints

## 🔧 Configuração Avançada

### 🌐 **Headers Customizados**

```bash
# Para APIs empresariais com autenticação específica
CUSTOM_LLM_HEADER_X_API_VERSION=2023-12-01
CUSTOM_LLM_HEADER_X_TENANT_ID=sua-empresa
CUSTOM_LLM_HEADER_Authorization=Bearer custom-token
```

### 🎯 **Formatos de API**

```bash
# Para APIs compatíveis com OpenAI
CUSTOM_LLM_FORMAT=openai
CUSTOM_LLM_ENDPOINT=/v1/chat/completions

# Para APIs estilo Ollama
CUSTOM_LLM_FORMAT=ollama
CUSTOM_LLM_ENDPOINT=/api/generate
```

### 📝 **Logs Detalhados**

```bash
# Configuração de logging
LOG_LEVEL=DEBUG
ENABLE_PROVIDER_LOGGING=true
LOG_FILE=./logs/multi_llm.log
```

## 🔍 API Endpoints

### 📋 **Consultas**
- `POST /query` - Consulta principal
- `POST /query?provider=ollama` - Consulta com provedor específico

### 🔄 **Gerenciamento**
- `POST /switch-provider` - Trocar provedor ativo
- `GET /providers` - Listar todos os provedores
- `GET /status` - Status completo do sistema

### 🩺 **Monitoramento**
- `GET /health` - Health check
- `GET /metrics` - Métricas de uso

## 🧪 Testes

```bash
# Teste rápido do sistema
python quick_test.py

# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Teste de performance
python tests/performance/benchmark_providers.py

# Exemplo completo
python examples/multi_llm_usage.py
```

## 📚 Documentação

- 📖 **[Guia Completo Multi-LLM](docs/MULTI_LLM_GUIDE.md)** - Documentação detalhada
- 🔧 **[Configuração Avançada](docs/ADVANCED_CONFIG.md)** - Opções avançadas
- 🏢 **[Deploy Empresarial](docs/ENTERPRISE_DEPLOY.md)** - Deploy em produção
- 🔐 **[Segurança](docs/SECURITY.md)** - Práticas de segurança

## 🆚 Comparação com Sistema Original

| Funcionalidade | Sistema Original | Multi-LLM System |
|---|---|---|
| **Provedores LLM** | OpenAI apenas | OpenAI + Ollama + Custom |
| **Flexibilidade** | Limitada | Total |
| **Dados Sensíveis** | Na nuvem | Local disponível |
| **Custos** | Fixos (OpenAI) | Otimizáveis |
| **Fallback** | Não | Automático |
| **APIs Empresariais** | Não | Sim |
| **Desenvolvimento Local** | Requer API key | Gratuito com Ollama |

## 🎉 Próximos Passos

1. **✅ Execute o teste rápido**: `python quick_test.py`
2. **🔧 Configure seus provedores** no arquivo `.env`
3. **🚀 Inicie a API**: `python multi_llm_api.py`
4. **🧪 Teste via navegador**: http://localhost:9000/docs
5. **📖 Leia o guia completo**: [docs/MULTI_LLM_GUIDE.md](docs/MULTI_LLM_GUIDE.md)

## 🤝 Contribuições

- **🐛 Issues**: Reporte bugs e problemas
- **💡 Features**: Sugira novas funcionalidades
- **📝 Docs**: Melhore a documentação
- **🧪 Tests**: Adicione mais testes

---

### 🎯 **Resultado Final**

Um sistema **flexível**, **seguro** e **pronto para produção** que se adapta desde desenvolvimento local até APIs empresariais proprietárias!

**🚀 Comece agora**: `python quick_test.py`
