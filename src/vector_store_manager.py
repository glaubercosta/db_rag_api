"""
Vector store manager for the RAG system
"""
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import pandas as pd
import os
import hashlib
import json
import logging
from models import DatabaseSchema, TableInfo
from database_scanner import DatabaseScanner
from config import RAGConfig


class SecurityError(Exception):
    """Exception raised for security-related issues"""
    pass


class VectorStoreManager:
    """Manages FAISS vector store operations"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self._vector_store: Optional[FAISS] = None

    def create_documents_from_schema(
        self, schema: DatabaseSchema
    ) -> List[Document]:
        """Create documents from database schema"""
        documents = []
        schema_text = schema.to_text()
        documents.append(
            Document(
                page_content=schema_text,
                metadata={"type": "schema", "content": "complete_schema"},
            )
        )
        for table in schema.tables:
            table_text = self._create_table_description(table)
            documents.append(
                Document(
                    page_content=table_text,
                    metadata={
                        "type": "table_schema",
                        "table_name": table.name,
                        "content": "table_description",
                    },
                )
            )
        return documents

    def create_documents_from_data(
        self, scanner: DatabaseScanner, schema: DatabaseSchema
    ) -> List[Document]:
        """Create documents from table data samples and stats"""
        documents = []
        for table in schema.tables:
            try:
                df = scanner.query_table_sample(
                    table.name, limit=self.config.table_sample_limit
                )
                if not df.empty:
                    stats_text = self._create_table_statistics(table.name, df)
                    documents.append(
                        Document(
                            page_content=stats_text,
                            metadata={
                                "type": "table_statistics",
                                "table_name": table.name,
                                "content": "statistics",
                            },
                        )
                    )
                    sample_text = self._create_data_sample(table.name, df)
                    documents.append(
                        Document(
                            page_content=sample_text,
                            metadata={
                                "type": "data_sample",
                                "table_name": table.name,
                                "content": "sample_data",
                            },
                        )
                    )
            except Exception as e:  # noqa: BLE001
                print(
                    "Warning: Could not process data for table "
                    f"{table.name}: {e}"
                )
                continue
        return documents

    def build_vector_store(
        self, documents: List[Document], embeddings
    ) -> FAISS:
        """Build the vector store from a list of documents"""
        if not documents:
            raise ValueError("Document list is empty")
        self._vector_store = FAISS.from_documents(documents, embeddings)
        if self.config.vector_store_path:
            self.save_vector_store(self.config.vector_store_path)
        return self._vector_store

    def load_vector_store(self, path: str, embeddings) -> FAISS:
        """Load previously saved vector store with security validation"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Vector store not found at: {path}")
        
        # Verificar se o diretório contém apenas arquivos esperados do FAISS
        expected_files = {'index.faiss', 'index.pkl'}
        optional_files = {'metadata.json'}  # Arquivo opcional de metadados
        allowed_files = expected_files | optional_files
        actual_files = set(os.listdir(path))
        
        # Validar que existem arquivos obrigatórios
        if not expected_files.issubset(actual_files):
            missing = expected_files - actual_files
            raise SecurityError(
                f"Missing required FAISS files: {missing}. "
                f"This might indicate a corrupted or malicious vector store."
            )
        
        # Verificar se há arquivos suspeitos extras
        extra_files = actual_files - allowed_files
        if extra_files:
            logging.warning(
                f"Extra files found in vector store directory: {extra_files}. "
                f"This might indicate tampering."
            )
        
        # Verificar tamanho dos arquivos (proteção contra arquivos grandes)
        max_file_size = 100 * 1024 * 1024  # 100MB limite
        for file in expected_files:
            file_path = os.path.join(path, file)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > max_file_size:
                    raise SecurityError(
                        f"Vector store file {file} is too large "
                        f"({file_size} bytes). "
                        f"Maximum allowed: {max_file_size} bytes."
                    )
        
        try:
            # Tentar carregar sem allow_dangerous_deserialization primeiro
            self._vector_store = FAISS.load_local(
                path, embeddings, allow_dangerous_deserialization=False
            )
        except Exception as e:
            # Se falhar, verificar se é um arquivo confiável
            if self._is_trusted_vector_store(path):
                logging.warning(
                    "Loading vector store with dangerous deserialization "
                    "from trusted source. Consider regenerating the store."
                )
                self._vector_store = FAISS.load_local(
                    path, embeddings, allow_dangerous_deserialization=True
                )
            else:
                raise SecurityError(
                    f"Cannot load vector store safely: {e}. "
                    f"The store may be corrupted or created with an "
                    f"incompatible version. Consider regenerating the "
                    f"vector store."
                ) from e
        
        return self._vector_store
    
    def _is_trusted_vector_store(self, path: str) -> bool:
        """Verificar se o vector store é de uma fonte confiável"""
        # Verificar se existe um arquivo de metadados que criamos
        metadata_file = os.path.join(path, 'metadata.json')
        if not os.path.exists(metadata_file):
            return False
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verificar se contém nossos campos esperados
            required_fields = {'created_by', 'version', 'checksum'}
            if not required_fields.issubset(metadata.keys()):
                return False
            
            # Verificar se foi criado por nossa aplicação
            if metadata.get('created_by') != 'db_rag_system':
                return False
            
            # Verificar checksum básico do arquivo index.faiss
            index_file = os.path.join(path, 'index.faiss')
            if os.path.exists(index_file):
                actual_checksum = self._calculate_file_checksum(index_file)
                expected_checksum = metadata.get('checksum')
                if actual_checksum != expected_checksum:
                    logging.warning(
                        f"Checksum mismatch for {index_file}. "
                        f"Expected: {expected_checksum}, "
                        f"Got: {actual_checksum}"
                    )
                    return False
            
            return True
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Could not read metadata file: {e}")
            return False
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calcular checksum SHA-256 de um arquivo"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def save_vector_store(self, path: str):
        """Persist vector store to disk with security metadata
        
        Args:
            path: Directory path where the vector store will be saved.
                  FAISS will create this directory automatically if it doesn't exist,
                  including any parent directories.
        
        Note:
            Previously this method called os.makedirs(os.path.dirname(path), exist_ok=True)
            which could fail when path was intended to be the target directory itself.
            FAISS save_local() handles directory creation automatically, so manual
            directory creation is unnecessary and potentially problematic.
        """
        if not self._vector_store:
            raise ValueError("Vector store not created yet")
        
        # FAISS save_local creates the directory automatically if it doesn't exist
        # No need to call os.makedirs() manually as it can cause issues
        # when path is intended to be the target directory itself
        self._vector_store.save_local(path)
        
        # Criar arquivo de metadados para validação de segurança
        index_file = os.path.join(path, 'index.faiss')
        if os.path.exists(index_file):
            checksum = self._calculate_file_checksum(index_file)
            metadata = {
                'created_by': 'db_rag_system',
                'version': '1.0',
                'checksum': checksum,
                'created_at': pd.Timestamp.now().isoformat(),
                'description': 'FAISS vector store for database RAG system'
            }
            
            metadata_file = os.path.join(path, 'metadata.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

    def search_similar(
        self, query: str, k: Optional[int] = None
    ) -> List[Document]:
        """Search similar documents in vector store"""
        if not self._vector_store:
            raise ValueError("Vector store not initialized")
        k = k or self.config.similarity_search_k
        return self._vector_store.similarity_search(query, k=k)

    def _create_table_description(self, table: TableInfo) -> str:
        """Create detailed description for a table"""
        lines = [f"Table: {table.name}"]
        lines.append("Purpose: Database table with the following structure:")
        lines.append("")
        lines.append("Columns:")
        for col in table.columns:
            pk_marker = " (Primary Key)" if col.is_primary_key else ""
            nullable = "nullable" if col.is_nullable else "not null"
            lines.append(
                f"  - {col.name}: {col.data_type} ({nullable}){pk_marker}"
            )
        if table.foreign_keys:
            lines.append("")
            lines.append("Relationships:")
            for fk in table.foreign_keys:
                lines.append(
                    "  - "
                    f"{fk.column} references {fk.references_table}."
                    f"{fk.references_column}"
                )
        return "\n".join(lines)

    def _create_table_statistics(
        self, table_name: str, df: pd.DataFrame
    ) -> str:
        """Create statistics summary for table"""
        lines = [f"Table Statistics: {table_name}"]
        lines.append(f"Total rows sampled: {len(df)}")
        lines.append("")
        lines.append("Column Statistics:")
        for col in df.columns:
            series = df[col]
            lines.append(f"  - {col}:")
            lines.append(f"    * Data type: {series.dtype}")
            lines.append(f"    * Null values: {series.isnull().sum()}")
            if series.dtype in ["int64", "float64"]:
                lines.append(f"    * Min: {series.min()}")
                lines.append(f"    * Max: {series.max()}")
                lines.append(f"    * Mean: {series.mean():.2f}")
            elif series.dtype == "object":
                unique_count = series.nunique()
                lines.append(f"    * Unique values: {unique_count}")
                if unique_count <= 10:
                    unique_values = series.unique()[:10]
                    lines.append(f"    * Sample values: {list(unique_values)}")
        return "\n".join(lines)

    def _create_data_sample(self, table_name: str, df: pd.DataFrame) -> str:
        """Create sample data text for table"""
        lines = [f"Data Sample from {table_name}:"]
        lines.append("")
        sample_size = min(5, len(df))
        for idx in range(sample_size):
            row = df.iloc[idx]
            lines.append(f"Row {idx + 1}:")
            for col, value in row.items():
                lines.append(f"  - {col}: {value}")
            lines.append("")
        return "\n".join(lines)
