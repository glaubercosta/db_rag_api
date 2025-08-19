# 🚧 TODO - Funcionalidades Faltantes para App de Consultas em Linguagem Natural

## 📊 **Status Atual vs. Funcionalidades Necessárias**

### ✅ **O QUE JÁ EXISTE NAS APIs**

#### 🤖 **Multi-LLM API (porta 9000)**
- ✅ Suporte a múltiplos provedores (OpenAI, Ollama, APIs customizadas)
- ✅ Alternância dinâmica entre LLMs via API
- ✅ Consultas em linguagem natural com contexto RAG
- ✅ Sistema de autenticação com Bearer token
- ✅ Status do sistema e informações de provedores
- ✅ Fallback automático entre provedores

#### 🔧 **API Original (porta 8000)**  
- ✅ Inicialização de sistema com vector store
- ✅ Exploração completa de schema (tabelas, colunas, relacionamentos)
- ✅ Consultas SQL diretas e linguagem natural
- ✅ Estatísticas de banco (contagem de registros, etc.)
- ✅ Múltiplos tipos de banco (SQLite, PostgreSQL, MySQL)
- ✅ Sistema de rate limiting e autenticação

#### 🏗️ **Infraestrutura Técnica**
- ✅ RAG com FAISS vector store
- ✅ Scanning automático de schema de banco
- ✅ Integração com SQLAlchemy para múltiplos DBs
- ✅ Sistema de configuração via environment variables
- ✅ Docker/containerização pronta
- ✅ Documentação Swagger completa

---

## 🚧 **O QUE PRECISA SER DESENVOLVIDO**

### 🎨 **FRONTEND/INTERFACE DE USUÁRIO** - **ALTA PRIORIDADE**

#### 📱 **US-001 a US-015: Interface Web Completa**
```bash
# PRIORIDADE CRÍTICA - SEM ISSO NÃO HÁ APP PARA USUÁRIO FINAL
```

**1. Interface de Configuração de Conexão**
- [ ] Formulário para configurar conexões de banco
- [ ] Suporte visual para SQLite, PostgreSQL, MySQL
- [ ] Teste de conectividade com feedback visual
- [ ] Gerenciamento de múltiplas conexões salvas
- [ ] Validação de inputs e tratamento de erros

**2. Interface de Configuração de LLM**
- [ ] Formulário para configurar provedores (OpenAI, Ollama, Custom)
- [ ] Teste de conectividade com LLMs
- [ ] Seleção do provedor ativo
- [ ] Exibição de status e informações do modelo

**3. Interface Principal de Consulta**
- [ ] Caixa de texto principal para perguntas
- [ ] Histórico de consultas (sidebar ou dropdown)
- [ ] Sugestões automáticas baseadas em schema
- [ ] Loading states e indicadores de progresso
- [ ] Tratamento de erros com mensagens amigáveis

**4. Visualização de Resultados**
- [ ] Painel de resposta em linguagem natural
- [ ] Display da consulta SQL com syntax highlighting
- [ ] Tabela de resultados com paginação
- [ ] Informações de execução (tempo, linhas retornadas)
- [ ] Botões de ação (copiar, exportar, re-executar)

**5. Explorer de Schema**
- [ ] Árvore navegável de tabelas
- [ ] Visualização de colunas e tipos de dados
- [ ] Indicação de chaves primárias/estrangeiras
- [ ] Amostras de dados por tabela
- [ ] Busca de tabelas e colunas

**Tecnologias Sugeridas:**
```
- React/Next.js ou Vue.js para frontend
- TailwindCSS ou Material-UI para styling
- Monaco Editor para syntax highlighting do SQL
- Recharts ou Chart.js para gráficos futuros
- Axios para comunicação com APIs
```

### 🔗 **BACKEND: FUNCIONALIDADES FALTANTES** - **MÉDIA PRIORIDADE**

#### 📊 **Sistema de Histórico e Favoritos**
```python
# Endpoints necessários para persistência de histórico
```

**1. Histórico de Consultas**
- [ ] Banco de dados para armazenar histórico
- [ ] API endpoints: GET/POST/DELETE `/history`
- [ ] Busca no histórico por texto/data
- [ ] Limpeza automática de histórico antigo

**2. Sistema de Favoritos**
- [ ] Endpoints: GET/POST/PUT/DELETE `/favorites`
- [ ] Organização por tags/categorias
- [ ] Compartilhamento de favoritos

