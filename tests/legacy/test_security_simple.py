#!/usr/bin/env python3
"""
Teste simplificado do sistema de segurança do vector store
"""
import os
import tempfile
import json
from dotenv import load_dotenv
from vector_store_manager import VectorStoreManager, SecurityError
from config import RAGConfig
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()


def test_basic_security():
    """Teste básico de funcionalidade de segurança"""
    print("=== TESTE BÁSICO DE SEGURANÇA ===\n")
    
    config = RAGConfig()
    
    # Criar documentos de teste
    documents = [
        Document(
            page_content="Test document for security validation",
            metadata={"type": "test", "source": "security_test"}
        )
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        vector_store_path = os.path.join(temp_dir, "test_vector_store")
        
        print("1. Testando criação com metadados...")
        try:
            real_embeddings = OpenAIEmbeddings()
            manager = VectorStoreManager(config)
            manager.build_vector_store(documents, real_embeddings)
            manager.save_vector_store(vector_store_path)
            
            # Verificar se metadados foram criados
            metadata_file = os.path.join(vector_store_path, 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"   ✅ Metadados criados: {metadata['created_by']}")
            else:
                print("   ❌ Metadados não foram criados")
                
        except Exception as e:
            print(f"   ❌ Erro na criação: {e}")
            return
        
        print("\n2. Testando carregamento seguro...")
        try:
            new_manager = VectorStoreManager(config)
            new_manager.load_vector_store(vector_store_path, real_embeddings)
            print("   ✅ Carregamento seguro bem-sucedido")
        except Exception as e:
            print(f"   ❌ Erro no carregamento: {e}")
        
        print("\n3. Testando proteção contra arquivos faltantes...")
        # Remover arquivo obrigatório
        index_file = os.path.join(vector_store_path, "index.faiss")
        if os.path.exists(index_file):
            os.remove(index_file)
            
            try:
                test_manager = VectorStoreManager(config)
                test_manager.load_vector_store(
                    vector_store_path, real_embeddings
                )
                print("   ❌ Deveria ter falhado com arquivo faltante")
            except SecurityError:
                print("   ✅ Bloqueou arquivo faltante corretamente")
            except Exception as e:
                print(f"   ❓ Erro inesperado: {type(e).__name__}")
    
    print("\n=== TESTE CONCLUÍDO ===")


def test_checksum_function():
    """Teste da função de checksum"""
    print("\n=== TESTE DE CHECKSUM ===")
    
    config = RAGConfig()
    manager = VectorStoreManager(config)
    
    # Criar arquivo de teste
    test_file = "test_checksum.txt"
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Conteúdo de teste para checksum")
        
        checksum1 = manager._calculate_file_checksum(test_file)
        checksum2 = manager._calculate_file_checksum(test_file)
        
        if checksum1 == checksum2:
            print("   ✅ Checksum é consistente")
        else:
            print("   ❌ Checksum é inconsistente")
        
        # Modificar arquivo
        with open(test_file, 'a', encoding='utf-8') as f:
            f.write(" - modificado")
        
        checksum3 = manager._calculate_file_checksum(test_file)
        if checksum1 != checksum3:
            print("   ✅ Checksum detecta modificações")
        else:
            print("   ❌ Checksum não detecta modificações")
            
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    test_basic_security()
    test_checksum_function()
