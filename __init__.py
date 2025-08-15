"""
Sistema RAG para Banco de Dados

Um sistema modular para consultas em linguagem natural sobre bancos de dados
usando Retrieval Augmented Generation (RAG) com LangChain e OpenAI.

Principais módulos:
- config: Configurações do sistema
- models: Modelos de dados
- database_scanner: Scanner de banco de dados
- vector_store_manager: Gerenciador do banco vetorial
- sql_agent: Agente SQL com LLM
- rag_system: Sistema principal integrado
"""

__version__ = "1.0.0"
__author__ = "Sistema RAG DB"

# Importações principais para facilitar o uso
# (Comentadas para evitar problemas durante testes)
# from .config import DatabaseConfig, OpenAIConfig, RAGConfig
# from .rag_system import DatabaseRAGSystem, create_system_from_env

__all__ = [
    # "DatabaseConfig",
    # "OpenAIConfig",
    # "RAGConfig",
    # "DatabaseRAGSystem",
    # "create_system_from_env"
]
