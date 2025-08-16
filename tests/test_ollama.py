#!/usr/bin/env python3
"""
🧪 TESTE DO PROVEDOR OLLAMA
===========================

Script para verificar se o servidor Ollama está ativo e funcionando corretamente.
Execute: python test_ollama.py
"""

import os
import sys
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Adicionar o src ao path - ajustado para nova estrutura
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def load_env():
    """Carregar variáveis de ambiente do .env"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Arquivo .env carregado")
        return True
    except ImportError:
        print("⚠️ python-dotenv não instalado")
        print("   As variáveis de ambiente do sistema serão usadas")
        return False

def get_ollama_config() -> Dict[str, str]:
    """Obter configuração do Ollama a partir das variáveis de ambiente"""
    return {
        'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
        'model': os.getenv('OLLAMA_MODEL', 'llama2'),
        'embedding_model': os.getenv('OLLAMA_EMBEDDING_MODEL', 'llama2')
    }

def test_ollama_health(base_url: str) -> bool:
    """Testar se o servidor Ollama está rodando"""
    try:
        # Remover barra final se existir
        base_url = base_url.rstrip('/')
        
        print(f"🔍 Testando conexão com: {base_url}")
        
        # Testar endpoint básico
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        
        if response.status_code == 200:
            print("✅ Servidor Ollama está ativo!")
            return True
        else:
            print(f"❌ Servidor respondeu com código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor Ollama")
        print(f"   Verifique se o servidor está rodando em: {base_url}")
        return False
    except requests.exceptions.Timeout:
        print("⏱️ Timeout ao conectar com o servidor")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def list_ollama_models(base_url: str) -> Optional[list]:
    """Listar modelos disponíveis no Ollama"""
    try:
        base_url = base_url.rstrip('/')
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"\n📋 Modelos disponíveis ({len(models)} encontrados):")
            
            if not models:
                print("   ⚠️ Nenhum modelo encontrado!")
                print("   💡 Para instalar um modelo, execute:")
                print("      ollama pull llama2")
                return []
            
            for i, model in enumerate(models, 1):
                name = model.get('name', 'N/A')
                size = model.get('size', 0)
                size_mb = round(size / (1024 * 1024), 1) if size else 0
                modified = model.get('modified_at', 'N/A')
                
                print(f"   {i}. 📦 {name}")
                print(f"      💾 Tamanho: {size_mb} MB")
                print(f"      🕒 Modificado: {modified[:19] if modified != 'N/A' else 'N/A'}")
                print()
            
            return [model.get('name') for model in models]
            
        else:
            print(f"❌ Erro ao listar modelos: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
        return None

def test_model_availability(base_url: str, model_name: str, available_models: list) -> bool:
    """Verificar se um modelo específico está disponível"""
    if not available_models:
        return False
    
    # Verificar se o modelo está na lista (com ou sem :latest)
    model_variants = [model_name, f"{model_name}:latest"]
    
    found_model = None
    for variant in model_variants:
        if variant in available_models:
            found_model = variant
            break
    
    if found_model:
        print(f"✅ Modelo '{model_name}' está disponível como '{found_model}'")
        return True
    else:
        print(f"❌ Modelo '{model_name}' não encontrado!")
        print(f"   💡 Para instalar, execute: ollama pull {model_name}")
        return False

def test_ollama_generation(base_url: str, model_name: str) -> bool:
    """Testar geração de texto com o modelo"""
    try:
        base_url = base_url.rstrip('/')
        
        print(f"\n🧪 Testando geração de texto com '{model_name}'...")
        
        payload = {
            "model": model_name,
            "prompt": "Olá! Responda apenas 'Ollama funcionando!' em português.",
            "stream": False
        }
        
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data.get('response', '').strip()
            
            print("✅ Geração de texto funcionando!")
            print(f"📝 Resposta: {generated_text}")
            
            # Verificar se a resposta parece válida
            if len(generated_text) > 0:
                print("✅ Modelo está respondendo corretamente!")
                return True
            else:
                print("⚠️ Modelo não gerou resposta válida")
                return False
                
        else:
            print(f"❌ Erro na geração: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data}")
            except:
                print(f"   Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Timeout durante geração (modelo pode estar carregando...)")
        return False
    except Exception as e:
        print(f"❌ Erro durante geração: {e}")
        return False

def test_ollama_provider_integration():
    """Testar integração com nosso provider personalizado"""
    try:
        print("\n🔌 Testando integração com nosso Provider...")
        
        from llm_providers.ollama_provider import OllamaProvider
        from config_multi_llm import OllamaConfig
        
        config = OllamaConfig.from_env()
        
        if not config:
            print("❌ Configuração Ollama não encontrada no .env")
            return False
        
        provider = OllamaProvider(config)
        
        # Testar se consegue inicializar
        if provider.is_available():
            print("✅ Provider Ollama inicializado com sucesso!")
            
            # Testar geração via provider
            try:
                result = provider.generate("Diga apenas 'Provider funcionando!'")
                print(f"📝 Resposta via provider: {result}")
                return True
            except Exception as e:
                print(f"⚠️ Provider criado mas erro na geração: {e}")
                return False
        else:
            print("❌ Provider Ollama não está disponível")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("   Verifique se os módulos estão no lugar correto")
        return False
    except Exception as e:
        print(f"❌ Erro no provider: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DO PROVEDOR OLLAMA")
    print("=" * 50)
    
    # Carregar configurações
    load_env()
    config = get_ollama_config()
    
    print(f"\n📋 Configuração atual:")
    print(f"   🌐 Base URL: {config['base_url']}")
    print(f"   🤖 Modelo LLM: {config['model']}")
    print(f"   📊 Modelo Embedding: {config['embedding_model']}")
    
    # Teste 1: Conectividade
    print(f"\n{'='*20} TESTE 1: CONECTIVIDADE {'='*20}")
    if not test_ollama_health(config['base_url']):
        print("\n❌ Servidor Ollama não está acessível!")
        print("\n🔧 Soluções possíveis:")
        print("   1. Verifique se o Ollama está instalado:")
        print("      https://ollama.ai")
        print("   2. Inicie o servidor:")
        print("      ollama serve")
        print("   3. Verifique a URL no .env:")
        print(f"      OLLAMA_BASE_URL={config['base_url']}")
        return False
    
    # Teste 2: Modelos disponíveis
    print(f"\n{'='*20} TESTE 2: MODELOS {'='*20}")
    available_models = list_ollama_models(config['base_url'])
    
    if available_models is None:
        print("❌ Não foi possível listar modelos")
        return False
    
    # Teste 3: Modelo configurado
    print(f"\n{'='*20} TESTE 3: MODELO CONFIGURADO {'='*20}")
    model_available = test_model_availability(
        config['base_url'], 
        config['model'], 
        available_models
    )
    
    # Teste 4: Geração de texto
    if model_available:
        print(f"\n{'='*20} TESTE 4: GERAÇÃO DE TEXTO {'='*20}")
        generation_ok = test_ollama_generation(config['base_url'], config['model'])
    else:
        print(f"\n{'='*20} TESTE 4: PULADO (modelo não disponível) {'='*20}")
        generation_ok = False
    
    # Teste 5: Integração com nosso provider
    print(f"\n{'='*20} TESTE 5: INTEGRAÇÃO PROVIDER {'='*20}")
    provider_ok = test_ollama_provider_integration()
    
    # Resumo final
    print(f"\n{'='*20} RESUMO FINAL {'='*20}")
    
    tests = [
        ("🌐 Conectividade", True),
        ("📋 Listagem de modelos", available_models is not None),
        ("🤖 Modelo configurado", model_available),
        ("🧪 Geração de texto", generation_ok),
        ("🔌 Provider integração", provider_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 OLLAMA ESTÁ TOTALMENTE FUNCIONAL!")
        print("\n✅ Você pode usar o provedor Ollama no sistema Multi-LLM")
        print("   Para usar como preferido, configure no .env:")
        print("   PREFERRED_LLM_PROVIDER=ollama")
    elif passed >= 3:
        print("⚠️ OLLAMA PARCIALMENTE FUNCIONAL")
        print("   Alguns testes falharam, mas o básico está funcionando")
    else:
        print("❌ OLLAMA NÃO ESTÁ FUNCIONAL")
        print("   Verifique a instalação e configuração")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
