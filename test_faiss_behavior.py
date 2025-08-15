"""Teste para verificar como o FAISS save_local funciona"""
import os
import tempfile
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from unittest.mock import Mock


def test_faiss_save_local_behavior():
    """Teste para entender o comportamento do FAISS save_local"""
    
    # Mock embeddings para evitar chamadas da API
    mock_embeddings = Mock()
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3] for _ in range(2)]
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    
    # Criar documentos de teste
    docs = [
        Document(page_content="Test document 1", metadata={"source": "test1"}),
        Document(page_content="Test document 2", metadata={"source": "test2"})
    ]
    
    # Criar vector store
    vector_store = FAISS.from_documents(docs, mock_embeddings)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Teste 1: Diretório pai existe, diretório destino não existe
        vector_store_dir = os.path.join(temp_dir, "vector_store")
        print(f"Tentando salvar em: {vector_store_dir}")
        print(f"Diretório existe antes: {os.path.exists(vector_store_dir)}")
        
        try:
            vector_store.save_local(vector_store_dir)
            print(f"Diretório existe depois: {os.path.exists(vector_store_dir)}")
            print(f"Arquivos criados: {os.listdir(vector_store_dir) if os.path.exists(vector_store_dir) else 'Nenhum'}")
        except Exception as e:
            print(f"Erro: {e}")
        
        # Teste 2: Diretório pai não existe
        nested_dir = os.path.join(temp_dir, "non_existent", "vector_store")
        print(f"\nTentando salvar em: {nested_dir}")
        print(f"Diretório pai existe: {os.path.exists(os.path.dirname(nested_dir))}")
        
        try:
            vector_store.save_local(nested_dir)
            print(f"Sucesso! Diretório existe: {os.path.exists(nested_dir)}")
        except Exception as e:
            print(f"Erro: {e}")


if __name__ == "__main__":
    test_faiss_save_local_behavior()
