#!/usr/bin/env python3
"""
Teste simples das validações da RAGConfig
"""
from config import RAGConfig

print("Testing RAGConfig validations...")

# Test 1: Default config should work
try:
    config = RAGConfig()
    print("✅ Default config works")
except Exception as e:
    print(f"❌ Default config failed: {e}")

# Test 2: Negative similarity_search_k should fail
try:
    RAGConfig(similarity_search_k=-1)
    print("❌ Negative similarity_search_k should have failed")
except ValueError as e:
    print(f"✅ Caught negative similarity_search_k: {e}")

# Test 3: Zero table_sample_limit should fail
try:
    RAGConfig(table_sample_limit=0)
    print("❌ Zero table_sample_limit should have failed")
except ValueError as e:
    print(f"✅ Caught zero table_sample_limit: {e}")

# Test 4: Empty vector_store_path should fail
try:
    RAGConfig(vector_store_path="")
    print("❌ Empty vector_store_path should have failed")
except ValueError as e:
    print(f"✅ Caught empty vector_store_path: {e}")

# Test 5: Too large similarity_search_k should fail
try:
    RAGConfig(similarity_search_k=101)
    print("❌ Large similarity_search_k should have failed")
except ValueError as e:
    print(f"✅ Caught large similarity_search_k: {e}")

# Test 6: Valid custom config should work
try:
    config = RAGConfig(
        similarity_search_k=10,
        table_sample_limit=500,
        vector_store_path="./test_path"
    )
    print("✅ Valid custom config works")
except Exception as e:
    print(f"❌ Valid custom config failed: {e}")

print("\n🎯 All validation tests completed!")
