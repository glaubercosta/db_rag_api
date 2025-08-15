#!/usr/bin/env python3
"""
DB RAG API - Sistema RAG para Consultas de Banco de Dados
Ponto de entrada principal da aplicacao
"""

import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Funcao principal da aplicacao"""
    print("Iniciando DB RAG API...")
    
    try:
        from src.rag_system import DatabaseRAGSystem
        from src.config import DatabaseConfig, OpenAIConfig, RAGConfig
        
        # Configurar sistema com todas as configurações necessárias
        db_config = DatabaseConfig.from_env()
        openai_config = OpenAIConfig.from_env()
        rag_config = RAGConfig.from_env()
        
        rag = DatabaseRAGSystem(db_config, openai_config, rag_config)
        
        print("\nSistema RAG inicializado com sucesso!")
        print("Para usar o sistema, importe as classes necessarias:")
        print("   from src.rag_system import DatabaseRAGSystem")
        print("   from src.config import DatabaseConfig, OpenAIConfig, RAGConfig")
        
        return rag
        
    except ImportError as e:
        print(f"Erro ao importar modulos: {e}")
        print("Verifique se todas as dependencias estao instaladas:")
        print("   pip install -r requirements.txt")
        return None
    except Exception as e:
        print(f"Erro ao inicializar sistema: {e}")
        return None

if __name__ == "__main__":
    main()
