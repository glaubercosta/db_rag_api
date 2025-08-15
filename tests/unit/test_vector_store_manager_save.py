"""Testes unitários para o método save_vector_store após correção"""
import os
import tempfile
import pytest
from unittest.mock import Mock, patch
from vector_store_manager import VectorStoreManager, SecurityError
from config import RAGConfig


class TestVectorStoreManagerSave:
    """Testes para o método save_vector_store"""

    def setup_method(self):
        """Setup para cada teste"""
        self.config = Mock(spec=RAGConfig)
        self.manager = VectorStoreManager(self.config)
        
        # Mock do vector store
        self.mock_vector_store = Mock()
        self.manager._vector_store = self.mock_vector_store

    def test_save_vector_store_no_vector_store(self):
        """Deve falhar se vector store não foi criado"""
        self.manager._vector_store = None
        
        with pytest.raises(ValueError, match="Vector store not created yet"):
            self.manager.save_vector_store("/some/path")

    def test_save_vector_store_calls_save_local(self):
        """Deve chamar save_local do vector store"""
        path = "/test/path"
        self.manager.save_vector_store(path)
        
        self.mock_vector_store.save_local.assert_called_once_with(path)

    def test_save_vector_store_no_makedirs_call(self):
        """Deve não chamar os.makedirs pois FAISS cria diretórios automaticamente"""
        path = "/test/path"
        
        with patch('os.makedirs') as mock_makedirs:
            self.manager.save_vector_store(path)
            
            # Não deve chamar makedirs pois foi removido da implementação
            mock_makedirs.assert_not_called()

    def test_save_vector_store_creates_metadata(self):
        """Deve criar arquivo de metadados após salvar"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_dir = os.path.join(temp_dir, "vector_store")
            
            # Mock para simular criação do index.faiss
            def mock_save_local(path):
                os.makedirs(path, exist_ok=True)
                # Criar arquivo index.faiss para simular FAISS
                with open(os.path.join(path, "index.faiss"), "w") as f:
                    f.write("fake faiss data")
                    
            self.mock_vector_store.save_local.side_effect = mock_save_local
            
            # Executar save
            self.manager.save_vector_store(vector_store_dir)
            
            # Verificar que metadata foi criado
            metadata_file = os.path.join(vector_store_dir, "metadata.json")
            assert os.path.exists(metadata_file), "Arquivo metadata.json deve ser criado"

    def test_save_vector_store_directory_creation_scenarios(self):
        """Testa diferentes cenários de criação de diretório"""
        test_cases = [
            # (descrição, path_relativo)
            ("diretório simples", "vector_store"),
            ("diretório aninhado", "level1/level2/vector_store"),
            ("diretório com espaços", "my vector store"),
            ("diretório com caracteres especiais", "vector-store_v1.0"),
        ]
        
        for description, relative_path in test_cases:
            with tempfile.TemporaryDirectory() as temp_dir:
                vector_store_dir = os.path.join(temp_dir, relative_path)
                
                # Mock para simular criação automática do FAISS
                def mock_save_local(path):
                    # FAISS cria o diretório automaticamente
                    os.makedirs(path, exist_ok=True)
                    
                self.mock_vector_store.save_local.side_effect = mock_save_local
                
                # Não deve falhar - FAISS cria diretórios automaticamente
                self.manager.save_vector_store(vector_store_dir)
                
                # Verificar que save_local foi chamado
                self.mock_vector_store.save_local.assert_called_with(vector_store_dir)
                
                # Reset para próximo teste
                self.mock_vector_store.reset_mock()

    def test_save_vector_store_existing_directory(self):
        """Deve funcionar quando diretório já existe"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store_dir = os.path.join(temp_dir, "existing_vector_store")
            os.makedirs(vector_store_dir, exist_ok=True)
            
            # Deve funcionar sem erros
            self.manager.save_vector_store(vector_store_dir)
            
            self.mock_vector_store.save_local.assert_called_once_with(vector_store_dir)

    def test_save_vector_store_path_as_target_directory(self):
        """
        Teste específico para o bug corrigido:
        Quando path é o diretório destino (não pai), deve funcionar corretamente
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Este é o caso que falhava antes da correção
            vector_store_dir = os.path.join(temp_dir, "target_directory")
            
            # Antes da correção: os.makedirs(os.path.dirname(path)) criaria apenas temp_dir
            # Depois da correção: FAISS cria vector_store_dir automaticamente
            
            def mock_save_local(path):
                # Simular comportamento do FAISS: cria o diretório se não existir
                os.makedirs(path, exist_ok=True)
                with open(os.path.join(path, "index.faiss"), "w") as f:
                    f.write("fake data")
                with open(os.path.join(path, "index.pkl"), "w") as f:
                    f.write("fake data")
                    
            self.mock_vector_store.save_local.side_effect = mock_save_local
            
            # Esta operação deve funcionar perfeitamente
            self.manager.save_vector_store(vector_store_dir)
            
            # Verificações
            assert os.path.exists(vector_store_dir), "Diretório destino deve existir"
            assert os.path.exists(os.path.join(vector_store_dir, "index.faiss")), "index.faiss deve existir"
            assert os.path.exists(os.path.join(vector_store_dir, "index.pkl")), "index.pkl deve existir"
            self.mock_vector_store.save_local.assert_called_once_with(vector_store_dir)
