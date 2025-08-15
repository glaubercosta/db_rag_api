# 🤖 Multi-LLM Database RAG System

## 🎯 Visão Geral

O sistema foi expandido para suportar **múltiplos provedores de LLM**, permitindo flexibilidade total na escolha de modelos de IA:

- **🌐 OpenAI**: GPT-4, GPT-3.5, embeddings
- **🏠 Ollama**: Modelos locais (Llama, Mistral, CodeLlama, etc.)
- **🏢 APIs Customizadas**: Modelos proprietários da sua empresa
- **🔄 Alternância Dinâmica**: Mude de provedor em tempo real

## 🚀 Início Rápido

### 1. Configuração Básica

```bash
# Clone e configure o projeto
git clone <repo-url>
cd db_rag_api

# Copie o arquivo de configuração
cp .env.multi-llm.example .env

# Configure pelo menos um provedor no .env
```

### 2. Opções de Provedores

#### OpenAI (Nuvem)

```bash
export OPENAI_API_KEY="sk-sua-chave-aqui"
export OPENAI_MODEL="gpt-4"
export OPENAI_EMBEDDING_MODEL="text-embedding-ada-002"
```

#### Ollama (Local)

```bash
# Instale o Ollama: https://ollama.ai
ollama serve
ollama pull llama2

export OLLAMA_MODEL="llama2"
export OLLAMA_EMBEDDING_MODEL="llama2"
export OLLAMA_BASE_URL="http://localhost:11434"
```

#### API Customizada (Empresa)

```bash
export CUSTOM_LLM_API_BASE="https://sua-empresa.com/api"
export CUSTOM_LLM_MODEL="seu-modelo-proprietario"
export CUSTOM_LLM_API_KEY="sua-chave-empresa"
export CUSTOM_LLM_FORMAT="openai"  # ou "ollama"
```

### 3. Executar a API

```bash
# API Multi-LLM (nova)
python multi_llm_api.py

# A API estará disponível em http://localhost:9000
```

## 📋 Funcionalidades

### ✨ **Flexibilidade de Provedores**

- **Suporte simultâneo** a múltiplos provedores
- **Fallback automático** se um provedor falhar
- **Preferências configuráveis** por tipo (LLM/Embeddings)

### 🔄 **Alternância Dinâmica**

```python
# Via código Python
rag_system.switch_llm_provider("ollama")
rag_system.switch_embedding_provider("openai")

# Via API REST
POST /switch-provider
{
    "provider": "ollama",
    "type": "llm"
}
```

### 📊 **Monitoramento Completo**

```python
# Status do sistema
GET /status

# Lista todos os provedores
GET /providers
```

### 🎯 **Consultas com Override**

```python
# Especifique o provedor por consulta
POST /query
{
    "query": "Quantos usuários existem?",
    "provider": "ollama"  # Opcional
}
```

## 🛠️ Exemplos de Uso

### Python Direto

```python
from src.multi_llm_rag_system import create_multi_llm_rag_system_from_env

# Criar sistema a partir do ambiente
rag_system = create_multi_llm_rag_system_from_env()

# Inicializar
if rag_system.initialize():
    # Consultar
    result = rag_system.query("Mostre as vendas do último mês")
    print(result["answer"])
    
    # Alternar provedor
    rag_system.switch_llm_provider("ollama")
    
    # Nova consulta com provedor diferente
    result2 = rag_system.query("Quantos produtos temos?")
    print(result2["answer"])
```

### API REST

```bash
# Consulta básica
curl -X POST http://localhost:9000/query \
  -H "Authorization: Bearer dev-multi-llm-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"query": "Quantos clientes ativos temos?"}'

# Consulta com provedor específico
curl -X POST http://localhost:9000/query \
  -H "Authorization: Bearer dev-multi-llm-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze user behavior", "provider": "openai"}'

# Verificar status
curl -H "Authorization: Bearer dev-multi-llm-key-12345" \
  http://localhost:9000/status

# Alternar provedor
curl -X POST http://localhost:9000/switch-provider \
  -H "Authorization: Bearer dev-multi-llm-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"provider": "ollama", "type": "llm"}'
```

## 🏗️ Arquitetura

### Componentes Principais

```text
Multi-LLM RAG System
├── 🔌 Provider Manager
│   ├── OpenAI Provider
│   ├── Ollama Provider  
│   └── Custom Provider
├── 🧠 LLM Interface
│   ├── Text Generation
│   └── Chat Completion
├── 📊 Embedding Interface
│   ├── Document Embeddings
│   └── Query Embeddings
├── 🗃️ Vector Store Manager
├── 🔍 SQL Agent (Multi-LLM)
└── 📋 RAG Query Processor
```

### Fluxo de Processamento

1. **Configuração**: Sistema detecta provedores disponíveis
2. **Seleção**: Escolhe provedor ativo baseado em preferências
3. **Consulta**: Processa linguagem natural usando provedor ativo
4. **Embeddings**: Busca contexto relevante no vector store
5. **Geração SQL**: Cria queries usando LLM ativo
6. **Resposta**: Retorna resultado com informações do provedor

