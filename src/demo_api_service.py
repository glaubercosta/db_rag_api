"""
Demo API Service - Simplified version without OpenAI dependency
"""

import time
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from api_models import (
    QueryResponse, SchemaResponse, TableInfo, 
    DatabaseStatsResponse, HealthResponse, InitializeResponse
)
from config import DatabaseConfig, RAGConfig
from database_scanner import DatabaseScanner


class DemoAPIService:
    """Demo service layer for API operations without OpenAI"""
    
    def __init__(self):
        self.scanner: Optional[DatabaseScanner] = None
        self.db_config: Optional[DatabaseConfig] = None
        self.rag_config: Optional[RAGConfig] = None
        self._initialized = False
        self._initialization_error = None
    
    async def initialize(self, force_rebuild: bool = False) -> InitializeResponse:
        """Initialize the demo system"""
        start_time = time.time()
        
        try:
            # Load configurations
            self.db_config = DatabaseConfig.from_env()
            self.rag_config = RAGConfig.from_env()
            
            # Initialize scanner only
            self.scanner = DatabaseScanner(self.db_config)
            
            # Test database connection
            table_names = self.scanner.get_table_names()
            
            self._initialized = True
            self._initialization_error = None
            
            return InitializeResponse(
                success=True,
                message="Demo system initialized successfully (without OpenAI)",
                vector_store_created=False,  # Demo mode
                tables_indexed=len(table_names),
                initialization_time=time.time() - start_time
            )
                
        except Exception as e:
            self._initialized = False
            self._initialization_error = str(e)
            
            return InitializeResponse(
                success=False,
                message="Demo system initialization failed",
                vector_store_created=False,
                tables_indexed=0,
                initialization_time=time.time() - start_time,
                error=str(e)
            )
    
    def _ensure_initialized(self):
        """Ensure the system is initialized"""
        if not self._initialized or not self.scanner:
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
        """Process a database query in demo mode"""
        start_time = time.time()
        
        try:
            self._ensure_initialized()
            
            if query_type == "natural_language":
                # Demo: Convert simple natural language to SQL
                sql_query = self._demo_natural_language_to_sql(query)
                explanation = f"Demo mode: Simulated natural language processing for '{query}'"
                
                if sql_query:
                    try:
                        results = self.scanner.query_table_sample(sql_query, limit=limit)
                        if isinstance(results, dict) and 'data' in results:
                            result_data = results['data']
                        else:
                            result_data = results if isinstance(results, list) else []
                    except Exception as e:
                        # If SQL fails, return demo data
                        result_data = self._get_demo_data(query)
                else:
                    result_data = self._get_demo_data(query)
                
                return QueryResponse(
                    success=True,
                    query=query,
                    sql_query=sql_query,
                    results=result_data,
                    row_count=len(result_data),
                    execution_time=time.time() - start_time,
                    explanation=explanation if include_explanation else None
                )
                
            elif query_type == "sql":
                # Direct SQL execution
                try:
                    results = self.scanner.query_table_sample(query, limit=limit)
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
                except Exception as e:
                    return QueryResponse(
                        success=False,
                        query=query,
                        sql_query=query,
                        results=[],
                        row_count=0,
                        execution_time=time.time() - start_time,
                        error=str(e)
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
    
    def _demo_natural_language_to_sql(self, query: str) -> Optional[str]:
        """Demo: Simple natural language to SQL conversion"""
        query_lower = query.lower()
        
        # Simple pattern matching for demo
        if "top" in query_lower and "customer" in query_lower:
            if "revenue" in query_lower:
                return "SELECT * FROM customers ORDER BY total_revenue DESC LIMIT 5"
        
        if "order" in query_lower and ("last" in query_lower or "recent" in query_lower):
            return "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10"
        
        if "product" in query_lower and "price" in query_lower:
            return "SELECT * FROM products ORDER BY price DESC LIMIT 10"
        
        if "customer" in query_lower and "all" in query_lower:
            return "SELECT * FROM customers LIMIT 10"
        
        if "product" in query_lower and "all" in query_lower:
            return "SELECT * FROM products LIMIT 10"
        
        # Default fallback
        return "SELECT * FROM customers LIMIT 5"
    
    def _get_demo_data(self, query: str) -> List[Dict[str, Any]]:
        """Get demo data when SQL fails"""
        return [
            {
                "demo_note": "This is demo data",
                "query": query,
                "message": "In demo mode - real OpenAI integration would provide better results"
            }
        ]
    
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
                table_names = self.scanner.get_table_names()
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
            stats = self.scanner.get_table_stats(table_name)
            
            # Get column info from scanner
            schema = self.scanner.scan_database()
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
                    sample_result = self.scanner.query_table_sample(
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
            
            table_names = self.scanner.get_table_names()
            total_tables = len(table_names)
            total_columns = 0
            table_stats = []
            
            for table_name in table_names:
                try:
                    stats = self.scanner.get_table_stats(table_name)
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
                database_size="Not available in demo mode",
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
            if self.scanner:
                try:
                    self.scanner.get_table_names()
                    database_connected = True
                except:
                    database_connected = False
            
            return HealthResponse(
                status="healthy" if database_connected else "degraded",
                version="1.0.0-demo",
                database_connected=database_connected,
                vector_store_initialized=False,  # Demo mode
                openai_configured=False  # Demo mode
            )
            
        except Exception:
            return HealthResponse(
                status="unhealthy",
                version="1.0.0-demo",
                database_connected=False,
                vector_store_initialized=False,
                openai_configured=False
            )


# Demo service instance
demo_api_service = DemoAPIService()
