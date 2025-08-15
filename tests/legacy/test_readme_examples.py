#!/usr/bin/env python3
"""
Teste para verificar se os exemplos do README funcionam corretamente
"""

print("=== TESTANDO EXEMPLOS DO README ===\n")

# 1. Teste de configuração válida
print("1. Testando configuração válida do README:")
try:
    from config import RAGConfig
    
    # Default values (all valid)
    config = RAGConfig()
    print(f"   ✅ Default config: k={config.similarity_search_k}, limit={config.table_sample_limit}")
    
    # Custom valid values
    config = RAGConfig(
        similarity_search_k=10,
        table_sample_limit=2500,
        vector_store_path="./my_vectors"
    )
    print(f"   ✅ Custom config: k={config.similarity_search_k}, limit={config.table_sample_limit}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. Teste de configurações inválidas
print("\n2. Testando configurações inválidas do README:")

invalid_configs = [
    ("similarity_search_k=-1", {"similarity_search_k": -1}),
    ("similarity_search_k=101", {"similarity_search_k": 101}),
    ("table_sample_limit=0", {"table_sample_limit": 0}),
    ("table_sample_limit=20000", {"table_sample_limit": 20000}),
    ("vector_store_path=''", {"vector_store_path": ""}),
    ("similarity_search_k='5'", {"similarity_search_k": "5"}),
]

for description, kwargs in invalid_configs:
    try:
        RAGConfig(**kwargs)
        print(f"   ❌ FALHOU: {description} deveria gerar erro")
    except (ValueError, TypeError) as e:
        print(f"   ✅ {description}: {type(e).__name__}")

# 3. Teste de validação com try/catch como no README
print("\n3. Testando padrão try/catch do README:")
try:
    rag_config = RAGConfig(
        similarity_search_k=10,      # Valid: 1-100
        table_sample_limit=2500,     # Valid: 1-10000
        vector_store_path="./my_vectors"
    )
    print("   ✅ Configuração válida criada com sucesso")
except (ValueError, TypeError) as e:
    print(f"   ❌ Configuration error: {e}")

print("\n🎯 Todos os exemplos do README testados!")
