#!/bin/bash

# 🚀 Script de Setup Automático - Frontend TDD
# Execute: ./setup-tdd-frontend.sh

set -e  # Exit on any error

echo "🚀 Iniciando setup do Frontend com TDD..."
echo "📁 Diretório atual: $(pwd)"

# Verificar se estamos no diretório correto
if [[ ! -f "multi_llm_api.py" ]]; then
    echo "❌ Execute este script no diretório raiz do projeto db_rag_api"
    exit 1
fi

# 1. Criar diretório frontend
echo "📁 Criando diretório frontend..."
mkdir -p frontend
cd frontend

# 2. Inicializar projeto Next.js
echo "⚡ Inicializando projeto Next.js com TypeScript..."
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-git

# 3. Instalar dependências de desenvolvimento
echo "📦 Instalando dependências de teste..."
npm install --save-dev \
    @testing-library/react \
    @testing-library/jest-dom \
    @testing-library/user-event \
    jest \
    jest-environment-jsdom \
    @types/jest

# 4. Instalar dependências de produção
echo "📦 Instalando dependências de produção..."
npm install \
    axios \
    @types/axios \
    monaco-editor \
    @monaco-editor/react \
    react-icons \
    lucide-react \
    file-saver \
    @types/file-saver \
    xlsx

# 5. Criar configuração do Jest
echo "⚙️  Configurando Jest..."
cat > jest.config.js << 'EOF'
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleDirectories: ['node_modules', '<rootDir>/'],
  testEnvironment: 'jest-environment-jsdom',
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
EOF

# 6. Criar setup do Jest
echo "⚙️  Criando jest.setup.js..."
cat > jest.setup.js << 'EOF'
import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    query: {},
    pathname: '/',
  }),
}))

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})
EOF

# 7. Criar estrutura de pastas
echo "📁 Criando estrutura de pastas..."
mkdir -p __tests__/{components,integration,services,setup}
mkdir -p src/{components/ui,components/forms,services,hooks,utils,types}

# 8. Atualizar package.json com scripts
echo "📝 Atualizando scripts no package.json..."
npm pkg set scripts.test="jest"
npm pkg set scripts.test:watch="jest --watch"
npm pkg set scripts.test:coverage="jest --coverage"
npm pkg set scripts.test:ci="jest --coverage --ci --watchAll=false"

# 9. Criar primeiro teste
echo "🧪 Criando primeiro teste..."
cat > __tests__/setup/app.test.tsx << 'EOF'
import { render, screen } from '@testing-library/react'
import Home from '@/app/page'

describe('Application Setup', () => {
  test('should render main application without crashing', () => {
    render(<Home />)
    
    const main = screen.getByRole('main')
    expect(main).toBeInTheDocument()
  })
  
  test('should have correct application title', () => {
    render(<Home />)
    
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('Database Query Assistant')
  })
  
  test('should display welcome message', () => {
    render(<Home />)
    
    const welcomeText = screen.getByText(/welcome to your natural language database assistant/i)
    expect(welcomeText).toBeInTheDocument()
  })
  
  test('should have navigation to database connection', () => {
    render(<Home />)
    
    const connectButton = screen.getByRole('button', { name: /connect to database/i })
    expect(connectButton).toBeInTheDocument()
  })
})
EOF

# 10. Criar componente Button
echo "🎨 Criando componente Button..."
cat > src/components/ui/Button.tsx << 'EOF'
import { ButtonHTMLAttributes, ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  children: ReactNode
}

export function Button({ 
  variant = 'primary', 
  size = 'md', 
  children, 
  className = '',
  ...props 
}: ButtonProps) {
  const baseClasses = 'font-bold rounded transition-colors'
  
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50'
  }
  
  const sizeClasses = {
    sm: 'py-1 px-3 text-sm',
    md: 'py-2 px-4',
    lg: 'py-3 px-6 text-lg'
  }
  
  return (
    <button 
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
EOF

# 11. Criar página principal
echo "🏠 Criando página principal..."
cat > src/app/page.tsx << 'EOF'
import { Button } from '@/components/ui/Button'

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Database Query Assistant
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Welcome to your natural language database assistant
          </p>
          <Button size="lg">
            Connect to Database
          </Button>
        </div>
      </div>
    </main>
  )
}
EOF

