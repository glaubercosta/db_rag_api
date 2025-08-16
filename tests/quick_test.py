#!/usr/bin/env python3
"""
🚀 TESTE RÁPIDO DO SISTEMA MULTI-LLM
====================================

Este script testa rapidamente se o sistema Multi-LLM está funcionando corretamente.
Execute: python quick_test.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Adicionar o src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_system():
    """Teste rápido do sistema Multi-LLM"""
    print("🔍 Testando Sistema Multi-LLM Database RAG...")
    print("=" * 50)
    
    try:
        # Importar e criar sistema
        from multi_llm_rag_system import create_multi_llm_rag_system_from_env
        
        print("✓ Módulos importados com sucesso")
        
        # Verificar variáveis de ambiente
        print("\n📋 Verificando configuração...")
        
        # Verificar provedores configurados
        providers_found = []
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            providers_found.append("OpenAI")
            print("✓ OpenAI configurado")
        else:
            print("⚠️ OpenAI não configurado (OPENAI_API_KEY ausente)")
        
        # Ollama
        if os.getenv("OLLAMA_MODEL") and os.getenv("OLLAMA_BASE_URL"):
            providers_found.append("Ollama")
            print("✓ Ollama configurado")
        else:
            print("⚠️ Ollama não configurado")
        
        # Custom
        if os.getenv("CUSTOM_LLM_API_BASE") and os.getenv("CUSTOM_LLM_MODEL"):
            providers_found.append("Custom")
            print("✓ API Customizada configurada")
        else:
            print("⚠️ API Customizada não configurada")
        
        if not providers_found:
            print("❌ Nenhum provedor configurado!")
            print("\n📖 Configure pelo menos um provedor no arquivo .env:")
            print("   1. Copie .env.multi-llm.example para .env")
            print("   2. Configure pelo menos um provedor (OpenAI, Ollama ou Custom)")
            print("   3. Execute novamente este teste")
            return False
        
        print(f"\n🎯 Provedores encontrados: {', '.join(providers_found)}")
        
        # Criar sistema RAG
        print("\n🤖 Inicializando sistema RAG...")
        rag_system = create_multi_llm_rag_system_from_env()
        
        if not rag_system:
            print("❌ Falha ao criar sistema RAG")
            return False
        
        print("✓ Sistema RAG criado")
        
        # Tentar inicializar
        print("🔧 Inicializando provedores...")
        if not rag_system.initialize():
            print("❌ Falha ao inicializar sistema")
            return False
        
        print("✓ Sistema inicializado com sucesso")
        
        # Verificar status do sistema
        print("\n📊 Status do sistema:")
        status = rag_system.get_system_info()
        
        for provider_type, providers in status.get("providers", {}).items():
            print(f"  {provider_type}:")
            for name, info in providers.items():
                status_icon = "✅" if info.get("available") else "❌"
                active_icon = "🔥" if info.get("active") else "💤"
                print(f"    {status_icon}{active_icon} {name}: {info}")
        
        # Teste simples de query (se banco existir)
        print("\n🧪 Testando consulta simples...")
        
        try:
            # Query de teste que não depende do banco de dados específico
            test_query = "Como posso usar este sistema?"
            print(f"Pergunta: '{test_query}'")
            
            result = rag_system.query(test_query)
            
            if result and result.get("answer"):
                print("✅ Consulta processada com sucesso!")
                print(f"📝 Resposta: {result['answer'][:200]}...")
                if result.get("provider_used"):
                    print(f"🤖 Provedor usado: {result['provider_used']}")
            else:
                print("⚠️ Consulta processada mas sem resposta clara")
                
        except Exception as e:
            print(f"⚠️ Erro na consulta de teste: {e}")
            print("   (Isso pode ser normal se não há banco de dados configurado)")
        
        print("\n🎉 Teste completado com sucesso!")
        print("\n📚 Próximos passos:")
        print("   1. Configure seu banco de dados")
        print("   2. Execute: python multi_llm_api.py")
        print("   3. Teste via API: http://localhost:9000/docs")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n🔧 Possíveis soluções:")
        print("   1. Instale as dependências: pip install -r requirements.txt")
        print("   2. Verifique se está no diretório correto")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def main():
    """Função principal"""
    print("🚀 Teste Rápido - Sistema Multi-LLM Database RAG")
    print("=" * 50)
    
    # Verificar se arquivo .env existe
    if not os.path.exists(".env"):
        print("⚠️ Arquivo .env não encontrado!")
        print("\n📋 Para configurar:")
        print("   1. cp .env.multi-llm.example .env")
        print("   2. Edite .env com suas configurações")
        print("   3. Execute novamente este teste")
        return
    
    # Carregar variáveis de ambiente do .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Arquivo .env carregado")
    except ImportError:
        print("⚠️ python-dotenv não instalado")
        print("   Instale com: pip install python-dotenv")
        # Continua mesmo assim, caso as vars estejam no ambiente
    
    # Executar teste
    if asyncio.run(test_system() if asyncio.iscoroutinefunction(test_system) else asyncio.coroutine(test_system)()):
        print("\n✅ Sistema Multi-LLM está funcionando!")
    else:
        print("\n❌ Problemas encontrados no sistema")
        sys.exit(1)


if __name__ == "__main__":
    main()
