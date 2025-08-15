"""
Multi-LLM FastAPI application for database RAG queries
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.multi_llm_rag_system import create_multi_llm_rag_system_from_env
from src.config_multi_llm import MultiLLMConfig

# Global RAG system instance
rag_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup RAG system"""
    global rag_system
    
    try:
        print("🚀 Starting Multi-LLM RAG API...")
        
        # Check if any LLM provider is configured
        multi_llm_config = MultiLLMConfig.from_env()
        if not multi_llm_config.has_any_provider():
            print("⚠️  WARNING: No LLM providers configured!")
            print("📋 Available providers:")
            print("   🤖 OpenAI: Set OPENAI_API_KEY")
            print("   🏠 Ollama: Set OLLAMA_MODEL and ensure Ollama is running")
            print("   🏢 Custom: Set CUSTOM_LLM_API_BASE and CUSTOM_LLM_MODEL")
            print("📖 See .env.multi-llm.example for configuration details")
        
        # Initialize RAG system
        rag_system = create_multi_llm_rag_system_from_env()
        
        if rag_system.initialize():
            print("✅ Multi-LLM RAG API initialized successfully!")
        else:
            print("❌ Failed to initialize RAG system")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)
    
    yield
    
    # Cleanup (if needed)
    print("🛑 Shutting down Multi-LLM RAG API...")

app = FastAPI(
    title="Multi-LLM Database RAG API",
    description="Natural language database queries with multiple LLM provider support",
    version="2.0.0",
    lifespan=lifespan
)

# Security
security = HTTPBearer(auto_error=False)
API_KEY = os.getenv("API_KEY", "dev-multi-llm-key-12345")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key"""
    if not credentials or credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    provider: Optional[str] = None  # Optional provider override

class QueryResponse(BaseModel):
    answer: str
    context: Optional[str] = None
    provider_info: Dict[str, Any]
    error: Optional[str] = None

class SystemStatusResponse(BaseModel):
    status: str
    providers: Dict[str, Any]
    database_info: Dict[str, Any]
    rag_info: Dict[str, Any]

class ProviderSwitchRequest(BaseModel):
    provider: str  # "openai", "ollama", or "custom"
    type: str  # "llm" or "embedding"

# API endpoints
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Multi-LLM Database RAG API",
        "version": "2.0.0",
        "description": "Natural language database queries with multiple LLM support",
        "endpoints": {
            "/query": "POST - Execute natural language database queries",
            "/status": "GET - Get system status and provider information", 
            "/providers": "GET - List available providers",
            "/switch-provider": "POST - Switch active LLM or embedding provider",
            "/health": "GET - Health check"
        },
        "authentication": "Bearer token required"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global rag_system
    if rag_system and rag_system.query_processor:
        return {"status": "healthy", "system": "ready"}
    else:
        return {"status": "unhealthy", "system": "not_ready"}

@app.post("/query", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
async def query_database(request: QueryRequest):
    """Execute a natural language database query"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Switch provider if requested
        if request.provider:
            success = rag_system.switch_llm_provider(request.provider)
            if not success:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to switch to provider: {request.provider}"
                )
        
        # Process query
        result = rag_system.query(request.query)
        
        # Get current provider info
        system_info = rag_system.get_system_info()
        active_providers = {}
        for provider, info in system_info["providers"]["llm_providers"].items():
            if info.get("active"):
                active_providers["llm"] = {
                    "name": provider,
                    "model": info.get("model_info", {}).get("model", "unknown")
                }
        for provider, info in system_info["providers"]["embedding_providers"].items():
            if info.get("active"):
                active_providers["embedding"] = {
                    "name": provider,
                    "dimension": info.get("embedding_dimension", "unknown")
                }
        
        return QueryResponse(
            answer=result.get("answer", "No answer generated"),
            context=result.get("context"),
            provider_info=active_providers,
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

@app.get("/status", response_model=SystemStatusResponse, dependencies=[Depends(verify_api_key)])
async def get_system_status():
    """Get comprehensive system status"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        system_info = rag_system.get_system_info()
        
        return SystemStatusResponse(
            status="ready" if system_info["initialized"] else "initializing",
            providers=system_info["providers"],
            database_info=system_info["database_config"],
            rag_info=system_info["rag_config"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")

@app.get("/providers", dependencies=[Depends(verify_api_key)])
async def list_providers():
    """List all available providers and their status"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    return rag_system.provider_manager.list_available_providers()

@app.post("/switch-provider", dependencies=[Depends(verify_api_key)])
async def switch_provider(request: ProviderSwitchRequest):
    """Switch active LLM or embedding provider"""
    global rag_system
    
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        if request.type == "llm":
            success = rag_system.switch_llm_provider(request.provider)
            message = f"LLM provider switched to {request.provider}" if success else f"Failed to switch to {request.provider}"
        elif request.type == "embedding":
            success = rag_system.switch_embedding_provider(request.provider)
            message = f"Embedding provider switched to {request.provider}" if success else f"Failed to switch to {request.provider}"
        else:
            raise HTTPException(status_code=400, detail="Type must be 'llm' or 'embedding'")
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        return {"success": True, "message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Provider switch error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Check for demo mode
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    if demo_mode:
        print("🎭 Running in Demo Mode (no LLM providers required)")
        print("📋 Set DEMO_MODE=false and configure providers for full functionality")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "9000")),
        reload=False
    )
