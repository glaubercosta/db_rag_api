"""
Multi-LLM RAG System Usage Examples

This script demonstrates how to use the enhanced RAG system with multiple LLM providers
including OpenAI, Ollama (local models), and custom enterprise APIs.
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.multi_llm_rag_system import MultiLLMDatabaseRAGSystem
from src.config_multi_llm import DatabaseConfig, MultiLLMConfig, RAGConfig
from src.llm_providers.provider_manager import LLMProviderManager
from src.llm_providers import LLMProvider, LLMConfig, EmbeddingConfig


def setup_environment_examples():
    """Show different environment setups"""
    print("=" * 60)
    print("🔧 ENVIRONMENT SETUP EXAMPLES")
    print("=" * 60)
    
    print("\n1️⃣ OpenAI Only Setup:")
    print("   export OPENAI_API_KEY='your-key-here'")
    print("   export OPENAI_MODEL='gpt-4'")
    print("   export OPENAI_EMBEDDING_MODEL='text-embedding-ada-002'")
    
    print("\n2️⃣ Ollama (Local) Only Setup:")
    print("   export OLLAMA_MODEL='llama2'")
    print("   export OLLAMA_EMBEDDING_MODEL='llama2'")
    print("   export OLLAMA_BASE_URL='http://localhost:11434'")
    print("   # Make sure Ollama is running: ollama serve")
    
    print("\n3️⃣ Enterprise/Custom API Setup:")
    print("   export CUSTOM_LLM_API_BASE='https://your-company-api.com'")
    print("   export CUSTOM_LLM_MODEL='your-model'")
    print("   export CUSTOM_LLM_API_KEY='your-enterprise-key'")
    print("   export CUSTOM_LLM_FORMAT='openai'")
    
    print("\n4️⃣ Mixed Setup (Multiple Providers):")
    print("   # Configure multiple providers and set preferences")
    print("   export PREFERRED_LLM_PROVIDER='openai'")
    print("   export PREFERRED_EMBEDDING_PROVIDER='custom'")
    print("   # + any combination of the above")


def demo_basic_usage():
    """Demonstrate basic multi-LLM usage"""
    print("\n" + "=" * 60)
    print("🚀 BASIC USAGE DEMO")
    print("=" * 60)
    
    try:
        # Method 1: Create from environment variables
        print("\n📋 Method 1: Create from Environment")
        from src.multi_llm_rag_system import create_multi_llm_rag_system_from_env
        
        rag_system = create_multi_llm_rag_system_from_env()
        
        if rag_system.initialize():
            print("✅ System initialized successfully!")
            
            # Example query
            result = rag_system.query("How many users are in the database?")
            print(f"\n🤔 Query: How many users are in the database?")
            print(f"💡 Answer: {result.get('answer', 'No answer')}")
            
            if result.get('error'):
                print(f"⚠️ Error: {result['error']}")
        else:
            print("❌ Failed to initialize system")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have at least one LLM provider configured!")


def demo_provider_switching():
    """Demonstrate switching between providers"""
    print("\n" + "=" * 60)
    print("🔄 PROVIDER SWITCHING DEMO")
    print("=" * 60)
    
    # This would work if you have multiple providers configured
    try:
        from src.multi_llm_rag_system import create_multi_llm_rag_system_from_env
        
        rag_system = create_multi_llm_rag_system_from_env()
        
        if rag_system.initialize():
            print("✅ System initialized!")
            
            # Show current status
            status = rag_system.get_system_info()
            print(f"\n📊 Available Providers:")
            for provider, info in status["providers"]["llm_providers"].items():
                active = " [ACTIVE]" if info["active"] else ""
                available = "✅" if info["available"] else "❌"
                print(f"   {available} {provider}{active}")
            
            print(f"\n🔄 Trying to switch providers...")
            
            # Try switching to different providers
            providers_to_try = ["ollama", "openai", "custom"]
            for provider in providers_to_try:
                success = rag_system.switch_llm_provider(provider)
                if success:
                    print(f"✅ Switched to {provider}")
                    
                    # Test a query with the new provider
                    result = rag_system.query("What tables exist in this database?")
                    print(f"   🤔 Query result: {result.get('answer', 'No answer')[:100]}...")
                    break
                else:
                    print(f"❌ Could not switch to {provider}")
        else:
            print("❌ Failed to initialize system")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_manual_configuration():
    """Demonstrate manual provider configuration"""
    print("\n" + "=" * 60)
    print("⚙️ MANUAL CONFIGURATION DEMO")
    print("=" * 60)
    
    try:
        # Create configurations manually
        db_config = DatabaseConfig(
            url="sqlite:///./sample_data.db",
            type="sqlite"
        )
        
        # Create provider manager manually
        manager = LLMProviderManager()
        
        print("🔧 Adding providers manually...")
        
        # Add OpenAI if key is available
        if os.getenv("OPENAI_API_KEY"):
            openai_config = LLMConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.0
            )
            manager.add_llm_provider(LLMProvider.OPENAI, openai_config)
            
            openai_embedding_config = EmbeddingConfig(
                provider=LLMProvider.OPENAI,
                model_name="text-embedding-ada-002",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            manager.add_embedding_provider(LLMProvider.OPENAI, openai_embedding_config)
            print("   ✅ OpenAI configured")
        else:
            print("   ⏭️ OpenAI skipped (no API key)")
        
        # Add Ollama if available
        if os.getenv("OLLAMA_MODEL"):
            ollama_config = LLMConfig(
                provider=LLMProvider.OLLAMA,
                model_name=os.getenv("OLLAMA_MODEL", "llama2"),
                api_base="http://localhost:11434"
            )
            manager.add_llm_provider(LLMProvider.OLLAMA, ollama_config)
            print("   ✅ Ollama configured")
        else:
            print("   ⏭️ Ollama skipped (no model specified)")
        
        # Create RAG system with manual config
        multi_llm_config = MultiLLMConfig.from_env()  # Still use env for other settings
        rag_config = RAGConfig.from_env()
        
        rag_system = MultiLLMDatabaseRAGSystem(
            db_config=db_config,
            multi_llm_config=multi_llm_config,
            rag_config=rag_config,
            provider_manager=manager
        )
        
        if rag_system.initialize():
            print("✅ Manually configured system initialized!")
            
            # Show system status
            print(f"\n📊 System Status:")
            status = rag_system.get_system_info()
            print(f"   🗄️ Database: {status['database_config']['type']}")
            print(f"   🔍 Vector store: {'Ready' if status['initialized'] else 'Not ready'}")
            
        else:
            print("❌ Failed to initialize manually configured system")
            
    except Exception as e:
        print(f"❌ Error in manual configuration: {e}")


def demo_api_usage():
    """Show how to use the multi-LLM API"""
    print("\n" + "=" * 60)
    print("🌐 API USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n1️⃣ Start the Multi-LLM API:")
    print("   python multi_llm_api.py")
    print("   # API will be available at http://localhost:9000")
    
    print("\n2️⃣ Basic Query (curl):")
    print("""   curl -X POST http://localhost:9000/query \\
     -H "Authorization: Bearer dev-multi-llm-key-12345" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "How many users are there?"}'""")
    
    print("\n3️⃣ Query with Provider Override:")
    print("""   curl -X POST http://localhost:9000/query \\
     -H "Authorization: Bearer dev-multi-llm-key-12345" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "Show user statistics", "provider": "ollama"}'""")
    
    print("\n4️⃣ Check System Status:")
    print("""   curl -X GET http://localhost:9000/status \\
     -H "Authorization: Bearer dev-multi-llm-key-12345\"""")
    
    print("\n5️⃣ Switch Provider:")
    print("""   curl -X POST http://localhost:9000/switch-provider \\
     -H "Authorization: Bearer dev-multi-llm-key-12345" \\
     -H "Content-Type: application/json" \\
     -d '{"provider": "ollama", "type": "llm"}'""")


