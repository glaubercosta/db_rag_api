# 📋 Diretrizes de Organização do Projeto

## 🎯 Princípio Fundamental

**MANTER A RAIZ LIMPA** - A raiz do projeto deve conter apenas arquivos essenciais para execução e configuração.

---

## ✅ O que PODE ficar na raiz

### Arquivos Essenciais
- `api.py`, `app.py` - Pontos de entrada da aplicação
- `create_sample_db.py` - Utilitário de setup básico
- `README.md` - Documentação principal do projeto
- `requirements.txt`, `requirements-dev.txt` - Dependências
- `docker-compose.yml`, `Dockerfile*` - Configuração Docker
- `pytest.ini`, `setup.cfg` - Configuração de ferramentas
- `Makefile*` - Scripts de build

### Diretórios Principais
- `src/` - Código fonte principal
- `tests/` - Testes automatizados  
- `docs/` - Documentação completa
- `examples/` - Exemplos e demos
- `utils/` - Utilitários administrativos
- `scripts/` - Scripts de automação
- `data/` - Dados do projeto
- `docker/` - Configurações Docker

---

## ❌ O que NÃO deve ficar na raiz

### Documentação
- ❌ Relatórios de análise → `docs/analysis/`
- ❌ Logs de operações → `docs/changelogs/`
- ❌ Notas de desenvolvimento → `docs/notes/`
- ❌ Status reports → `docs/analysis/`
- ❌ Auditorias → `docs/analysis/`

### Scripts e Utilitários
- ❌ Scripts de setup → `scripts/`
- ❌ Ferramentas de debug → `utils/`
- ❌ Dados de teste → `tests/fixtures/`
- ❌ Exemplos de uso → `examples/`
- ❌ Validações → `examples/` ou `utils/`

### Arquivos Temporários
- ❌ Caches de desenvolvimento
- ❌ Logs temporários
- ❌ Arquivos de backup
- ❌ Outputs de análise

---

## 📁 Localizações Corretas

| Tipo de Arquivo | Destino | Exemplo |
|------------------|---------|---------|
| Relatórios de análise | `docs/analysis/` | `CODEBASE_AUDIT.md` |
| Guias de API | `docs/api/` | `GETTING_STARTED.md` |
| Scripts de setup | `scripts/` | `setup_dev.py` |
| Utilitários admin | `utils/` | `check_data.py` |
| Exemplos de uso | `examples/` | `validation_demo.py` |
| Dados de teste | `tests/fixtures/` | `create_test_data.py` |
| Changelogs | `docs/changelogs/` | `CHANGELOG.md` |

---

## 🚀 Benefícios da Organização

### Para Desenvolvedores
- **Navegação rápida**: Encontrar arquivos intuitivamente
- **Onboarding fácil**: Estrutura clara para novos membros
- **Manutenção simples**: Localização previsível de recursos

### Para o Projeto
- **Aparência profissional**: Impressiona colaboradores e usuários
- **Escalabilidade**: Estrutura suporta crescimento
- **Padrões consistentes**: Fácil de manter e expandir

---

## ⚡ Aplicação Imediata

**Sempre que criar novos arquivos:**

1. 🤔 **Pergunte**: "Este arquivo é essencial para executar o projeto?"
2. 📁 **Categorize**: Que tipo de arquivo é este?
3. 🎯 **Localize**: Onde ele deveria estar baseado nas diretrizes?
4. ✅ **Mova**: Para o local apropriado imediatamente

---

## 📌 Lembrete

**Esta é uma diretriz PERMANENTE**. Todos os futuros arquivos de documentação, análise, relatórios e utilitários devem seguir esta organização desde o momento da criação.

**Objetivo**: Manter o projeto sempre organizado e profissional! 🌟
