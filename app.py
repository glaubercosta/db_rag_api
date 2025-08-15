#!/usr/bin/env python3
"""
DB RAG API - Sistema RAG para Consultas de Banco de Dados
Ponto de entrada principal da aplicacao
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Funcao principal da aplicacao"""
    print("Iniciando DB RAG API...")
    
    try:
        from src.rag_system import RAGSystem
        from src.config import RAGConfig
        
        # Configurar sistema
        config = RAGConfig()
        rag = RAGSystem(config)
        
        print("\nSistema RAG inicializado com sucesso!")
        print("Para usar o sistema, importe as classes necessarias:")
        print("   from src.rag_system import RAGSystem")
        print("   from src.config import RAGConfig")
        
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