def main():
    """Main demonstration"""
    print("🎯 MULTI-LLM RAG SYSTEM DEMONSTRATIONS")
    print("=" * 60)
    print("This system supports:")
    print("  🤖 OpenAI (GPT models)")
    print("  🏠 Ollama (Local models like Llama, Mistral, etc.)")
    print("  🏢 Custom Enterprise APIs")
    print("  🔄 Dynamic provider switching")
    print("  📊 Comprehensive monitoring")
    
    # Show environment setup examples
    setup_environment_examples()
    
    # Run demos based on what's available
    print(f"\n🔍 Checking available providers...")
    
    providers_available = []
    if os.getenv("OPENAI_API_KEY"):
        providers_available.append("OpenAI")
    if os.getenv("OLLAMA_MODEL"):
        providers_available.append("Ollama")
    if os.getenv("CUSTOM_LLM_API_BASE"):
        providers_available.append("Custom")
    
    if providers_available:
        print(f"✅ Found providers: {', '.join(providers_available)}")
        
        # Run live demos
        demo_basic_usage()
        demo_provider_switching()
        demo_manual_configuration()
    else:
        print("⚠️ No providers configured. Please set up at least one provider to run demos.")
        print("📖 See .env.multi-llm.example for configuration examples")
    
    # Always show API usage (doesn't require live providers)
    demo_api_usage()
    
    print(f"\n🎉 Demo complete! Configure providers and try the examples above.")


if __name__ == "__main__":
    main()
