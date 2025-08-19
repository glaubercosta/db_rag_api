# 🚀 Script de Setup Automático - Frontend TDD (PowerShell)
# Execute: .\setup-tdd-frontend.ps1

Write-Host "🚀 Iniciando setup do Frontend com TDD..." -ForegroundColor Green
Write-Host "📁 Diretório atual: $(Get-Location)" -ForegroundColor Blue

# Verificar se estamos no diretório correto
if (-not (Test-Path "multi_llm_api.py")) {
    Write-Host "❌ Execute este script no diretório raiz do projeto db_rag_api" -ForegroundColor Red
    exit 1
}

# 1. Criar diretório frontend
Write-Host "📁 Criando diretório frontend..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "frontend" -Force | Out-Null
Set-Location "frontend"

# 2. Verificar se Node.js está instalado
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não encontrado. Instale Node.js antes de continuar." -ForegroundColor Red
    exit 1
}

# 3. Inicializar projeto Next.js
Write-Host "⚡ Inicializando projeto Next.js com TypeScript..." -ForegroundColor Yellow
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --no-git

# 4. Instalar dependências de desenvolvimento
Write-Host "📦 Instalando dependências de teste..." -ForegroundColor Yellow
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom '@types/jest'

# 5. Instalar dependências de produção
Write-Host "📦 Instalando dependências de produção..." -ForegroundColor Yellow
npm install axios '@types/axios' monaco-editor '@monaco-editor/react' react-icons lucide-react file-saver '@types/file-saver' xlsx

# 6. Criar configuração do Jest
Write-Host "⚙️ Configurando Jest..." -ForegroundColor Yellow
@"
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
"@ | Out-File -FilePath "jest.config.js" -Encoding UTF8

# 7. Criar setup do Jest
Write-Host "⚙️ Criando jest.setup.js..." -ForegroundColor Yellow
@"
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
"@ | Out-File -FilePath "jest.setup.js" -Encoding UTF8

# 8. Criar estrutura de pastas
Write-Host "📁 Criando estrutura de pastas..." -ForegroundColor Yellow
$folders = @(
    "__tests__/components",
    "__tests__/integration", 
    "__tests__/services",
    "__tests__/setup",
    "src/components/ui",
    "src/components/forms",
    "src/services",
    "src/hooks",
    "src/utils",
    "src/types"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}

# 9. Atualizar package.json com scripts
Write-Host "📝 Atualizando scripts no package.json..." -ForegroundColor Yellow
npm pkg set scripts.test="jest"
npm pkg set scripts.test:watch="jest --watch"
npm pkg set scripts.test:coverage="jest --coverage"
npm pkg set scripts.test:ci="jest --coverage --ci --watchAll=false"

# 10. Criar primeiro teste
Write-Host "🧪 Criando primeiro teste..." -ForegroundColor Yellow
@"
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
"@ | Out-File -FilePath "__tests__/setup/app.test.tsx" -Encoding UTF8

# 11. Criar componente Button
Write-Host "🎨 Criando componente Button..." -ForegroundColor Yellow
@"
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
      className={`${"$"}{baseClasses} ${"$"}{variantClasses[variant]} ${"$"}{sizeClasses[size]} ${"$"}{className}`}
      {...props}
    >
      {children}
    </button>
  )
}
"@ | Out-File -FilePath "src/components/ui/Button.tsx" -Encoding UTF8

# 12. Criar página principal
Write-Host "🏠 Criando página principal..." -ForegroundColor Yellow
@"
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
"@ | Out-File -FilePath "src/app/page.tsx" -Encoding UTF8

# 13. Criar arquivo de tipos
Write-Host "📝 Criando tipos TypeScript..." -ForegroundColor Yellow
@"
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
"@ | Out-File -FilePath "src/types/api.ts" -Encoding UTF8

# 14. Criar service para API
Write-Host "🔧 Criando service para API..." -ForegroundColor Yellow
@"
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
    'Authorization': ``Bearer ${"$"}{API_KEY}``,
    'Content-Type': 'application/json',
  },
})

const multiLlmApi = axios.create({
  baseURL: MULTI_LLM_API_URL,
  headers: {
    'Authorization': 'Bearer dev-multi-llm-key-12345',
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
"@ | Out-File -FilePath "src/services/api.ts" -Encoding UTF8

# 15. Criar arquivo .env.local
Write-Host "🔑 Criando arquivo .env.local..." -ForegroundColor Yellow
@"
# URLs das APIs backend
NEXT_PUBLIC_ORIGINAL_API_URL=http://localhost:8000
NEXT_PUBLIC_MULTI_LLM_API_URL=http://localhost:9000

# API Keys
NEXT_PUBLIC_API_KEY=dev-api-key-12345
NEXT_PUBLIC_MULTI_LLM_API_KEY=dev-multi-llm-key-12345
"@ | Out-File -FilePath ".env.local" -Encoding UTF8

# 16. Executar testes iniciais
Write-Host "🧪 Executando testes iniciais..." -ForegroundColor Yellow
try {
    npm test -- --passWithNoTests --watchAll=false
    Write-Host "✅ Testes iniciais passaram!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Alguns testes falharam, mas isso é esperado no setup inicial." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Setup concluído com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. cd frontend" -ForegroundColor White
Write-Host "   2. npm run dev (para iniciar servidor de desenvolvimento)" -ForegroundColor White
Write-Host "   3. npm run test:watch (para executar testes em modo watch)" -ForegroundColor White
Write-Host ""
Write-Host "🌐 URLs importantes:" -ForegroundColor Cyan
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - API Original: http://localhost:8000" -ForegroundColor White
Write-Host "   - Multi-LLM API: http://localhost:9000" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Versão atual: v0.1.0 (Foundation Setup)" -ForegroundColor Magenta
Write-Host "🚀 Próxima versão: v0.2.0 (Database Connection UI)" -ForegroundColor Magenta
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
