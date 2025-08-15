"""
Main RAG system for relational databases
"""
import os
import traceback
from langchain_openai import OpenAIEmbeddings

from config import DatabaseConfig, OpenAIConfig, RAGConfig
from database_scanner import DatabaseScanner
from vector_store_manager import VectorStoreManager
from sql_agent import SQLAgent, RAGQueryProcessor


class DatabaseRAGSystem:
    """Main system coordinating all components"""

    def __init__(
        self,
        db_config: DatabaseConfig,
        openai_config: OpenAIConfig,
        rag_config: RAGConfig,
    ):
        self.db_config = db_config
        self.openai_config = openai_config
        self.rag_config = rag_config

        # Initialize components
        self.scanner = DatabaseScanner(db_config)
        self.vector_store_manager = VectorStoreManager(rag_config)
        self.sql_agent = SQLAgent(openai_config, self.scanner)

        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            api_key=openai_config.api_key,
            model=openai_config.embedding_model,
        )

        self.query_processor = None

    def initialize(self, force_rebuild: bool = False) -> bool:
        """Initialize system building or loading the vector store.

        You can force a rebuild by:
        - Passing force_rebuild=True when calling initialize()
        - Setting environment variable RAG_FORCE_REBUILD=1|true|yes
        """
        try:
            if not force_rebuild:
                # Allow environment variable override
                env_force = os.getenv("RAG_FORCE_REBUILD", "").lower()
                if env_force in {"1", "true", "yes"}:
                    force_rebuild = True
            vector_store_path = self.rag_config.vector_store_path
            vector_store_exists = (
                vector_store_path and os.path.exists(vector_store_path)
            )

            def _has_faiss_files(path: str) -> bool:
                if not path:
                    return False
                try:
                    entries = os.listdir(path)
                except OSError:
                    return False
                # Typical FAISS local save includes index.faiss + index.pkl
                return any(f.endswith(".faiss") for f in entries)

            if (
                not force_rebuild
                and vector_store_exists
                and _has_faiss_files(vector_store_path)
            ):
                print("Loading existing vector store...")
                try:
                    self.vector_store_manager.load_vector_store(
                        vector_store_path, self.embeddings
                    )
                except Exception as e:
                    print(f"Failed to load existing vector store: {e}")
                    print("Regenerating vector store for security...")
                    self._build_vector_store()
            else:
                if vector_store_exists and not _has_faiss_files(
                    vector_store_path
                ):
                    print(
                        "Vector store directory exists but FAISS files are "
                        "missing; rebuilding index..."
                    )
                else:
                    print("Building new vector store...")
                self._build_vector_store()

            # Initialize query processor
            self.query_processor = RAGQueryProcessor(
                self.scanner, self.vector_store_manager, self.sql_agent
            )

            print("RAG system initialized successfully!")
            return True
        except Exception as e:  # noqa: BLE001
            print(f"Error initializing system: {e}")
            traceback.print_exc()
            return False

    def _build_vector_store(self):
        """Build vector store from database content"""
        print("Scanning database...")
        schema = self.scanner.scan_database()

        print("Creating documents from schema...")
        schema_docs = self.vector_store_manager.create_documents_from_schema(
            schema
        )

        print("Creating documents from data...")
        data_documents = self.vector_store_manager.create_documents_from_data(
            self.scanner, schema
        )

        all_documents = schema_docs + data_documents
        print(f"Total documents created: {len(all_documents)}")

        print("Building vector store...")
        self.vector_store_manager.build_vector_store(
            all_documents, self.embeddings
        )

    def ask(self, question: str) -> dict:
        """Main interface to ask natural language questions"""
        if not self.query_processor:
            return {
                "error": "System not initialized. Run initialize() first.",
                "status": "error",
            }

        return self.query_processor.process_question(question)

    def get_schema_info(self) -> str:
        """Return schema information"""
        if not self.query_processor:
            return "System not initialized."

        return self.query_processor.get_schema_summary()

    def get_table_preview(self, table_name: str, limit: int = 10) -> dict:
        """Return a preview (sample rows) for a table"""
        if not self.query_processor:
            return {"error": "System not initialized.", "status": "error"}

        return self.query_processor.get_table_sample(table_name, limit)

    def get_available_tables(self) -> list:
        """Return list of available table names"""
        try:
            return self.scanner.get_table_names()
        except Exception:  # noqa: BLE001
            return []

    def close(self):
        """Close resources / connections"""
        if hasattr(self, "scanner"):
            self.scanner.close()


def create_system_from_env() -> DatabaseRAGSystem:
    """Factory creating system from environment variables"""
    db_config = DatabaseConfig.from_env()
    openai_config = OpenAIConfig.from_env()
    rag_config = RAGConfig.from_env()

    return DatabaseRAGSystem(db_config, openai_config, rag_config)


# Example usage
if __name__ == "__main__":  # pragma: no cover
    # Load environment configurations
    system = create_system_from_env()

    try:
        # Initialize the system
        if system.initialize():
            # Usage examples
            print("\n" + "=" * 50)
            print("DATABASE INFORMATION")
            print("=" * 50)
            print(system.get_schema_info())

            print("\n" + "=" * 50)
            print("AVAILABLE TABLES")
            print("=" * 50)
            tables = system.get_available_tables()
            for table in tables:
                print(f"- {table}")

            print("\n" + "=" * 50)
            print("SAMPLE QUERY")
            print("=" * 50)

            # Sample question
            question = (
                "What are the main tables in the system and their "
                "relationships?"
            )
            result = system.ask(question)

            if result["status"] == "success":
                print(f"Question: {result['question']}")
                print(f"Answer: {result['sql_response']}")
                print("\nContext used:")
                for ctx in result["relevant_context"]:
                    print(f"- {ctx['metadata']}")
            else:
                print(f"Error: {result['error']}")
    finally:
        system.close()
