#!/usr/bin/env python3
"""
Diagnóstico rápido do problema vector_store
"""
import os
import sys

# Add src to path - ajustado para nova estrutura
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_vector_store_access():
    """Testa o acesso ao vector store"""
    print("🔍 DIAGNÓSTICO DO VECTOR STORE")
    print("=" * 40)
    
    try:
        from vector_store_manager import VectorStoreManager
        from config_multi_llm import RAGConfig
        
        # Criar um RAGConfig simples
        rag_config = RAGConfig.from_env()
        
        # Criar VectorStoreManager
        vm = VectorStoreManager(rag_config)
        
        print("✅ VectorStoreManager criado com sucesso")
        print(f"📋 Atributos disponíveis: {[attr for attr in dir(vm) if not attr.startswith('__')]}")
        
        # Verificar se tem _vector_store
        if hasattr(vm, '_vector_store'):
            print("✅ Atributo '_vector_store' existe")
            print(f"💾 Valor: {vm._vector_store}")
        else:
            print("❌ Atributo '_vector_store' NÃO existe")
            
        # Verificar se tem vector_store
        if hasattr(vm, 'vector_store'):
            print("⚠️ Atributo 'vector_store' existe (problemático)")
        else:
            print("✅ Atributo 'vector_store' NÃO existe (correto)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_vector_store_access()
