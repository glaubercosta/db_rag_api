"""
SQL Agent for natural language query processing with multiple LLM support
"""
from typing import Optional, Union
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_core.language_models.base import BaseLanguageModel

from config import OpenAIConfig
from database_scanner import DatabaseScanner
from vector_store_manager import VectorStoreManager


class SQLAgent:
    """Processes natural language SQL queries using any LLM"""

    def __init__(self, config: OpenAIConfig, scanner: DatabaseScanner):
        """Initialize SQL Agent with OpenAI config (legacy compatibility)"""
        self.config = config
        self.scanner = scanner
        self.db = SQLDatabase(scanner.engine)
        self.llm = ChatOpenAI(
            model=config.model, api_key=config.api_key, temperature=0
        )
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            handle_parsing_errors=True,
        )
    
    @classmethod
    def from_langchain_llm(cls, llm: BaseLanguageModel, scanner: DatabaseScanner):
        """Create SQL Agent from any LangChain-compatible LLM"""
        # Create a new instance without going through __init__
        instance = cls.__new__(cls)
        
        # Set attributes directly
        instance.config = None  # No specific config for multi-LLM
        instance.scanner = scanner
        instance.db = SQLDatabase(scanner.engine)
        instance.llm = llm
        instance.toolkit = SQLDatabaseToolkit(db=instance.db, llm=llm)
        instance.agent = create_sql_agent(
            llm=llm,
            toolkit=instance.toolkit,
            verbose=True,
            handle_parsing_errors=True,
        )
        
        return instance

    def query(self, question: str, context: Optional[str] = None) -> str:
        """Execute a natural language query (optionally with context)"""
        if context:
            prompt = (
                "Database context (schema and data):\n"
                f"{context}\n\n"
                f"Question: {question}\n\n"
                "Use the provided context to better understand the database "
                "structure before generating and executing the SQL query."
            )
        else:
            prompt = question
        try:
            response = self.agent.run(prompt)
            return response
        except Exception as e:  # noqa: BLE001
            return f"Error processing query: {str(e)}"

    def query_with_rag(
        self,
        question: str,
        vector_store_manager: VectorStoreManager = None,
        k: Optional[int] = None,
        pre_retrieved_docs: Optional[list] = None,
    ) -> str:
        """Execute query using retrieved augmented context (RAG)
        
        Args:
            question: The question to process
            vector_store_manager: Vector store manager (used if pre_retrieved_docs is None)
            k: Number of documents to retrieve (used if pre_retrieved_docs is None)
            pre_retrieved_docs: Already retrieved documents to avoid duplicate search
        """
        if pre_retrieved_docs is not None:
            relevant_docs = pre_retrieved_docs
        else:
            if vector_store_manager is None:
                raise ValueError("Either vector_store_manager or pre_retrieved_docs must be provided")
            relevant_docs = vector_store_manager.search_similar(question, k=k)
        
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"Source: {doc.metadata}")
            context_parts.append(doc.page_content)
            context_parts.append("")
        context = "\n".join(context_parts)
        return self.query(question, context)

    def query_with_rag_simple(
        self,
        question: str,
        vector_store_manager: VectorStoreManager,
        k: Optional[int] = None,
    ) -> str:
        """Simplified RAG query (for backward compatibility)"""
        return self.query_with_rag(
            question=question,
            vector_store_manager=vector_store_manager,
            k=k
        )


class RAGQueryProcessor:
    """High-level processor integrating retrieval + SQL agent"""

    def __init__(
        self,
        scanner: DatabaseScanner,
        vector_store_manager: VectorStoreManager,
        sql_agent: SQLAgent,
    ):
        self.scanner = scanner
        self.vector_store_manager = vector_store_manager
        self.sql_agent = sql_agent

    def process_question(self, question: str) -> dict:
        """Process a question and return full answer + context"""
        try:
            # Recuperar documentos relevantes uma única vez
            relevant_docs = self.vector_store_manager.search_similar(question)
            
            # Passar os documentos já recuperados para evitar duplicação
            sql_response = self.sql_agent.query_with_rag(
                question, 
                pre_retrieved_docs=relevant_docs
            )
            
            return {
                "question": question,
                "sql_response": sql_response,
                "relevant_context": [
                    {
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata,
                    }
                    for doc in relevant_docs
                ],
                "status": "success",
            }
        except Exception as e:  # noqa: BLE001
            return {"question": question, "error": str(e), "status": "error"}

    def get_schema_summary(self) -> str:
        """Return database schema summary"""
        try:
            schema = self.scanner.scan_database()
            return schema.to_text()
        except Exception as e:  # noqa: BLE001
            return f"Error getting schema: {e}"

    def get_table_sample(self, table_name: str, limit: int = 10) -> dict:
        """Return a sample of data from a specific table"""
        try:
            df = self.scanner.query_table_sample(table_name, limit)
            return {
                "table_name": table_name,
                "data": df.to_dict("records"),
                "columns": list(df.columns),
                "row_count": len(df),
                "status": "success",
            }
        except Exception as e:  # noqa: BLE001
            return {
                "table_name": table_name,
                "error": str(e),
                "status": "error",
            }
