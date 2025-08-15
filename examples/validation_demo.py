#!/usr/bin/env python3
"""
Demonstração das validações da RAGConfig
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import RAGConfig

def demonstrate_validations():
    """Demonstra as validações implementadas na RAGConfig"""
    
    print("=== DEMONSTRAÇÃO DAS VALIDAÇÕES RAGConfig ===\n")
    
    print("1. Configuração padrão (válida):")
    try:
        config = RAGConfig()
        print(f"   ✅ similarity_search_k: {config.similarity_search_k}")
        print(f"   ✅ table_sample_limit: {config.table_sample_limit}")
        print(f"   ✅ vector_store_path: {config.vector_store_path}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n2. Configuração personalizada válida:")
    try:
        config = RAGConfig(
            similarity_search_k=15,
            table_sample_limit=2500,
            vector_store_path="./data/embeddings"
        )
        print(f"   ✅ similarity_search_k: {config.similarity_search_k}")
        print(f"   ✅ table_sample_limit: {config.table_sample_limit}")
        print(f"   ✅ vector_store_path: {config.vector_store_path}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n3. VALIDAÇÕES DE ERRO:")
    
    # similarity_search_k inválidos
    invalid_k_values = [
        (-1, "valor negativo"),
        (0, "valor zero"),
        (101, "valor muito alto (> 100)"),
        ("5", "tipo string em vez de int"),
        (5.5, "tipo float em vez de int")
    ]
    
    print("\n   3.1 similarity_search_k inválidos:")
    for value, description in invalid_k_values:
        try:
            RAGConfig(similarity_search_k=value)
            print(f"      ❌ FALHOU: {description} deveria gerar erro")
        except (ValueError, TypeError) as e:
            print(f"      ✅ {description}: {e}")
    
    # table_sample_limit inválidos
    invalid_limit_values = [
        (-100, "valor negativo"),
        (0, "valor zero"),
        (15000, "valor muito alto (> 10000)"),
        ("1000", "tipo string em vez de int"),
        (1000.0, "tipo float em vez de int")
    ]
    
    print("\n   3.2 table_sample_limit inválidos:")
    for value, description in invalid_limit_values:
        try:
            RAGConfig(table_sample_limit=value)
            print(f"      ❌ FALHOU: {description} deveria gerar erro")
        except (ValueError, TypeError) as e:
            print(f"      ✅ {description}: {e}")
    
    # vector_store_path inválidos
    invalid_path_values = [
        ("", "string vazia"),
        ("   ", "string só com espaços"),
        (123, "tipo int em vez de string"),
        ([], "tipo list em vez de string")
    ]
    
    print("\n   3.3 vector_store_path inválidos:")
    for value, description in invalid_path_values:
        try:
            RAGConfig(vector_store_path=value)
            print(f"      ❌ FALHOU: {description} deveria gerar erro")
        except (ValueError, TypeError) as e:
            print(f"      ✅ {description}: {e}")
    
    print("\n4. VALORES LIMÍTROFES VÁLIDOS:")
    
    # Testando valores nos limites
    boundary_configs = [
        (1, 1, "valores mínimos"),
        (100, 10000, "valores máximos"),
        (50, 5000, "valores médios")
    ]
    
    for k, limit, description in boundary_configs:
        try:
            config = RAGConfig(similarity_search_k=k, table_sample_limit=limit)
            print(f"   ✅ {description}: k={k}, limit={limit}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")
    
    print("\n=== RESUMO ===")
    print("✅ Implementadas validações para:")
    print("   - similarity_search_k: deve ser int positivo ≤ 100")
    print("   - table_sample_limit: deve ser int positivo ≤ 10000")
    print("   - vector_store_path: deve ser string não-vazia ou None")
    print("✅ Validações aplicadas tanto no __post_init__ quanto no from_env()")
    print("✅ Mensagens de erro claras e específicas")

if __name__ == "__main__":
    demonstrate_validations()
