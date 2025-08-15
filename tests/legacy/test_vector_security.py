#!/usr/bin/env python3
"""
Teste do sistema de segurança do vector store
"""
import os
import tempfile
import shutil
import json
from unittest.mock import Mock
from dotenv import load_dotenv
from vector_store_manager import VectorStoreManager, SecurityError
from config import RAGConfig
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()


def test_secure_vector_store():
    """Testa a funcionalidade de segurança do vector store"""
    print("=== TESTE DE SEGURANÇA DO VECTOR STORE ===\n")
    
    # Configuração
    config = RAGConfig()
    
    # Mock embeddings para teste
    embeddings = Mock()
    embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    
    # Criar documentos de teste
    documents = [
        Document(
            page_content="Test document for security validation",
            metadata={"type": "test", "source": "security_test"}
        )
    ]
    
    # Usar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        vector_store_path = os.path.join(temp_dir, "test_vector_store")
        
        print("1. Testando criação segura do vector store...")
        try:
            # Usar embeddings reais para criar o store
            real_embeddings = OpenAIEmbeddings()
            real_manager = VectorStoreManager(config)
            real_manager.build_vector_store(documents, real_embeddings)
            real_manager.save_vector_store(vector_store_path)
            
            print("   ✅ Vector store criado com sucesso")
            
            # Verificar se o arquivo de metadados foi criado
            metadata_file = os.path.join(vector_store_path, 'metadata.json')
            if os.path.exists(metadata_file):
                print("   ✅ Arquivo de metadados criado")
                
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    print(f"   📋 Criado por: {metadata.get('created_by')}")
                    print(f"   📋 Versão: {metadata.get('version')}")
                    print(f"   📋 Checksum: {metadata.get('checksum')[:16]}...")
            else:
                print("   ❌ Arquivo de metadados não foi criado")
            
        except Exception as e:
            print(f"   ❌ Erro na criação: {e}")
            return
        
        print("\n2. Testando carregamento seguro...")
        try:
            loaded_manager = VectorStoreManager(config)
            loaded_manager.load_vector_store(
                vector_store_path, real_embeddings
            )
            print("   ✅ Vector store carregado com segurança")
            
            # Testar busca
            results = loaded_manager.search_similar("test document", k=1)
            print(f"   📊 Encontrados {len(results)} documentos na busca")
            
        except Exception as e:
            print(f"   ❌ Erro no carregamento seguro: {e}")
        
        print("\n3. Testando proteção contra arquivos maliciosos...")
        
        # Teste 3a: Arquivo extra suspeito
        malicious_file = os.path.join(vector_store_path, "malicious.py")
        with open(malicious_file, 'w') as f:
            f.write("# This could be malicious code")
        
        try:
            loaded_manager = VectorStoreManager(config)
            loaded_store = loaded_manager.load_vector_store(vector_store_path, real_embeddings)
            print("   ⚠️  Sistema permitiu arquivo extra (warning esperado)")
        except SecurityError as e:
            print(f"   ✅ Sistema bloqueou arquivo extra: {e}")
        except Exception as e:
            print(f"   ❓ Erro inesperado: {e}")
        
        # Limpar arquivo malicioso
        os.remove(malicious_file)
        
        # Teste 3b: Arquivo obrigatório removido
        index_file = os.path.join(vector_store_path, "index.faiss")
        backup_path = index_file + ".backup"
        shutil.move(index_file, backup_path)
        
        try:
            loaded_manager = VectorStoreManager(config)
            loaded_store = loaded_manager.load_vector_store(vector_store_path, real_embeddings)
            print("   ❌ Sistema deveria ter bloqueado arquivo faltante")
        except SecurityError as e:
            print(f"   ✅ Sistema bloqueou arquivo faltante: {e}")
        except Exception as e:
            print(f"   ❓ Erro inesperado: {e}")
        
        # Restaurar arquivo
        shutil.move(backup_path, index_file)
        
        # Teste 3c: Corromper metadados
        metadata_file = os.path.join(vector_store_path, 'metadata.json')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'w') as f:
                f.write("corrupted data")
            
            try:
                loaded_manager = VectorStoreManager(config)
                loaded_store = loaded_manager.load_vector_store(vector_store_path, real_embeddings)
                print("   ⚠️  Sistema tolerou metadados corrompidos")
            except Exception as e:
                print(f"   ✅ Sistema detectou metadados corrompidos")
    
    print("\n=== TESTE CONCLUÍDO ===")


def test_security_validation():
    """Testa validações específicas de segurança"""
    print("\n=== VALIDAÇÕES DE SEGURANÇA ===")
    
    config = RAGConfig()
    manager = VectorStoreManager(config)
    
    # Teste de arquivo inexistente
    try:
        manager.load_vector_store("/path/that/does/not/exist", Mock())
        print("   ❌ Deveria ter falhado para caminho inexistente")
    except FileNotFoundError:
        print("   ✅ Bloqueou caminho inexistente corretamente")
    except Exception as e:
        print(f"   ❓ Erro inesperado: {e}")
    
    # Teste de checksum
    test_file = "test_file.txt"
    with open(test_file, 'w') as f:
        f.write("test content for checksum")
    
    try:
        checksum1 = manager._calculate_file_checksum(test_file)
        checksum2 = manager._calculate_file_checksum(test_file)
        
        if checksum1 == checksum2:
            print("   ✅ Função de checksum é consistente")
        else:
            print("   ❌ Função de checksum é inconsistente")
        
        # Modificar arquivo e verificar se checksum muda
        with open(test_file, 'a') as f:
            f.write(" modified")
        
        checksum3 = manager._calculate_file_checksum(test_file)
        if checksum1 != checksum3:
            print("   ✅ Checksum detecta modificações")
        else:
            print("   ❌ Checksum não detecta modificações")
        
    except Exception as e:
        print(f"   ❌ Erro no teste de checksum: {e}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    test_secure_vector_store()
    test_security_validation()
