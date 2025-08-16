#!/usr/bin/env python3
"""
Script para forçar a recriação do vector store
"""
import os
import sys
import shutil

# Add src to path - ajustado para nova estrutura
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from multi_llm_rag_system import create_multi_llm_rag_system_from_env

def force_rebuild_vector_store():
    """Força a recriação do vector store"""
    print("🔄 FORÇANDO RECRIAÇÃO DO VECTOR STORE")
    print("=" * 50)
    
    # Verificar se existe vector store antigo
    vector_store_path = "./vector_store"
    if os.path.exists(vector_store_path):
        print(f"📁 Vector store encontrado em: {vector_store_path}")
        print("🗑️ Removendo vector store antigo...")
        try:
            shutil.rmtree(vector_store_path)
            print("✅ Vector store antigo removido com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao remover vector store antigo: {e}")
            return False
    else:
        print("📭 Nenhum vector store antigo encontrado")
    
    # Criar sistema RAG e forçar rebuild
    print("\n🚀 Criando sistema RAG com rebuild forçado...")
    try:
        rag_system = create_multi_llm_rag_system_from_env()
        
        # Inicializar com force_rebuild=True
        success = rag_system.initialize(force_rebuild=True)
        
        if success:
            print("\n✅ SUCESSO: Vector store recriado com segurança!")
            print("📊 Sistema Multi-LLM RAG inicializado corretamente")
            return True
        else:
            print("\n❌ FALHA: Não foi possível recriar o vector store")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🛡️ FERRAMENTA DE RECRIAÇÃO SEGURA DO VECTOR STORE")
    print("=" * 60)
    print("Esta ferramenta remove o vector store existente e cria um novo")
    print("para evitar avisos de segurança sobre desserialização perigosa.")
    print("=" * 60)
    
    force_rebuild_vector_store()
    
    print("\n" + "=" * 60)
    print("🏁 PROCESSO CONCLUÍDO")
    print("Agora você pode executar 'python multi_llm_api.py' com segurança!")
