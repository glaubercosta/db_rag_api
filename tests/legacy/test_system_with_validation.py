from config import DatabaseConfig, OpenAIConfig, RAGConfig

print("Testando sistema com validações...")
try:
    # Carregar configurações (com validações)
    db_config = DatabaseConfig.from_env()
    openai_config = OpenAIConfig.from_env()
    rag_config = RAGConfig.from_env()  # Aqui as validações são aplicadas!
    
    print("✅ Configurações carregadas e validadas com sucesso!")
    print(f"Config válida: k={rag_config.similarity_search_k}, limit={rag_config.table_sample_limit}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
