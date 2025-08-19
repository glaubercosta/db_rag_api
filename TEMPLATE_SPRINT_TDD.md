# 📋 Template de Sprint TDD - Database Query Assistant

## 🎯 **v0.X.0 - [Nome da Feature]** (Semana X)

### 📊 **Contexto e Objetivo**
**Persona:** [Analista de Negócios / Desenvolvedor / Executivo]  
**História de Usuário:** [Referência à US-XXX]  
**Problema a Resolver:** [Descrição do problema atual]  
**Valor Entregue:** [Benefício para o usuário final]  

---

### 🧪 **FASE RED - Testes Falhando**

#### 📝 **Testes Unitários**
```typescript
// __tests__/components/ComponentName.test.tsx
describe('ComponentName', () => {
  test('should render without crashing', () => {
    // Arrange
    
    // Act
    
    // Assert
  })
  
  test('should handle user interaction correctly', () => {
    // Arrange
    
    // Act
    
    // Assert
  })
  
  test('should display error states appropriately', () => {
    // Arrange
    
    // Act
    
    // Assert
  })
})
```

#### 🔗 **Testes de Integração**
```typescript
// __tests__/integration/feature-integration.test.tsx
describe('Feature Integration', () => {
  test('should integrate with backend API correctly', () => {
    // Mock API responses
    
    // Test complete user flow
    
    // Verify API calls and UI updates
  })
})
```

#### 🎭 **Testes E2E (para features críticas)**
```typescript
// __tests__/e2e/feature-e2e.test.ts
describe('Feature E2E', () => {
  test('should complete full user journey', () => {
    // Navigate to feature
    
    // Perform user actions
    
    // Verify results
  })
})
```

#### ⚡ **Executar Testes (Devem Falhar)**
```bash
npm test
# Resultado esperado: ❌ Testes falham porque funcionalidade não existe ainda
```

---

### 🟢 **FASE GREEN - Implementação Mínima**

#### 🎨 **Componentes React**
```typescript
// src/components/FeatureComponent.tsx
interface FeatureComponentProps {
  // Props interface
}

export function FeatureComponent({ /* props */ }: FeatureComponentProps) {
  // Implementação mínima para passar nos testes
  return (
    <div>
      {/* JSX mínimo */}
    </div>
  )
}
```

#### 🔧 **Services/Hooks**
```typescript
// src/services/feature-service.ts
export class FeatureService {
  static async performAction() {
    // Implementação mínima
  }
}

// src/hooks/useFeature.ts
export function useFeature() {
  // Custom hook se necessário
}
```

#### ✅ **Executar Testes (Devem Passar)**
```bash
npm test
# Resultado esperado: ✅ Todos os testes passam
```

---

### 🔵 **FASE REFACTOR - Melhorias**

#### 🎯 **Refatorações Planejadas**
- [ ] Extrair componentes reutilizáveis
- [ ] Melhorar performance (memoização, lazy loading)
- [ ] Adicionar tratamento robusto de erros
- [ ] Melhorar acessibilidade (ARIA labels, keyboard navigation)
- [ ] Otimizar bundle size
- [ ] Adicionar animações/transições suaves

#### 🧹 **Code Quality**
```bash
# Executar linting
npm run lint

# Executar testes com coverage
npm run test:coverage

# Verificar performance bundle
npm run build && npm run analyze
```

#### ✅ **Verificar que Testes Ainda Passam**
```bash
npm test
# Resultado esperado: ✅ Todos os testes continuam passando
```

---

### 📊 **Critérios de Aceitação**

#### ✅ **Funcionalidade**
- [ ] [Critério específico 1]
- [ ] [Critério específico 2]
- [ ] [Critério específico 3]
- [ ] Tratamento de erros implementado
- [ ] Loading states funcionam corretamente

#### 🎨 **UI/UX**
- [ ] Interface responsiva (mobile + desktop)
- [ ] Acessibilidade básica (WCAG 2.1 AA)
- [ ] Feedback visual adequado
- [ ] Navegação intuitiva
- [ ] Consistent com design system

#### ⚡ **Performance**
- [ ] Componente carrega em < 1s
- [ ] Não bloqueia a UI durante operações
- [ ] Bundle size não aumenta significativamente
- [ ] Sem memory leaks

#### 🧪 **Testes**
- [ ] Cobertura de testes > 80%
- [ ] Testes unitários passam
- [ ] Testes de integração passam
- [ ] Testes E2E passam (se aplicável)

---

### 🚀 **Deploy e Validação**

#### 📦 **Build e Deploy**
```bash
# Build de produção
npm run build

# Deploy para staging
# (comando específico do ambiente)

# Verificar se aplicação funciona em staging
# curl ou testes automáticos
```

