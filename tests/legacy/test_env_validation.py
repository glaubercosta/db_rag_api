#!/usr/bin/env python3
"""
Teste das validações do from_env da RAGConfig
"""
import os
from config import RAGConfig

print("Testing RAGConfig.from_env() validations...")

# Backup original environment
original_env = {
    "SIMILARITY_SEARCH_K": os.getenv("SIMILARITY_SEARCH_K"),
    "TABLE_SAMPLE_LIMIT": os.getenv("TABLE_SAMPLE_LIMIT"),
    "VECTOR_STORE_PATH": os.getenv("VECTOR_STORE_PATH")
}

# Test 1: Valid environment values
try:
    os.environ["SIMILARITY_SEARCH_K"] = "10"
    os.environ["TABLE_SAMPLE_LIMIT"] = "2000"
    os.environ["VECTOR_STORE_PATH"] = "./test_path"
    
    config = RAGConfig.from_env()
    print(f"✅ Valid env config: k={config.similarity_search_k}, limit={config.table_sample_limit}")
except Exception as e:
    print(f"❌ Valid env config failed: {e}")

# Test 2: Invalid SIMILARITY_SEARCH_K
try:
    os.environ["SIMILARITY_SEARCH_K"] = "not_a_number"
    RAGConfig.from_env()
    print("❌ Invalid SIMILARITY_SEARCH_K should have failed")
except ValueError as e:
    print(f"✅ Caught invalid SIMILARITY_SEARCH_K: {e}")

# Test 3: Invalid TABLE_SAMPLE_LIMIT
try:
    os.environ["SIMILARITY_SEARCH_K"] = "5"
    os.environ["TABLE_SAMPLE_LIMIT"] = "not_a_number"
    RAGConfig.from_env()
    print("❌ Invalid TABLE_SAMPLE_LIMIT should have failed")
except ValueError as e:
    print(f"✅ Caught invalid TABLE_SAMPLE_LIMIT: {e}")

# Test 4: Negative value from environment
try:
    os.environ["SIMILARITY_SEARCH_K"] = "-5"
    os.environ["TABLE_SAMPLE_LIMIT"] = "1000"
    RAGConfig.from_env()
    print("❌ Negative similarity_search_k should have failed")
except ValueError as e:
    print(f"✅ Caught negative similarity_search_k from env: {e}")

# Test 5: Too large value from environment
try:
    os.environ["SIMILARITY_SEARCH_K"] = "5"
    os.environ["TABLE_SAMPLE_LIMIT"] = "20000"
    RAGConfig.from_env()
    print("❌ Large table_sample_limit should have failed")
except ValueError as e:
    print(f"✅ Caught large table_sample_limit from env: {e}")

# Restore original environment
for key, value in original_env.items():
    if value is not None:
        os.environ[key] = value
    elif key in os.environ:
        del os.environ[key]

print("\n🎯 All from_env validation tests completed!")
