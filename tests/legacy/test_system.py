"""
Teste rápido do sistema RAG refatorado
Execute este arquivo para testar se tudo está funcionando
"""

import os

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("Testando importações dos módulos...")
    
    try:
        from config import DatabaseConfig, OpenAIConfig, RAGConfig
        print("✓ Módulo config importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar config: {e}")
        return False
    
    try:
        from models import DatabaseSchema, TableInfo, ColumnInfo
        print("✓ Módulo models importado com sucesso")  
    except Exception as e:
        print(f"✗ Erro ao importar models: {e}")
        return False
    
    try:
        from database_scanner import DatabaseScanner
        print("✓ Módulo database_scanner importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar database_scanner: {e}")
        return False
    
    try:
        from vector_store_manager import VectorStoreManager
        print("✓ Módulo vector_store_manager importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar vector_store_manager: {e}")
        return False
    
    try:
        from sql_agent import SQLAgent, RAGQueryProcessor
        print("✓ Módulo sql_agent importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar sql_agent: {e}")
        return False
    
    try:
        from rag_system import DatabaseRAGSystem, create_system_from_env
        print("✓ Módulo rag_system importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar rag_system: {e}")
        return False
    
    return True


def test_config():
    """Testa criação de configurações"""
    print("\nTestando configurações...")
    
    from config import DatabaseConfig, OpenAIConfig, RAGConfig
    
    # Teste com valores manuais
    try:
        db_config = DatabaseConfig(
            url="sqlite:///test.db",
            type="sqlite"
        )
        print(f"✓ DatabaseConfig criado: {db_config.type}")
    except Exception as e:
        print(f"✗ Erro ao criar DatabaseConfig: {e}")
        return False
    
    try:
        openai_config = OpenAIConfig(
            api_key="test-key",
            model="gpt-4"
        )
        print(f"✓ OpenAIConfig criado: {openai_config.model}")
    except Exception as e:
        print(f"✗ Erro ao criar OpenAIConfig: {e}")
        return False
    
    try:
        rag_config = RAGConfig()
        print(f"✓ RAGConfig criado: k={rag_config.similarity_search_k}")
    except Exception as e:
        print(f"✗ Erro ao criar RAGConfig: {e}")
        return False
    
    return True


def test_models():
    """Testa modelos de dados"""
    print("\nTestando modelos de dados...")
    
    from models import ColumnInfo, TableInfo, DatabaseSchema
    
    try:
        # Cria uma coluna
        col = ColumnInfo(
            name="id", 
            data_type="integer", 
            is_nullable=False,
            is_primary_key=True
        )
        print(f"✓ ColumnInfo criado: {col.name}")
        
        # Cria uma tabela
        table = TableInfo(
            name="users",
            columns=[col],
            primary_keys=["id"],
            foreign_keys=[]
        )
        print(f"✓ TableInfo criado: {table.name}")
        
        # Cria schema
        schema = DatabaseSchema(tables=[table])
        print(f"✓ DatabaseSchema criado com {len(schema.tables)} tabela(s)")
        
        # Testa conversão para texto
        text = schema.to_text()
        print(f"✓ Schema convertido para texto: {len(text)} caracteres")
        
    except Exception as e:
        print(f"✗ Erro ao testar models: {e}")
        return False
    
    return True


def show_structure():
    """Mostra estrutura do projeto"""
    print("\n" + "="*50)
    print("ESTRUTURA DO PROJETO REFATORADO")
    print("="*50)
    
    files_info = {
        "config.py": "Configurações centralizadas",
        "models.py": "Modelos de dados (TableInfo, ColumnInfo, etc)",
        "database_scanner.py": "Scanner para extração de metadados",
        "vector_store_manager.py": "Gerenciador do banco vetorial FAISS",
        "sql_agent.py": "Agente SQL com LLM",
        "rag_system.py": "Sistema principal que integra tudo",
        "examples.py": "Exemplos de uso",
        "main.py": "Ponto de entrada (atualizado)",
        "requirements.txt": "Dependências",
        ".env.example": "Exemplo de configuração",
        "README.md": "Documentação completa"
    }
    
    for file, description in files_info.items():
        print(f"{file:25} - {description}")


def main():
    print("=== TESTE DO SISTEMA RAG REFATORADO ===\n")
    
    # Testa importações
    if not test_imports():
        print("\n❌ Falha nos testes de importação")
        return
    
    # Testa configurações  
    if not test_config():
        print("\n❌ Falha nos testes de configuração")
        return
    
    # Testa modelos
    if not test_models():
        print("\n❌ Falha nos testes de modelos")
        return
    
    print("\n✅ TODOS OS TESTES PASSARAM!")
    print("O sistema foi refatorado com sucesso.")
    
    # Mostra estrutura
    show_structure()
    
    print("\n" + "="*50)
    print("PRÓXIMOS PASSOS")
    print("="*50)
    print("1. Configure suas variáveis de ambiente no arquivo .env")
    print("2. Execute: python examples.py")
    print("3. Ou use o sistema em seu próprio código:")
    print("   from rag_system import create_system_from_env")
    print("   system = create_system_from_env()")
    print("   system.initialize()")
    print("   result = system.ask('Sua pergunta aqui')")


if __name__ == "__main__":
    main()
