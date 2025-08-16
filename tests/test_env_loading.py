#!/usr/bin/env python3
"""
Teste de carregamento de variáveis .env pelo sistema Multi-LLM
"""
import os
import sys

# Add src to path - ajustado para nova estrutura
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from multi_llm_rag_system import create_multi_llm_rag_system_from_env
from config_multi_llm import MultiLLMConfig

def test_env_loading():
    """Testa se as variáveis do .env estão sendo carregadas"""
    print("🔍 TESTE DE CARREGAMENTO DO ARQUIVO .ENV")
    print("=" * 50)
    
    # Teste 1: Verificar se as variáveis estão no environment
    print("\n📋 1. VARIÁVEIS DO SISTEMA:")
    key_vars = [
        "OPENAI_API_KEY", "OLLAMA_BASE_URL", "OLLAMA_MODEL", 
        "DATABASE_URL", "DATABASE_PATH", "PREFERRED_LLM_PROVIDER"
    ]
    
    for var in key_vars:
        value = os.getenv(var)
        if value:
            # Mascarar chaves sensíveis
            if "API_KEY" in var:
                display_value = f"{value[:10]}***{value[-4:]}" if len(value) > 14 else "***"
            else:
                display_value = value
            print(f"   ✅ {var} = {display_value}")
        else:
            print(f"   ❌ {var} = (não definida)")
    
    # Teste 2: Verificar carregamento via MultiLLMConfig
    print("\n📋 2. CONFIGURAÇÃO MULTI-LLM:")
    try:
        config = MultiLLMConfig.from_env()
        print(f"   🤖 OpenAI disponível: {'✅' if config.openai else '❌'}")
        print(f"   🏠 Ollama disponível: {'✅' if config.ollama else '❌'}")
        print(f"   🏢 Custom disponível: {'✅' if config.custom else '❌'}")
        print(f"   📊 Total provedores: {len([p for p in [config.openai, config.ollama, config.custom] if p])}")
        
        if config.has_any_provider():
            print("   ✅ Sistema tem pelo menos um provedor configurado")
        else:
            print("   ❌ ERRO: Nenhum provedor configurado!")
            
    except Exception as e:
        print(f"   ❌ ERRO ao carregar MultiLLMConfig: {e}")
    
    # Teste 3: Verificar criação do sistema RAG
    print("\n📋 3. SISTEMA RAG:")
    try:
        rag_system = create_multi_llm_rag_system_from_env()
        print("   ✅ Sistema RAG criado com sucesso")
        
        # Verificar provedores disponíveis
        available_providers = rag_system.provider_manager.list_available_providers()
        print(f"   📊 LLM providers: {len(available_providers.get('llm_providers', {}))}")
        print(f"   📊 Embedding providers: {len(available_providers.get('embedding_providers', {}))}")
        
        for provider_name, info in available_providers.get('llm_providers', {}).items():
            status = "✅" if info.get('available') else "❌"
            print(f"      {status} {provider_name}: {info.get('reason', 'OK')}")
            
    except Exception as e:
        print(f"   ❌ ERRO ao criar sistema RAG: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_env_loading()
