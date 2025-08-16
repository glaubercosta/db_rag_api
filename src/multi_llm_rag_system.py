"""
Multi-LLM RAG system for relational databases
"""
import os
import traceback
from typing import Optional

from config_multi_llm import DatabaseConfig, MultiLLMConfig, RAGConfig
from llm_providers.provider_manager import LLMProviderManager, create_provider_manager_from_env
from database_scanner import DatabaseScanner
from vector_store_manager import VectorStoreManager
from sql_agent import SQLAgent, RAGQueryProcessor


class MultiLLMDatabaseRAGSystem:
    """Main RAG system coordinating multiple LLM providers"""

    def __init__(
        self,
        db_config: DatabaseConfig,
        multi_llm_config: MultiLLMConfig,
        rag_config: RAGConfig,
        provider_manager: Optional[LLMProviderManager] = None
    ):
        self.db_config = db_config
        self.multi_llm_config = multi_llm_config
        self.rag_config = rag_config

        # Initialize provider manager
        if provider_manager:
            self.provider_manager = provider_manager
        else:
            self.provider_manager = self._create_provider_manager()

        # Initialize components
        self.scanner = DatabaseScanner(db_config)
        self.vector_store_manager = VectorStoreManager(rag_config)
        self.sql_agent = None  # Will be initialized after provider selection
        self.query_processor = None

    def _create_provider_manager(self) -> LLMProviderManager:
        """Create and configure provider manager"""
        manager = LLMProviderManager()
        
        # Add LLM providers from configuration
        llm_configs = self.multi_llm_config.get_llm_configs()
        for provider_type, config in llm_configs.items():
            manager.add_llm_provider(provider_type, config)
        
        # Add embedding providers from configuration
        embedding_configs = self.multi_llm_config.get_embedding_configs()
        for provider_type, config in embedding_configs.items():
            manager.add_embedding_provider(provider_type, config)
        
        return manager

    def initialize(self, force_rebuild: bool = False) -> bool:
        """Initialize system building or loading the vector store."""
        try:
            if not force_rebuild:
                # Allow environment variable override
                env_force = os.getenv("RAG_FORCE_REBUILD", "").lower()
                force_rebuild = env_force in ("1", "true", "yes")

            print("🚀 Initializing Multi-LLM Database RAG System...")
            
            # Select active providers
            llm_provider = self.provider_manager.select_active_llm_provider()
            embedding_provider = self.provider_manager.select_active_embedding_provider()
            
            if not llm_provider:
                print("❌ No LLM provider available. Please configure at least one provider.")
                return False
            
            if not embedding_provider:
                print("❌ No embedding provider available. Please configure at least one provider.")
                return False

            # Initialize SQL Agent with active LLM provider
            langchain_llm = self.provider_manager.get_langchain_llm()
            self.sql_agent = SQLAgent.from_langchain_llm(langchain_llm, self.scanner)

            # Get embeddings for vector store
            langchain_embeddings = self.provider_manager.get_langchain_embeddings()
            
            # Scan database
            print("📊 Scanning database schema and data...")
            schema_info = self.scanner.scan_database()
            
            # Initialize vector store
            print("🔍 Setting up vector store...")
            vector_store_path = self.rag_config.vector_store_path
            vector_store_loaded = False
            
            # Try to load existing vector store if not forcing rebuild
            if not force_rebuild and os.path.exists(vector_store_path):
                try:
                    print("📂 Loading existing vector store...")
                    self.vector_store_manager.load_vector_store(vector_store_path, langchain_embeddings)
                    vector_store_loaded = True
                    print("✅ Vector store loaded successfully!")
                except Exception as e:
                    print(f"⚠️ Failed to load existing vector store: {e}")
                    print("🔄 Will rebuild vector store...")
            
            # Build vector store if not loaded
            if not vector_store_loaded:
                print("🔄 Building vector store from database schema...")
                texts, metadatas = self._prepare_vectorization_data(schema_info)
                
                # Convert texts and metadatas to Document objects
                from langchain.schema import Document
                documents = [
                    Document(page_content=text, metadata=metadata)
                    for text, metadata in zip(texts, metadatas)
                ]
                
                # Use the active embedding provider
                self.vector_store_manager._vector_store = self.vector_store_manager.build_vector_store(
                    documents, langchain_embeddings
                )
                print("✅ Vector store built and saved successfully!")
            else:
                print("✅ Loaded existing vector store")
                # Update the embeddings in the loaded vector store
                self.vector_store_manager._vector_store._embedding = langchain_embeddings

            # Initialize query processor
            self.query_processor = RAGQueryProcessor(
                self.vector_store_manager._vector_store,
                self.sql_agent,
                self.rag_config
            )

            print("✅ Multi-LLM Database RAG System initialized successfully!")
            self._print_system_status()
            return True

        except Exception as e:
            print(f"❌ Error during initialization: {str(e)}")
            print(f"Stack trace: {traceback.format_exc()}")
            return False

    def _prepare_vectorization_data(self, schema_info):
        """Prepare data for vectorization"""
        texts = []
        metadatas = []

        # schema_info is now a DatabaseSchema object
        for table in schema_info.tables:
            # Table schema text
            schema_text = f"Table: {table.name}\n"
            schema_text += f"Description: Database table {table.name}\n"
            schema_text += "Columns:\n"
            
            for col in table.columns:
                schema_text += f"- {col.name} ({col.data_type})"
                if col.is_nullable:
                    schema_text += " [nullable]"
                if col.name in table.primary_keys:
                    schema_text += " [primary key]"
                schema_text += "\n"
            
            # Add foreign keys if any
            if table.foreign_keys:
                schema_text += "Foreign Keys:\n"
                for fk in table.foreign_keys:
                    schema_text += f"- {fk.column} references {fk.references_table}.{fk.references_column}\n"
            
            # Try to get sample data
            try:
                sample_data = self.scanner.query_table_sample(table.name, limit=5)
                if sample_data:
                    schema_text += f"\nSample data (first few rows):\n"
                    # Add header
                    headers = list(sample_data[0].keys()) if sample_data else []
                    if headers:
                        schema_text += " | ".join(str(h) for h in headers) + "\n"
                        schema_text += "-" * len(" | ".join(str(h) for h in headers)) + "\n"
                        
                        # Add sample rows
                        for row in sample_data[:3]:  # Limit to first 3 rows
                            values = [str(row.get(h, '')) for h in headers]
                            schema_text += " | ".join(values) + "\n"
            except Exception as e:
                # If sample data fails, continue without it
                print(f"⚠️ Could not get sample data for {table.name}: {e}")
            
            texts.append(schema_text)
            metadatas.append({
                'table_name': table.name,
                'type': 'table_schema',
                'row_count': 0  # Could get actual row count if needed
            })

        return texts, metadatas

    def _print_system_status(self):
        """Print current system status"""
        print("\n" + "="*60)
        print("🎯 MULTI-LLM RAG SYSTEM STATUS")
        print("="*60)
        
        status = self.provider_manager.list_available_providers()
        
        print("\n🤖 LLM PROVIDERS:")
        for provider, info in status["llm_providers"].items():
            status_icon = "✅" if info["available"] else "❌"
            active_icon = " [ACTIVE]" if info["active"] else ""
            print(f"  {status_icon} {provider.upper()}{active_icon}")
            if info["available"] and info["model_info"]:
                model_info = info["model_info"]
                print(f"      Model: {model_info['model']}")
                print(f"      Temperature: {model_info['temperature']}")
        
        print("\n🔤 EMBEDDING PROVIDERS:")
        for provider, info in status["embedding_providers"].items():
            status_icon = "✅" if info["available"] else "❌"
            active_icon = " [ACTIVE]" if info["active"] else ""
            print(f"  {status_icon} {provider.upper()}{active_icon}")
            if info["available"] and info["embedding_dimension"]:
                print(f"      Dimension: {info['embedding_dimension']}")
        
        print("\n📊 DATABASE:")
        print(f"  📋 Tables scanned: {len(self.scanner.get_table_names()) if hasattr(self.scanner, 'get_table_names') else 'N/A'}")
        print(f"  🔍 Vector store: {'Ready' if self.vector_store_manager._vector_store else 'Not loaded'}")
        
        print("="*60 + "\n")

    def query(self, question: str) -> dict:
        """Process a natural language query"""
        if not self.query_processor:
            return {
                "error": "System not initialized. Call initialize() first.",
                "answer": None,
                "context": None
            }

        try:
            return self.query_processor.process_query(question)
        except Exception as e:
            return {
                "error": f"Query processing error: {str(e)}",
                "answer": None,
                "context": None
            }

    def switch_llm_provider(self, provider_name: str) -> bool:
        """Switch to a different LLM provider"""
        from llm_providers import LLMProvider
        
        # Convert string to enum
        provider_map = {
            "openai": LLMProvider.OPENAI,
            "ollama": LLMProvider.OLLAMA,
            "custom": LLMProvider.CUSTOM
        }
        
        provider_type = provider_map.get(provider_name.lower())
        if not provider_type:
            print(f"❌ Unknown provider: {provider_name}")
            return False
        
        success = self.provider_manager.switch_llm_provider(provider_type)
        if success:
            # Reinitialize SQL agent with new provider
            try:
                langchain_llm = self.provider_manager.get_langchain_llm()
                self.sql_agent = SQLAgent.from_langchain_llm(langchain_llm, self.scanner)
                print(f"✅ Switched to {provider_name} and updated SQL agent")
            except Exception as e:
                print(f"⚠️ Switched provider but failed to update SQL agent: {e}")
                return False
        
        return success
    
    def switch_embedding_provider(self, provider_name: str) -> bool:
        """Switch to a different embedding provider"""
        from llm_providers import LLMProvider
        
        provider_map = {
            "openai": LLMProvider.OPENAI,
            "ollama": LLMProvider.OLLAMA,
            "custom": LLMProvider.CUSTOM
        }
        
        provider_type = provider_map.get(provider_name.lower())
        if not provider_type:
            print(f"❌ Unknown provider: {provider_name}")
            return False
        
        success = self.provider_manager.switch_embedding_provider(provider_type)
        if success:
            # Update vector store with new embeddings
            try:
                langchain_embeddings = self.provider_manager.get_langchain_embeddings()
                if self.vector_store_manager._vector_store:
                    self.vector_store_manager._vector_store._embedding = langchain_embeddings
                print(f"✅ Switched to {provider_name} and updated vector store")
            except Exception as e:
                print(f"⚠️ Switched provider but failed to update vector store: {e}")
                return False
        
        return success

    def get_system_info(self) -> dict:
        """Get comprehensive system information"""
        return {
            "providers": self.provider_manager.list_available_providers(),
            "database_config": {
                "url": self.db_config.url,
                "type": self.db_config.type
            },
            "rag_config": {
                "vector_store_path": self.rag_config.vector_store_path,
                "similarity_search_k": self.rag_config.similarity_search_k,
                "table_sample_limit": self.rag_config.table_sample_limit
            },
            "initialized": bool(self.query_processor)
        }


def create_multi_llm_rag_system_from_env() -> MultiLLMDatabaseRAGSystem:
    """Create RAG system from environment variables"""
    # Load configurations
    db_config = DatabaseConfig.from_env()
    multi_llm_config = MultiLLMConfig.from_env()
    rag_config = RAGConfig.from_env()
    
    # Create provider manager from environment
    provider_manager = create_provider_manager_from_env()
    
    return MultiLLMDatabaseRAGSystem(
        db_config=db_config,
        multi_llm_config=multi_llm_config,
        rag_config=rag_config,
        provider_manager=provider_manager
    )