## ⚙️ Configuração Avançada

### Preferências de Provedor

```bash
# Defina preferências globais
export PREFERRED_LLM_PROVIDER="openai"
export PREFERRED_EMBEDDING_PROVIDER="custom"

# Sistema tentará usar OpenAI para LLM e API customizada para embeddings
```

### Headers Customizados (Empresariais)

```bash
# Para APIs que requerem headers específicos
export CUSTOM_LLM_HEADER_X_API_VERSION="2023-12-01"
export CUSTOM_LLM_HEADER_X_TENANT_ID="sua-empresa"

# Estes se tornam headers HTTP:
# X-API-Version: 2023-12-01
# X-Tenant-ID: sua-empresa
```

### Formatos de API Customizada

```bash
# Para APIs compatíveis com OpenAI
export CUSTOM_LLM_FORMAT="openai"
export CUSTOM_LLM_ENDPOINT="/v1/chat/completions"

# Para APIs no estilo Ollama
export CUSTOM_LLM_FORMAT="ollama"
export CUSTOM_LLM_ENDPOINT="/api/generate"
```

## 🔐 Segurança

### Autenticação da API

```bash
# Defina sua chave personalizada
export API_KEY="sua-chave-super-secreta"

# Use nos requests
curl -H "Authorization: Bearer sua-chave-super-secreta" ...
```

### Segurança de Dados

- **Embeddings locais**: Use Ollama para manter dados internos
- **APIs privadas**: Configure endpoints internos da empresa
- **Logs auditoria**: Sistema registra todas as consultas e trocas de provedor

## 🎯 Casos de Uso

### 1. **Desenvolvimento e Produção**
```bash
# Desenvolvimento: Ollama (grátis, local)
export OLLAMA_MODEL="llama2"

# Produção: OpenAI (mais preciso)
export OPENAI_API_KEY="sk-prod-key"
export PREFERRED_LLM_PROVIDER="openai"
```

### 2. **Conformidade de Dados**
```bash
# Dados sensíveis: apenas modelos locais
export OLLAMA_MODEL="llama2"  
export OLLAMA_EMBEDDING_MODEL="llama2"

# Dados públicos: pode usar OpenAI
export PREFERRED_LLM_PROVIDER="ollama"
```

### 3. **Fallback e Redundância**
```bash
# Configure múltiplos provedores
export OPENAI_API_KEY="sk-key"
export OLLAMA_MODEL="llama2"
export CUSTOM_LLM_API_BASE="https://backup-api.com"

# Sistema alternará automaticamente se um falhar
```

### 4. **Otimização de Custos**
```bash
# Embeddings (baratos): OpenAI
export OPENAI_API_KEY="sk-key"
export PREFERRED_EMBEDDING_PROVIDER="openai"

# LLM (caros): Ollama local
export OLLAMA_MODEL="llama2"  
export PREFERRED_LLM_PROVIDER="ollama"
```

## 📊 Monitoramento

### Status do Sistema
```python
# Ver todos os provedores e seu status
status = rag_system.get_system_info()
print(status["providers"])

# Saída exemplo:
{
    "llm_providers": {
        "openai": {"available": True, "active": True, "model": "gpt-4"},
        "ollama": {"available": False, "active": False},
        "custom": {"available": True, "active": False}
    },
    "embedding_providers": {
        "openai": {"available": True, "active": True, "dimension": 1536}
    }
}
```

### Logs e Auditoria
```python
# Sistema registra automaticamente:
# - Provedores inicializados
# - Trocas de provedor
# - Falhas de provedor
# - Queries processadas
```

## 🚦 Solução de Problemas

### ❌ Nenhum provedor disponível
```bash
# Verifique configurações
python examples/multi_llm_usage.py

# Verifique providers específicos:
# OpenAI: chave válida?
# Ollama: serviço rodando? Modelo baixado?
# Custom: API acessível? Headers corretos?
```

### ⚠️ Provedor específico falha
```bash
# Sistema alternará automaticamente para fallback
# Logs mostrarão o motivo da falha
```

### 🔄 Troca de provedor não funciona
```bash
# Verifique se provedor está disponível
curl -H "Authorization: Bearer key" http://localhost:9000/providers

# Verifique se o nome está correto: "openai", "ollama", "custom"
```

## 🎉 Próximos Passos

1. **Configure seu primeiro provedor** (OpenAI ou Ollama)
2. **Execute** `python multi_llm_api.py`
3. **Teste** com `examples/multi_llm_usage.py`
4. **Configure provedores adicionais** para redundância
5. **Implemente** em produção com suas APIs customizadas

---

**🎯 Resultado**: Sistema flexível que se adapta às suas necessidades, desde desenvolvimento local até produção empresarial com APIs proprietárias!