**Modelo de Dados Necessário:**
```sql
CREATE TABLE query_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    query_text TEXT,
    query_type VARCHAR(50),
    sql_generated TEXT,
    response TEXT,
    execution_time FLOAT,
    created_at TIMESTAMP,
    database_connection VARCHAR(255)
);

CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    name VARCHAR(255),
    query_text TEXT,
    tags TEXT[],
    created_at TIMESTAMP
);
```

#### 🔒 **Sistema de Usuários e Permissões**
```python
# Sistema básico de autenticação necessário
```

**1. Gerenciamento de Usuários**
- [ ] Modelo de dados para usuários
- [ ] Autenticação (login/logout)
- [ ] Sessões de usuário
- [ ] Perfis de permissão (admin, user, viewer)

**2. Controle de Acesso a Conexões**
- [ ] Associação usuário-conexões
- [ ] Validação de permissões por endpoint
- [ ] Log de auditoria de consultas

### 📈 **EXPORTAÇÃO E RELATÓRIOS** - **MÉDIA PRIORIDADE**

#### 📄 **Sistema de Export**
```python
# Novos endpoints para diferentes formatos
```

**1. Endpoints de Export**
- [ ] `/export/csv` - Export para CSV
- [ ] `/export/excel` - Export para Excel (com openpyxl)
- [ ] `/export/pdf` - Export para PDF (com reportlab)
- [ ] `/export/sql` - Export apenas da consulta SQL

**2. Funcionalidades de Export**
- [ ] Nomeação inteligente de arquivos
- [ ] Formatação correta de encoding (UTF-8)
- [ ] Compressão para resultados grandes
- [ ] Histórico de exports realizados

### 📊 **VISUALIZAÇÃO E GRÁFICOS** - **BAIXA PRIORIDADE**

#### 🎨 **Sistema de Gráficos Automáticos**
```python
# Análise dos dados para sugerir visualizações
```

**1. Detecção Automática de Gráficos**
- [ ] Análise de tipos de dados para sugerir gráficos
- [ ] Geração automática de configuração de gráficos
- [ ] Endpoint `/visualize` para gerar sugestões de chart

**2. API de Visualização**
- [ ] Retorno de dados formatados para gráficos
- [ ] Configurações de gráficos (cores, labels, etc.)
- [ ] Export de gráficos como imagem

### ⚙️ **CONFIGURAÇÕES E PERSONALIZAÇÃO** - **BAIXA PRIORIDADE**

#### 🛠️ **Sistema de Configuração de Usuário**
```python
# Persistência de preferências por usuário
```

**1. Configurações Persistentes**
- [ ] Modelo para user preferences
- [ ] Endpoints GET/PUT `/user/settings`
- [ ] Configurações: tema, idioma, formato de data, etc.

**2. Configurações de Sistema**
- [ ] Rate limiting configurável por usuário
- [ ] Timeout de consulta configurável
- [ ] Limites de resultado por perfil

---

## 📋 **ROADMAP DE DESENVOLVIMENTO**

### 🎯 **FASE 1: MVP (Prioridade CRÍTICA) - 4-6 semanas**
```
Objetivo: App funcional básico para usuários finais
```

**Semana 1-2: Setup e Configuração**
- [ ] Setup projeto frontend (React/Next.js)
- [ ] Configuração de comunicação com APIs existentes
- [ ] Interface de configuração de conexão de banco
- [ ] Interface de configuração de LLM

**Semana 3-4: Interface Principal**
- [ ] Caixa de consulta principal
- [ ] Exibição de resultados (texto + SQL + tabela)
- [ ] Explorer básico de schema
- [ ] Tratamento de erros

**Semana 5-6: Polimento e Testes**
- [ ] Responsividade mobile
- [ ] Testes de usabilidade
- [ ] Documentação de usuário
- [ ] Deploy de produção

### 🚀 **FASE 2: Funcionalidades Essenciais (Prioridade ALTA) - 3-4 semanas**

**Semana 7-8: Histórico e Persistência**
- [ ] Implementar sistema de histórico no backend
- [ ] Interface de histórico de consultas
- [ ] Sistema básico de favoritos
- [ ] Busca no histórico

**Semana 9-10: Melhorias UX**
- [ ] Sugestões automáticas de consulta
- [ ] Follow-up de consultas
- [ ] Melhorias na visualização de resultados
- [ ] Sistema de export básico (CSV)

### ⭐ **FASE 3: Funcionalidades Avançadas (Prioridade MÉDIA) - 4-6 semanas**

