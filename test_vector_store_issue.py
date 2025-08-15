"""Teste para demonstrar o problema do save_vector_store"""
import os
import tempfile
from unittest.mock import Mock, patch
from vector_store_manager import VectorStoreManager
from config import RAGConfig


def test_save_vector_store_directory_issue():
    """Teste para demonstrar o problema quando path é o diretório destino"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Caso 1: path é um diretório que não existe ainda
        vector_store_dir = os.path.join(temp_dir, "vector_store")
        
        # Mock do config
        config = Mock(spec=RAGConfig)
        manager = VectorStoreManager(config)
        
        # Mock do vector store
        mock_vector_store = Mock()
        manager._vector_store = mock_vector_store
        
        # Tentativa de salvar
        manager.save_vector_store(vector_store_dir)
        
        # O problema: os.path.dirname(vector_store_dir) é temp_dir
        # Mas o FAISS precisa que vector_store_dir exista!
        
        # Verificar que save_local foi chamado com o diretório correto
        mock_vector_store.save_local.assert_called_once_with(vector_store_dir)
        
        print(f"Diretório pai criado: {os.path.dirname(vector_store_dir)}")
        print(f"Diretório destino (pode não existir): {vector_store_dir}")
        print(f"Diretório pai existe: {os.path.exists(os.path.dirname(vector_store_dir))}")
        print(f"Diretório destino existe: {os.path.exists(vector_store_dir)}")


if __name__ == "__main__":
    test_save_vector_store_directory_issue()
