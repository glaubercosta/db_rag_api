"""
DB RAG API - FastAPI Application
Main FastAPI application with Swagger documentation
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_models import (
    QueryRequest, QueryResponse, SchemaRequest, SchemaResponse,
    HealthResponse, ErrorResponse, DatabaseStatsResponse,
    InitializeRequest, InitializeResponse
)
from auth import verify_api_key, check_rate_limit, get_auth_info

# Choose service based on environment
demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
if demo_mode or not os.getenv("OPENAI_API_KEY"):
    print("🔧 Running in Demo Mode (without OpenAI)")
    from demo_api_service import demo_api_service as api_service
else:
    print("🚀 Running in Full Mode (with OpenAI)")
    from api_service import api_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("🚀 Starting DB RAG API...")
    
    # Initialize the RAG system on startup
    init_result = await api_service.initialize()
    if init_result.success:
        print(f"✅ System initialized: {init_result.tables_indexed} tables indexed")
    else:
        print(f"⚠️  System initialization failed: {init_result.error}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down DB RAG API...")


# Create FastAPI application
app = FastAPI(
    title="DB RAG API",
    description="""
    ## 🗃️ Database RAG API

    A powerful API that enables natural language queries against relational databases using RAG (Retrieval-Augmented Generation) technology.

    ### 🚀 Features

    - **Natural Language Queries**: Ask questions in plain English
    - **SQL Execution**: Direct SQL query support
    - **Schema Exploration**: Discover database structure
    - **Smart Caching**: Optimized performance with vector storage
    - **Multi-Database Support**: PostgreSQL, MySQL, SQLite

    ### 🔐 Authentication

    This API uses Bearer token authentication. Include your API key in the Authorization header:

    ```
    Authorization: Bearer your-api-key-here
    ```

    ### 📊 Rate Limiting

    - **100 requests per hour** per API key
    - Rate limit headers included in responses
    - 429 status code when limit exceeded

    ### 🛠️ Getting Started

    1. **Initialize the system** using `/initialize` endpoint
    2. **Explore your database** with `/schema` endpoint
    3. **Ask questions** using `/query` endpoint

    ### 📝 Example Queries

    - "What are the top 5 customers by revenue?"
    - "Show me all orders from last month"
    - "Which products have the highest profit margin?"
    - "Find customers who haven't placed orders recently"

    ### 🔧 Development Mode

    In development mode (REQUIRE_AUTH=false), you can use the API without authentication.
    Default development API key: `dev-api-key-12345`
    """,
    version="1.0.0",
    contact={
        "name": "DB RAG API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": {"message": str(exc)}
        }
    )


# Health and Info Endpoints

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """Get API health status"""
    return await api_service.health_check()


@app.get(
    "/auth/info",
    tags=["Authentication"],
    summary="Authentication Info",
    description="Get information about authentication requirements and development keys"
)
async def auth_info():
    """Get authentication configuration info"""
    return get_auth_info()


# Core API Endpoints

@app.post(
    "/initialize",
    response_model=InitializeResponse,
    dependencies=[Depends(check_rate_limit)],
    tags=["System"],
    summary="Initialize System",
    description="""
    Initialize or reinitialize the RAG system. This will:
    - Scan the database schema
    - Build or rebuild the vector store
    - Index all tables for natural language queries
    
    **Note**: This may take a few minutes for large databases.
    """
)
async def initialize_system(
    request: InitializeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Initialize the RAG system"""
    return await api_service.initialize(force_rebuild=request.force_rebuild)


@app.post(
    "/query",
    response_model=QueryResponse,
    dependencies=[Depends(check_rate_limit)],
    tags=["Queries"],
    summary="Execute Query",
    description="""
    Execute a database query using natural language or SQL.
    
    **Natural Language Examples:**
    - "What are the top 5 customers by revenue?"
    - "Show me orders from last month"
    - "Which products are most popular?"
    
    **SQL Examples:**
    - "SELECT * FROM customers LIMIT 10"
    - "SELECT COUNT(*) FROM orders WHERE created_date > '2024-01-01'"
    """
)
async def execute_query(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Execute a database query"""
    return await api_service.process_query(
        query=request.query,
        query_type=request.query_type,
        limit=request.limit,
        include_explanation=request.include_explanation
    )


@app.post(
    "/schema",
    response_model=SchemaResponse,
    dependencies=[Depends(check_rate_limit)],
    tags=["Schema"],
    summary="Explore Schema",
    description="""
    Explore the database schema. You can:
    - Get information about all tables
    - Get detailed info about a specific table
    - Include sample data from tables
    
    This is useful for understanding your database structure before querying.
    """
)
async def get_schema(
    request: SchemaRequest,
    api_key: str = Depends(verify_api_key)
):
    """Get database schema information"""
    return await api_service.get_schema(
        table_name=request.table_name,
        include_sample_data=request.include_sample_data,
        sample_limit=request.sample_limit
    )


@app.get(
    "/stats",
    response_model=DatabaseStatsResponse,
    dependencies=[Depends(check_rate_limit)],
    tags=["Statistics"],
    summary="Database Statistics",
    description="Get comprehensive statistics about the database including table counts, row counts, and column information"
)
async def get_database_stats(api_key: str = Depends(verify_api_key)):
    """Get database statistics"""
    return await api_service.get_database_stats()


# Convenience Endpoints

@app.get(
    "/",
    tags=["Info"],
    summary="API Information",
    description="Basic API information and links to documentation"
)
async def root():
    """API root endpoint"""
    return {
        "name": "DB RAG API",
        "version": "1.0.0",
        "description": "Natural language database queries using RAG technology",
        "documentation": "/docs",
        "health": "/health",
        "authentication": "/auth/info"
    }


@app.get(
    "/tables",
    dependencies=[Depends(check_rate_limit)],
    tags=["Schema"],
    summary="List Tables",
    description="Get a simple list of all table names in the database"
)
async def list_tables(api_key: str = Depends(verify_api_key)):
    """Get list of table names"""
    try:
        schema_response = await api_service.get_schema()
        if schema_response.success:
            table_names = [table.table_name for table in schema_response.tables]
            return {
                "success": True,
                "tables": table_names,
                "count": len(table_names)
            }
        else:
            return {
                "success": False,
                "error": schema_response.error,
                "tables": [],
                "count": 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tables": [],
            "count": 0
        }


if __name__ == "__main__":
    import uvicorn
    
    # Configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 Starting DB RAG API on {host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )
