#!/usr/bin/env python3
"""
🚀 TESTE RÁPIDO OLLAMA
====================

Script simples para verificar rapidamente se Ollama está ativo.
Execute: python quick_ollama_test.py
"""

import os
import requests
from dotenv import load_dotenv

def main():
    print("🚀 TESTE RÁPIDO OLLAMA")
    print("=" * 30)
    
    # Carregar .env
    load_dotenv()
    
    # Obter configuração
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    model = os.getenv('OLLAMA_MODEL', 'llama2')
    
    print(f"🌐 Servidor: {base_url}")
    print(f"🤖 Modelo: {model}")
    
    try:
        # Teste de conectividade
        base_url = base_url.rstrip('/')
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            
            print("✅ Ollama está ATIVO!")
            print(f"📦 Modelos disponíveis: {len(models)}")
            
            if model in models or f"{model}:latest" in models:
                print(f"✅ Modelo '{model}' está disponível!")
                
                # Teste rápido de geração
                try:
                    gen_response = requests.post(
                        f"{base_url}/api/generate",
                        json={"model": model, "prompt": "Hi", "stream": False},
                        timeout=10
                    )
                    
                    if gen_response.status_code == 200:
                        print("✅ Geração funcionando!")
                        return True
                    else:
                        print("⚠️ Conectado, mas erro na geração")
                        return False
                        
                except requests.exceptions.Timeout:
                    print("⚠️ Conectado, mas timeout na geração")
                    return False
            else:
                print(f"❌ Modelo '{model}' não encontrado!")
                print(f"   Disponíveis: {models}")
                return False
        else:
            print(f"❌ Servidor respondeu com código {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar!")
        print(f"   Verifique: {base_url}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    if main():
        print("\n🎉 OLLAMA FUNCIONANDO!")
        exit(0)
    else:
        print("\n❌ OLLAMA COM PROBLEMAS!")
        exit(1)
