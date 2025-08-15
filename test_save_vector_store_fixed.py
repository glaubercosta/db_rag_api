"""Teste para verificar a correção do save_vector_store"""
import os
import tempfile
from unittest.mock import Mock
from vector_store_manager import VectorStoreManager
from config import RAGConfig
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def test_save_vector_store_fixed():
    """Teste para verificar que save_vector_store funciona corretamente após correção"""
    
    # Mock embeddings
    mock_embeddings = Mock()
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3] for _ in range(2)]
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    
    # Mock config
    config = Mock(spec=RAGConfig)
    manager = VectorStoreManager(config)
    
    # Criar vector store real
    docs = [
        Document(page_content="Test document 1", metadata={"source": "test1"}),
        Document(page_content="Test document 2", metadata={"source": "test2"})
    ]
    vector_store = FAISS.from_documents(docs, mock_embeddings)
    manager._vector_store = vector_store
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Teste 1: Diretório simples
        vector_store_dir = os.path.join(temp_dir, "vector_store")
        print(f"Teste 1 - Salvando em: {vector_store_dir}")
        
        manager.save_vector_store(vector_store_dir)
        
        assert os.path.exists(vector_store_dir), f"Diretório {vector_store_dir} deve existir"
        assert os.path.exists(os.path.join(vector_store_dir, "index.faiss")), "index.faiss deve existir"
        assert os.path.exists(os.path.join(vector_store_dir, "index.pkl")), "index.pkl deve existir"
        assert os.path.exists(os.path.join(vector_store_dir, "metadata.json")), "metadata.json deve existir"
        print("✅ Teste 1 passou!")
        
        # Teste 2: Diretório aninhado (pai não existe)
        nested_dir = os.path.join(temp_dir, "level1", "level2", "vector_store")
        print(f"Teste 2 - Salvando em: {nested_dir}")
        
        manager.save_vector_store(nested_dir)
        
        assert os.path.exists(nested_dir), f"Diretório {nested_dir} deve existir"
        assert os.path.exists(os.path.join(nested_dir, "index.faiss")), "index.faiss deve existir"
        assert os.path.exists(os.path.join(nested_dir, "index.pkl")), "index.pkl deve existir"
        assert os.path.exists(os.path.join(nested_dir, "metadata.json")), "metadata.json deve existir"
        print("✅ Teste 2 passou!")
        
        # Teste 3: Sobrescrever diretório existente
        print(f"Teste 3 - Sobrescrevendo: {vector_store_dir}")
        
        manager.save_vector_store(vector_store_dir)  # Deve funcionar sem erro
        
        assert os.path.exists(vector_store_dir), f"Diretório {vector_store_dir} deve existir"
        print("✅ Teste 3 passou!")
        
    print("🎉 Todos os testes passaram! A correção funciona corretamente.")


if __name__ == "__main__":
    test_save_vector_store_fixed()