**Semana 11-13: Usuários e Permissões**
- [ ] Sistema básico de usuários
- [ ] Controle de acesso a conexões
- [ ] Perfis de permissão
- [ ] Auditoria básica

**Semana 14-16: Visualização e Export**
- [ ] Sistema de gráficos automáticos
- [ ] Export avançado (Excel, PDF)
- [ ] Dashboard de estatísticas
- [ ] Configurações personalizadas

### 💎 **FASE 4: Funcionalidades Premium (Prioridade BAIXA) - 2-4 semanas**

**Semana 17-20: Recursos Avançados**
- [ ] Comparação de LLMs lado a lado
- [ ] Relatórios automáticos
- [ ] Alertas inteligentes
- [ ] Colaboração em equipe

---

## 🔧 **ESPECIFICAÇÕES TÉCNICAS DETALHADAS**

### 🏗️ **Arquitetura Proposta**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend APIs   │    │   Database      │
│   (React/Next)  │◄──►│  (FastAPI)       │◄──►│   (PostgreSQL)  │
│                 │    │                  │    │                 │
│ - UI Components │    │ - Multi-LLM API  │    │ - User Data     │
│ - State Mgmt    │    │ - Original API   │    │ - Query History │
│ - API Client    │    │ - New Endpoints  │    │ - Connections   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 📊 **Estimativa de Esforço**

| **Componente** | **Complexidade** | **Tempo Estimado** | **Prioridade** |
|----------------|------------------|--------------------|----------------|
| Frontend UI | Alta | 6-8 semanas | CRÍTICA |
| Sistema Histórico | Média | 1-2 semanas | ALTA |
| Export System | Baixa | 1 semana | MÉDIA |
| Gráficos | Média | 2-3 semanas | BAIXA |
| Usuários/Permissões | Alta | 3-4 semanas | MÉDIA |
| Funcionalidades Premium | Baixa | 2-4 semanas | BAIXA |

### 💰 **Recursos Necessários**

**Equipe Mínima:**
- 1 Desenvolvedor Frontend (React/TypeScript)
- 1 Desenvolvedor Backend (Python/FastAPI) 
- 1 UX/UI Designer (part-time)
- 1 QA Tester (part-time)

**Infraestrutura:**
- Servidor para frontend (Vercel/Netlify)
- Database PostgreSQL (AWS RDS/DigitalOcean)
- APIs já existentes (mantém infraestrutura atual)

---

## 🎯 **DEFINIÇÃO DE SUCESSO**

### 📈 **Métricas de MVP (Fase 1)**
- [ ] Usuário consegue conectar a banco em < 2 minutos
- [ ] Consulta em linguagem natural retorna em < 10 segundos
- [ ] Interface responsiva funciona em mobile
- [ ] 0 crashes críticos em produção
- [ ] Documentação completa para usuário final

### 🏆 **Métricas de Produto Completo**
- [ ] 90% das consultas dos usuários são bem-sucedidas
- [ ] Tempo médio de resposta < 5 segundos
- [ ] Usuários fazem >10 consultas por sessão
- [ ] Export de resultados usado por >50% dos usuários
- [ ] NPS > 8.0 com usuários beta

---

## 📞 **PRÓXIMOS PASSOS IMEDIATOS**

### ✅ **TODO para ESTA SEMANA**
1. [ ] **Decisão de Stack Tecnológico**
   - Definir: React vs Vue vs Angular para frontend
   - Definir: TailwindCSS vs Material-UI vs Ant Design
   - Definir: PostgreSQL vs MySQL para dados de usuário

2. [ ] **Setup do Projeto Frontend**
   - Criar repositório separado ou monorepo
   - Configurar estrutura inicial
   - Setup de comunicação com APIs existentes

3. [ ] **Prototipagem Rápida**
   - Wireframes das telas principais
   - Protótipo navegável (Figma)
   - Validação com stakeholders

4. [ ] **Definição de UI/UX**
   - Criar design system básico
   - Definir paleta de cores e tipografia
   - Componentes principais (botões, inputs, cards)

### 🎯 **TODO para PRÓXIMO MÊS**
1. [ ] **Implementação do MVP**
2. [ ] **Testes com usuários beta**
3. [ ] **Documentação completa**
4. [ ] **Deploy em produção**

---

*Documento criado em: ${new Date().toLocaleDateString('pt-BR')}*  
*Status: Planejamento inicial*  
*Próxima revisão: Após Fase 1*