#### 👥 **Validação com Usuários**
- [ ] Demo para stakeholders realizados
- [ ] Feedback coletado e documentado
- [ ] Ajustes críticos implementados
- [ ] Sign-off dos usuários obtido

#### 📈 **Métricas de Sucesso**
- **Performance:** [Métrica específica, ex: tempo de carregamento]
- **Usabilidade:** [Métrica específica, ex: taxa de conclusão de tarefa]
- **Qualidade:** [Métrica específica, ex: número de bugs encontrados]
- **Satisfação:** [Métrica específica, ex: NPS ou rating]

---

### 🏷️ **Release Notes v0.X.0**

#### 🆕 **Novas Funcionalidades**
- [Descrição da funcionalidade principal]
- [Melhorias de UX implementadas]
- [Integrações adicionadas]

#### 🐛 **Correções**
- [Bugs corrigidos, se houver]

#### ⚡ **Melhorias**
- [Melhorias de performance]
- [Refatorações importantes]

#### 🔧 **Para Desenvolvedores**
- [Mudanças na API]
- [Novas dependências]
- [Breaking changes, se houver]

---

### 🎯 **Preparação para Próxima Versão**

#### 📋 **Retrospectiva**
**O que funcionou bem:**
- [Pontos positivos do sprint]

**O que pode melhorar:**
- [Pontos de melhoria identificados]

**Lições aprendidas:**
- [Conhecimentos adquiridos]

#### 🚀 **Próximos Passos**
- [ ] Planejar v0.X+1.0
- [ ] Escrever testes para próxima feature
- [ ] Atualizar documentação
- [ ] Comunicar release para usuários

---

## 📝 **Exemplo Concreto: v0.2.0 - Database Connection UI**

### 📊 **Contexto e Objetivo**
**Persona:** Analista de Negócios  
**História de Usuário:** US-001 - Configurar Conexão com Banco de Dados  
**Problema a Resolver:** Usuário não consegue conectar sua base de dados ao sistema  
**Valor Entregue:** Usuário pode configurar conexão SQLite/PostgreSQL/MySQL em < 2 minutos  

### 🧪 **FASE RED - Testes Falhando**

```typescript
// __tests__/components/DatabaseConnectionForm.test.tsx
describe('DatabaseConnectionForm', () => {
  test('should render connection form with all database types', () => {
    render(<DatabaseConnectionForm />)
    
    expect(screen.getByRole('form')).toBeInTheDocument()
    expect(screen.getByText('SQLite')).toBeInTheDocument()
    expect(screen.getByText('PostgreSQL')).toBeInTheDocument()
    expect(screen.getByText('MySQL')).toBeInTheDocument()
  })
  
  test('should validate required fields before submission', () => {
    render(<DatabaseConnectionForm />)
    
    const submitButton = screen.getByRole('button', { name: /connect/i })
    fireEvent.click(submitButton)
    
    expect(screen.getByText(/database type is required/i)).toBeInTheDocument()
  })
  
  test('should show success message on valid connection', async () => {
    // Mock successful API response
    jest.spyOn(ApiService, 'testDatabaseConnection').mockResolvedValue(true)
    
    render(<DatabaseConnectionForm />)
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/database type/i), { target: { value: 'sqlite' } })
    fireEvent.change(screen.getByLabelText(/file path/i), { target: { value: '/path/to/db.sqlite' } })
    
    // Submit
    fireEvent.click(screen.getByRole('button', { name: /test connection/i }))
    
    await waitFor(() => {
      expect(screen.getByText(/connection successful/i)).toBeInTheDocument()
    })
  })
})
```

### ✅ **Critérios de Aceitação Específicos**
- [ ] Formulário renderiza com 3 opções de banco (SQLite, PostgreSQL, MySQL)
- [ ] Validação client-side previne submissão com campos vazios
- [ ] Botão "Test Connection" chama API e exibe resultado
- [ ] Estados de loading são mostrados durante teste
- [ ] Mensagens de erro são claras e acionáveis
- [ ] Configuração é salva após conexão bem-sucedida

### 📈 **Métricas de Sucesso Específicas**
- **Performance:** Formulário carrega em < 500ms
- **Usabilidade:** 90% dos usuários conectam banco na primeira tentativa
- **Qualidade:** 0 bugs críticos em produção
- **Satisfação:** Rating > 4.0/5.0 dos usuários beta

---

*Template criado em: 16 de Agosto de 2025*  
*Metodologia: Test-Driven Development*  
*Uso: Copiar e adaptar para cada nova versão/sprint*