# 12. Criar arquivo de tipos
echo "📝 Criando tipos TypeScript..."
cat > src/types/api.ts << 'EOF'
// Tipos para comunicação com APIs backend

export interface DatabaseConnection {
  id: string
  name: string
  type: 'sqlite' | 'postgresql' | 'mysql'
  connectionString: string
  isActive: boolean
}

export interface QueryRequest {
  query: string
  queryType: 'natural_language' | 'sql'
  limit?: number
  includeExplanation?: boolean
}

export interface QueryResponse {
  success: boolean
  query: string
  sqlQuery?: string
  results: any[]
  rowCount: number
  executionTime: number
  explanation?: string
  error?: string
}

export interface LLMProvider {
  name: string
  type: 'openai' | 'ollama' | 'custom'
  active: boolean
  config: {
    apiKey?: string
    baseUrl?: string
    model?: string
  }
}
EOF

# 13. Criar service para API
echo "🔧 Criando service para API..."
cat > src/services/api.ts << 'EOF'
import axios from 'axios'
import { QueryRequest, QueryResponse, DatabaseConnection, LLMProvider } from '@/types/api'

// URLs das APIs
const ORIGINAL_API_URL = process.env.NEXT_PUBLIC_ORIGINAL_API_URL || 'http://localhost:8000'
const MULTI_LLM_API_URL = process.env.NEXT_PUBLIC_MULTI_LLM_API_URL || 'http://localhost:9000'

// API Key padrão (deve ser configurável)
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'dev-api-key-12345'

// Configuração do axios
const originalApi = axios.create({
  baseURL: ORIGINAL_API_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json',
  },
})

const multiLlmApi = axios.create({
  baseURL: MULTI_LLM_API_URL,
  headers: {
    'Authorization': `Bearer dev-multi-llm-key-12345`,
    'Content-Type': 'application/json',
  },
})

export class ApiService {
  // Testar conectividade
  static async testConnection(): Promise<boolean> {
    try {
      await originalApi.get('/health')
      return true
    } catch {
      return false
    }
  }

  // Executar query
  static async executeQuery(request: QueryRequest): Promise<QueryResponse> {
    const { data } = await originalApi.post('/query', request)
    return data
  }

  // Obter schema do banco
  static async getSchema() {
    const { data } = await originalApi.post('/schema', {})
    return data
  }

  // Listar provedores LLM
  static async getProviders(): Promise<LLMProvider[]> {
    const { data } = await multiLlmApi.get('/providers')
    return data
  }

  // Alternar provedor LLM
  static async switchProvider(provider: string, type: 'llm' | 'embedding') {
    const { data } = await multiLlmApi.post('/switch-provider', {
      provider,
      type,
    })
    return data
  }
}
EOF

# 14. Criar arquivo .env.local
echo "🔑 Criando arquivo .env.local..."
cat > .env.local << 'EOF'
# URLs das APIs backend
NEXT_PUBLIC_ORIGINAL_API_URL=http://localhost:8000
NEXT_PUBLIC_MULTI_LLM_API_URL=http://localhost:9000

# API Keys
NEXT_PUBLIC_API_KEY=dev-api-key-12345
NEXT_PUBLIC_MULTI_LLM_API_KEY=dev-multi-llm-key-12345
EOF

# 15. Atualizar .gitignore
echo "📝 Atualizando .gitignore..."
cat >> .gitignore << 'EOF'

# Test coverage
coverage/

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local
EOF

# 16. Executar testes iniciais
echo "🧪 Executando testes iniciais..."
npm test -- --passWithNoTests

echo ""
echo "✅ Setup concluído com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "   1. cd frontend"
echo "   2. npm run dev (para iniciar servidor de desenvolvimento)"
echo "   3. npm run test:watch (para executar testes em modo watch)"
echo ""
echo "🌐 URLs importantes:"
echo "   - Frontend: http://localhost:3000"
echo "   - API Original: http://localhost:8000"
echo "   - Multi-LLM API: http://localhost:9000"
echo ""
echo "🎯 Versão atual: v0.1.0 (Foundation Setup)"
echo "🚀 Próxima versão: v0.2.0 (Database Connection UI)"
echo ""
echo "Happy coding! 🚀"
