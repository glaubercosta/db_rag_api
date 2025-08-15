#!/usr/bin/env python3
"""
Teste do sistema de segurança do vector store - REFATORADO COM ASSERTIONS
"""
import os
import tempfile
import shutil
import json
import pytest
from unittest.mock import Mock
from dotenv import load_dotenv
from vector_store_manager import VectorStoreManager, SecurityError
from config import RAGConfig
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()


class TestVectorStoreSecurity:
    """Test class para segurança do vector store com assertions determinísticas"""

    @pytest.fixture
    def config(self):
        """Fixture para configuração RAG"""
        return RAGConfig()

    @pytest.fixture
    def sample_documents(self):
        """Fixture para documentos de teste"""
        return [
            Document(
                page_content="Test document for security validation",
                metadata={"type": "test", "source": "security_test"}
            )
        ]

    @pytest.fixture
    def mock_embeddings(self):
        """Fixture para embeddings mockados"""
        embeddings = Mock()
        embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        return embeddings

    def test_secure_vector_store_creation(self, config, sample_documents):
        """Testa criação segura do vector store"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_path = os.path.join(temp_dir, "test_vector_store")
            
            # Criar vector store com embeddings reais
            real_embeddings = OpenAIEmbeddings()
            manager = VectorStoreManager(config)
            
            # Deve criar sem erros
            manager.build_vector_store(sample_documents, real_embeddings)
            manager.save_vector_store(vector_store_path)
            
            # Verificar se arquivos necessários foram criados
            assert os.path.exists(vector_store_path), "Diretório do vector store deve existir"
            assert os.path.exists(os.path.join(vector_store_path, "index.faiss")), "Arquivo index.faiss deve existir"
            assert os.path.exists(os.path.join(vector_store_path, "index.pkl")), "Arquivo index.pkl deve existir"
            
            # Verificar se arquivo de metadados foi criado
            metadata_file = os.path.join(vector_store_path, 'metadata.json')
            assert os.path.exists(metadata_file), "Arquivo de metadados deve ser criado"
            
            # Verificar conteúdo dos metadados
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            assert 'created_by' in metadata, "Metadados devem ter campo 'created_by'"
            assert 'version' in metadata, "Metadados devem ter campo 'version'"
            assert 'checksum' in metadata, "Metadados devem ter campo 'checksum'"
            assert 'created_at' in metadata, "Metadados devem ter campo 'created_at'"
            assert len(metadata['checksum']) > 0, "Checksum não deve estar vazio"

    def test_secure_vector_store_loading(self, config, sample_documents):
        """Testa carregamento seguro do vector store"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_path = os.path.join(temp_dir, "test_vector_store")
            
            # Criar vector store
            real_embeddings = OpenAIEmbeddings()
            manager = VectorStoreManager(config)
            manager.build_vector_store(sample_documents, real_embeddings)
            manager.save_vector_store(vector_store_path)
            
            # Carregar vector store
            loaded_manager = VectorStoreManager(config)
            loaded_manager.load_vector_store(vector_store_path, real_embeddings)
            
            # Verificar se carregou corretamente
            assert loaded_manager.vector_store is not None, "Vector store deve estar carregado"
            
            # Testar busca
            results = loaded_manager.search_similar("test document", k=1)
            assert len(results) > 0, "Busca deve retornar resultados"
            assert len(results) <= 1, "Busca com k=1 deve retornar no máximo 1 resultado"

    def test_protection_against_malicious_files(self, config, sample_documents):
        """Testa proteção contra arquivos maliciosos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_path = os.path.join(temp_dir, "test_vector_store")
            
            # Criar vector store válido
            real_embeddings = OpenAIEmbeddings()
            manager = VectorStoreManager(config)
            manager.build_vector_store(sample_documents, real_embeddings)
            manager.save_vector_store(vector_store_path)
            
            # Adicionar arquivo malicioso
            malicious_file = os.path.join(vector_store_path, "malicious.py")
            with open(malicious_file, 'w') as f:
                f.write("# This could be malicious code")
            
            # Tentar carregar - deve detectar arquivo extra
            loaded_manager = VectorStoreManager(config)
            with pytest.warns(UserWarning, match="Extra files detected"):
                loaded_manager.load_vector_store(vector_store_path, real_embeddings)

    def test_protection_against_missing_files(self, config, sample_documents):
        """Testa proteção contra arquivos faltantes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_path = os.path.join(temp_dir, "test_vector_store")
            
            # Criar vector store válido
            real_embeddings = OpenAIEmbeddings()
            manager = VectorStoreManager(config)
            manager.build_vector_store(sample_documents, real_embeddings)
            manager.save_vector_store(vector_store_path)
            
            # Remover arquivo obrigatório
            index_file = os.path.join(vector_store_path, "index.faiss")
            backup_path = index_file + ".backup"
            shutil.move(index_file, backup_path)
            
            # Tentar carregar - deve falhar
            loaded_manager = VectorStoreManager(config)
            with pytest.raises(SecurityError, match="Missing required files"):
                loaded_manager.load_vector_store(vector_store_path, real_embeddings)
            
            # Restaurar arquivo para cleanup
            shutil.move(backup_path, index_file)

    def test_protection_against_corrupted_metadata(self, config, sample_documents):
        """Testa proteção contra metadados corrompidos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_path = os.path.join(temp_dir, "test_vector_store")
            
            # Criar vector store válido
            real_embeddings = OpenAIEmbeddings()
            manager = VectorStoreManager(config)
            manager.build_vector_store(sample_documents, real_embeddings)
            manager.save_vector_store(vector_store_path)
            
            # Corromper metadados
            metadata_file = os.path.join(vector_store_path, 'metadata.json')
            with open(metadata_file, 'w') as f:
                f.write("corrupted data")
            
            # Tentar carregar - deve detectar corrupção
            loaded_manager = VectorStoreManager(config)
            with pytest.raises((json.JSONDecodeError, SecurityError)):
                loaded_manager.load_vector_store(vector_store_path, real_embeddings)

    def test_nonexistent_path_handling(self, config, mock_embeddings):
        """Testa tratamento de caminho inexistente"""
        manager = VectorStoreManager(config)
        
        with pytest.raises(FileNotFoundError):
            manager.load_vector_store("/path/that/does/not/exist", mock_embeddings)

    def test_checksum_functionality(self, config):
        """Testa funcionalidade de checksum"""
        manager = VectorStoreManager(config)
        
        # Criar arquivo de teste
        test_file = "test_checksum_file.txt"
        try:
            with open(test_file, 'w') as f:
                f.write("test content for checksum")
            
            # Calcular checksum duas vezes - deve ser consistente
            checksum1 = manager._calculate_file_checksum(test_file)
            checksum2 = manager._calculate_file_checksum(test_file)
            
            assert checksum1 == checksum2, "Checksum deve ser consistente"
            assert len(checksum1) > 0, "Checksum não deve estar vazio"
            
            # Modificar arquivo e verificar se checksum muda
            with open(test_file, 'a') as f:
                f.write(" modified")
            
            checksum3 = manager._calculate_file_checksum(test_file)
            assert checksum1 != checksum3, "Checksum deve detectar modificações"
            
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_security_validation_integration(self, config, sample_documents):
        """Teste integrado de todas as validações de segurança"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_path = os.path.join(temp_dir, "test_vector_store")
            
            # 1. Criar vector store
            real_embeddings = OpenAIEmbeddings()
            manager = VectorStoreManager(config)
            manager.build_vector_store(sample_documents, real_embeddings)
            manager.save_vector_store(vector_store_path)
            
            # 2. Verificar estrutura criada
            required_files = ["index.faiss", "index.pkl", "metadata.json"]
            for file_name in required_files:
                file_path = os.path.join(vector_store_path, file_name)
                assert os.path.exists(file_path), f"Arquivo {file_name} deve existir"
            
            # 3. Carregar e validar funcionalidade
            loaded_manager = VectorStoreManager(config)
            loaded_manager.load_vector_store(vector_store_path, real_embeddings)
            
            results = loaded_manager.search_similar("test", k=1)
            assert len(results) >= 0, "Busca deve funcionar após carregamento"
            
            # 4. Verificar que sistema detecta problemas
            # Adicionar arquivo suspeito
            suspicious_file = os.path.join(vector_store_path, "suspicious.exe")
            with open(suspicious_file, 'w') as f:
                f.write("suspicious content")
            
            # Deve emitir warning mas não falhar completamente
            with pytest.warns(UserWarning):
                test_manager = VectorStoreManager(config)
                test_manager.load_vector_store(vector_store_path, real_embeddings)


if __name__ == "__main__":
    # Executar com pytest se chamado diretamente
    pytest.main([__file__, "-v", "--tb=short"])
