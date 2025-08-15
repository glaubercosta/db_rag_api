"""
API Models for DB RAG API
Pydantic models for request/response validation and documentation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class QueryType(str, Enum):
    """Types of queries supported by the API"""
    NATURAL_LANGUAGE = "natural_language"
    SQL = "sql"
    SCHEMA_EXPLORATION = "schema_exploration"


class QueryRequest(BaseModel):
    """Request model for database queries"""
    query: str = Field(
        ..., 
        description="Natural language question or SQL query",
        example="What are the top 5 customers by revenue?"
    )
    query_type: QueryType = Field(
        default=QueryType.NATURAL_LANGUAGE,
        description="Type of query being submitted"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Maximum number of results to return"
    )
    include_explanation: Optional[bool] = Field(
        default=True,
        description="Include explanation of how the query was processed"
    )

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class QueryResponse(BaseModel):
    """Response model for database queries"""
    success: bool = Field(description="Whether the query was successful")
    query: str = Field(description="Original query submitted")
    sql_query: Optional[str] = Field(description="Generated SQL query (if applicable)")
    results: List[Dict[str, Any]] = Field(description="Query results")
    row_count: int = Field(description="Number of rows returned")
    execution_time: float = Field(description="Query execution time in seconds")
    explanation: Optional[str] = Field(description="Explanation of query processing")
    error: Optional[str] = Field(description="Error message if query failed")


class SchemaRequest(BaseModel):
    """Request model for schema exploration"""
    table_name: Optional[str] = Field(
        default=None,
        description="Specific table to explore (if not provided, returns all tables)",
        example="customers"
    )
    include_sample_data: Optional[bool] = Field(
        default=False,
        description="Include sample data from tables"
    )
    sample_limit: Optional[int] = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of sample rows to include"
    )


class TableInfo(BaseModel):
    """Model for table information"""
    table_name: str = Field(description="Name of the table")
    column_count: int = Field(description="Number of columns in the table")
    row_count: Optional[int] = Field(description="Number of rows in the table")
    columns: List[Dict[str, Any]] = Field(description="Column information")
    sample_data: Optional[List[Dict[str, Any]]] = Field(description="Sample rows from the table")
    foreign_keys: Optional[List[Dict[str, str]]] = Field(description="Foreign key relationships")


class SchemaResponse(BaseModel):
    """Response model for schema exploration"""
    success: bool = Field(description="Whether the schema request was successful")
    database_type: str = Field(description="Type of database (e.g., postgresql, mysql)")
    tables: List[TableInfo] = Field(description="Information about database tables")
    total_tables: int = Field(description="Total number of tables in the database")
    error: Optional[str] = Field(description="Error message if request failed")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(description="API status")
    version: str = Field(description="API version")
    database_connected: bool = Field(description="Database connection status")
    vector_store_initialized: bool = Field(description="Vector store initialization status")
    openai_configured: bool = Field(description="OpenAI configuration status")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(description="Error message")
    error_code: str = Field(description="Error code for client handling")
    details: Optional[Dict[str, Any]] = Field(description="Additional error details")


class DatabaseStatsResponse(BaseModel):
    """Response model for database statistics"""
    success: bool = Field(description="Whether the stats request was successful")
    total_tables: int = Field(description="Total number of tables")
    total_columns: int = Field(description="Total number of columns across all tables")
    database_size: Optional[str] = Field(description="Database size information")
    table_stats: List[Dict[str, Any]] = Field(description="Statistics for each table")
    error: Optional[str] = Field(description="Error message if request failed")


class InitializeRequest(BaseModel):
    """Request model for system initialization"""
    force_rebuild: Optional[bool] = Field(
        default=False,
        description="Force rebuild of vector store"
    )
    
    
class InitializeResponse(BaseModel):
    """Response model for system initialization"""
    success: bool = Field(description="Whether initialization was successful")
    message: str = Field(description="Initialization result message")
    vector_store_created: bool = Field(description="Whether vector store was created/updated")
    tables_indexed: int = Field(description="Number of tables indexed")
    initialization_time: float = Field(description="Time taken for initialization")
    error: Optional[str] = Field(default=None, description="Error message if initialization failed")
