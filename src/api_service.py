"""
API Service layer for DB RAG API
Business logic and service methods for the FastAPI application
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from api_models import (
    QueryResponse, SchemaResponse, TableInfo, 
    DatabaseStatsResponse, HealthResponse, InitializeResponse
)
from rag_system import DatabaseRAGSystem
from config import DatabaseConfig, OpenAIConfig, RAGConfig


class APIService:
    """Service layer for API operations"""
    
    def __init__(self):
        self.rag_system: Optional[DatabaseRAGSystem] = None
        self.db_config: Optional[DatabaseConfig] = None
        self.openai_config: Optional[OpenAIConfig] = None
        self.rag_config: Optional[RAGConfig] = None
        self._initialized = False
        self._initialization_error = None
    
    async def initialize(self, force_rebuild: bool = False) -> InitializeResponse:
        """Initialize the RAG system"""
        start_time = time.time()
        
        try:
            # Load configurations
            self.db_config = DatabaseConfig.from_env()
            self.openai_config = OpenAIConfig.from_env()
            self.rag_config = RAGConfig.from_env()
            
            # Initialize RAG system
            self.rag_system = DatabaseRAGSystem(
                self.db_config, 
                self.openai_config, 
                self.rag_config
            )
            
            # Initialize the system
            success = self.rag_system.initialize(force_rebuild=force_rebuild)
            
            if success:
                self._initialized = True
                self._initialization_error = None
                
                # Get table count
                tables_indexed = len(self.rag_system.scanner.get_table_names())
                
                return InitializeResponse(
                    success=True,
                    message="System initialized successfully",
                    vector_store_created=True,
                    tables_indexed=tables_indexed,
                    initialization_time=time.time() - start_time
                )
            else:
                self._initialized = False
                self._initialization_error = "Failed to initialize vector store"
                
                return InitializeResponse(
                    success=False,
                    message="Failed to initialize system",
                    vector_store_created=False,
                    tables_indexed=0,
                    initialization_time=time.time() - start_time,
                    error="Vector store initialization failed"
                )
                
        except Exception as e:
            self._initialized = False
            self._initialization_error = str(e)
            
            return InitializeResponse(
                success=False,
                message="System initialization failed",
                vector_store_created=False,
                tables_indexed=0,
                initialization_time=time.time() - start_time,
                error=str(e)
            )
    
    def _ensure_initialized(self):
        """Ensure the system is initialized"""
        if not self._initialized or not self.rag_system:
            raise RuntimeError(
                f"System not initialized. Error: {self._initialization_error or 'Unknown'}"
            )
    
    async def process_query(
        self, 
        query: str, 
        query_type: str = "natural_language",
        limit: int = 10,
        include_explanation: bool = True
    ) -> QueryResponse:
        """Process a database query"""
        start_time = time.time()
        
        try:
            self._ensure_initialized()
            
            if query_type == "natural_language":
                # Use RAG system for natural language queries
                result = self.rag_system.ask(query)
                
                # Parse the result (assuming it's a string with SQL and explanation)
                sql_query = self._extract_sql_from_result(result)
                explanation = result if include_explanation else None
                
                # Execute the SQL to get actual results
                if sql_query:
                    results = self.rag_system.scanner.query_table_sample(
                        sql_query, limit=limit
                    )
                    if isinstance(results, dict) and 'data' in results:
                        result_data = results['data']
                    else:
                        result_data = results if isinstance(results, list) else []
                else:
                    result_data = []
                
                return QueryResponse(
                    success=True,
                    query=query,
                    sql_query=sql_query,
                    results=result_data,
                    row_count=len(result_data),
                    execution_time=time.time() - start_time,
                    explanation=explanation
                )
                
            elif query_type == "sql":
                # Direct SQL execution
                results = self.rag_system.scanner.query_table_sample(
                    query, limit=limit
                )
                if isinstance(results, dict) and 'data' in results:
                    result_data = results['data']
                else:
                    result_data = results if isinstance(results, list) else []
                
                return QueryResponse(
                    success=True,
                    query=query,
                    sql_query=query,
                    results=result_data,
                    row_count=len(result_data),
                    execution_time=time.time() - start_time,
                    explanation="Direct SQL execution" if include_explanation else None
                )
            
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
                
        except Exception as e:
            return QueryResponse(
                success=False,
                query=query,
                sql_query=None,
                results=[],
                row_count=0,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    def _extract_sql_from_result(self, result: str) -> Optional[str]:
        """Extract SQL query from RAG result"""
        if not result:
            return None
            
        # Look for SQL patterns in the result
        lines = result.split('\n')
        for line in lines:
            line = line.strip()
            if (line.upper().startswith('SELECT') or 
                line.upper().startswith('WITH') or
                line.upper().startswith('UPDATE') or
                line.upper().startswith('INSERT') or
                line.upper().startswith('DELETE')):
                return line
        
        return None
    
    async def get_schema(
        self, 
        table_name: Optional[str] = None,
        include_sample_data: bool = False,
        sample_limit: int = 5
    ) -> SchemaResponse:
        """Get database schema information"""
        try:
            self._ensure_initialized()
            
            tables_info = []
            
            if table_name:
                # Get specific table info
                table_info = await self._get_table_info(
                    table_name, include_sample_data, sample_limit
                )
                if table_info:
                    tables_info.append(table_info)
            else:
                # Get all tables
                table_names = self.rag_system.scanner.get_table_names()
                for name in table_names:
                    table_info = await self._get_table_info(
                        name, include_sample_data, sample_limit
                    )
                    if table_info:
                        tables_info.append(table_info)
            
            return SchemaResponse(
                success=True,
                database_type=self.db_config.type,
                tables=tables_info,
                total_tables=len(tables_info)
            )
            
        except Exception as e:
            return SchemaResponse(
                success=False,
                database_type="unknown",
                tables=[],
                total_tables=0,
                error=str(e)
            )
    
    async def _get_table_info(
        self, 
        table_name: str, 
        include_sample_data: bool = False,
        sample_limit: int = 5
    ) -> Optional[TableInfo]:
        """Get information for a specific table"""
        try:
            # Get table stats
            stats = self.rag_system.scanner.get_table_stats(table_name)
            
            # Get column info from scanner
            schema = self.rag_system.scanner.scan_database()
            table_schema = None
            
            for table in schema.tables:
                if table.name == table_name:
                    table_schema = table
                    break
            
            if not table_schema:
                return None
            
            # Format column information
            columns = []
            for col in table_schema.columns:
                columns.append({
                    "name": col.name,
                    "data_type": col.data_type,
                    "is_nullable": col.is_nullable,
                    "is_primary_key": col.is_primary_key
                })
            
            # Format foreign keys
            foreign_keys = []
            for fk in table_schema.foreign_keys:
                foreign_keys.append({
                    "column": fk.column_name,
                    "referenced_table": fk.referenced_table,
                    "referenced_column": fk.referenced_column
                })
            
            # Get sample data if requested
            sample_data = None
            if include_sample_data:
                try:
                    sample_result = self.rag_system.scanner.query_table_sample(
                        table_name, limit=sample_limit
                    )
                    if isinstance(sample_result, dict) and 'data' in sample_result:
                        sample_data = sample_result['data']
                    elif isinstance(sample_result, list):
                        sample_data = sample_result
                except:
                    sample_data = []
            
            return TableInfo(
                table_name=table_name,
                column_count=stats.get('column_count', len(columns)),
                row_count=stats.get('row_count'),
                columns=columns,
                sample_data=sample_data,
                foreign_keys=foreign_keys
            )
            
        except Exception:
            return None
    
    async def get_database_stats(self) -> DatabaseStatsResponse:
        """Get database statistics"""
        try:
            self._ensure_initialized()
            
            table_names = self.rag_system.scanner.get_table_names()
            total_tables = len(table_names)
            total_columns = 0
            table_stats = []
            
            for table_name in table_names:
                try:
                    stats = self.rag_system.scanner.get_table_stats(table_name)
                    total_columns += stats.get('column_count', 0)
                    table_stats.append({
                        "table_name": table_name,
                        "row_count": stats.get('row_count', 0),
                        "column_count": stats.get('column_count', 0)
                    })
                except:
                    # Skip tables that can't be analyzed
                    continue
            
            return DatabaseStatsResponse(
                success=True,
                total_tables=total_tables,
                total_columns=total_columns,
                database_size="Not available",  # Would need database-specific queries
                table_stats=table_stats
            )
            
        except Exception as e:
            return DatabaseStatsResponse(
                success=False,
                total_tables=0,
                total_columns=0,
                database_size="Error",
                table_stats=[],
                error=str(e)
            )
    
    async def health_check(self) -> HealthResponse:
        """Perform health check"""
        try:
            # Check database connection
            database_connected = False
            if self.rag_system and self.rag_system.scanner:
                try:
                    self.rag_system.scanner.get_table_names()
                    database_connected = True
                except:
                    database_connected = False
            
            # Check vector store
            vector_store_initialized = (
                self._initialized and 
                self.rag_system and 
                hasattr(self.rag_system, 'query_processor') and
                self.rag_system.query_processor is not None
            )
            
            # Check OpenAI configuration
            openai_configured = (
                self.openai_config and 
                self.openai_config.api_key and 
                len(self.openai_config.api_key) > 10
            )
            
            return HealthResponse(
                status="healthy" if database_connected else "degraded",
                version="1.0.0",
                database_connected=database_connected,
                vector_store_initialized=vector_store_initialized,
                openai_configured=openai_configured
            )
            
        except Exception as e:
            return HealthResponse(
                status="unhealthy",
                version="1.0.0",
                database_connected=False,
                vector_store_initialized=False,
                openai_configured=False
            )


# Global service instance
api_service = APIService()
