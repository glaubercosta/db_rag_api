#!/usr/bin/env python3
"""
Teste da otimização para evitar duplicação de recuperação de documentos
"""
from unittest.mock import Mock, patch
from dotenv import load_dotenv

load_dotenv()

from config import DatabaseConfig, OpenAIConfig
from database_scanner import DatabaseScanner
from vector_store_manager import VectorStoreManager
from sql_agent import SQLAgent, RAGQueryProcessor


def test_no_duplicate_retrieval():
    """Testa que a recuperação de documentos não é duplicada"""
    print("=== TESTE DE OTIMIZAÇÃO - SEM DUPLICAÇÃO ===\n")
    
    # Criar mocks para evitar dependências externas
    mock_config = Mock()
    mock_scanner = Mock()
    mock_vector_manager = Mock()
    mock_sql_agent = Mock()
    
    # Simular documentos recuperados
    mock_doc1 = Mock()
    mock_doc1.page_content = "Schema info: users table with id, name, email"
    mock_doc1.metadata = {"type": "schema", "table": "users"}
    
    mock_doc2 = Mock()
    mock_doc2.page_content = "Sample data: John, jane@email.com"
    mock_doc2.metadata = {"type": "sample", "table": "users"}
    
    mock_docs = [mock_doc1, mock_doc2]
    
    # Configurar mock do vector store manager
    mock_vector_manager.search_similar.return_value = mock_docs
    
    # Configurar mock do SQL agent
    mock_sql_agent.query_with_rag.return_value = "There are 3 users in the table"
    
    # Criar o processor
    processor = RAGQueryProcessor(
        scanner=mock_scanner,
        vector_store_manager=mock_vector_manager,
        sql_agent=mock_sql_agent
    )
    
    # Executar uma query
    question = "How many users are there?"
    result = processor.process_question(question)
    
    # Verificar que search_similar foi chamado apenas UMA vez
    print("1. Verificando número de chamadas ao search_similar:")
    call_count = mock_vector_manager.search_similar.call_count
    if call_count == 1:
        print(f"   ✅ search_similar chamado {call_count} vez (otimizado!)")
    else:
        print(f"   ❌ search_similar chamado {call_count} vezes (duplicação!)")
    
    # Verificar que o SQL agent foi chamado com pre_retrieved_docs
    print("\n2. Verificando chamada do SQL agent:")
    sql_agent_calls = mock_sql_agent.query_with_rag.call_args_list
    if len(sql_agent_calls) == 1:
        call_args = sql_agent_calls[0]
        # Verificar se foi chamado com pre_retrieved_docs
        if 'pre_retrieved_docs' in call_args.kwargs:
            print("   ✅ SQL agent chamado com pre_retrieved_docs (sem duplicação)")
            passed_docs = call_args.kwargs['pre_retrieved_docs']
            print(f"   ✅ Documentos passados: {len(passed_docs)} docs")
        else:
            print("   ❌ SQL agent não recebeu pre_retrieved_docs")
    else:
        print(f"   ❌ SQL agent chamado {len(sql_agent_calls)} vezes")
    
    # Verificar estrutura do resultado
    print("\n3. Verificando resultado:")
    if result["status"] == "success":
        print("   ✅ Processamento bem-sucedido")
        print(f"   ✅ Pergunta: {result['question']}")
        print(f"   ✅ Resposta: {result['sql_response']}")
        print(f"   ✅ Contexto: {len(result['relevant_context'])} documentos")
    else:
        print(f"   ❌ Erro no processamento: {result.get('error', 'Unknown')}")
    
    print(f"\n🎯 Teste de otimização concluído!")
    return call_count == 1


def test_real_system_performance():
    """Teste com sistema real para medir performance"""
    print("\n=== TESTE DE PERFORMANCE REAL ===\n")
    
    try:
        from rag_system import create_system_from_env
        
        print("Inicializando sistema...")
        system = create_system_from_env()
        
        if not system.initialize():
            print("❌ Falha na inicialização")
            return
        
        print("✅ Sistema inicializado")
        
        # Patch para contar chamadas do search_similar
        original_search = system.query_processor.vector_store_manager.search_similar
        call_counter = {"count": 0}
        
        def counting_search(*args, **kwargs):
            call_counter["count"] += 1
            print(f"   📊 search_similar chamada #{call_counter['count']}")
            return original_search(*args, **kwargs)
        
        # Aplicar o patch
        system.query_processor.vector_store_manager.search_similar = counting_search
        
        # Fazer uma pergunta
        print("\n Executando query: 'Quantas tabelas existem?'")
        result = system.ask("Quantas tabelas existem?")
        
        print(f"\n📈 Resultado do teste:")
        print(f"   - Chamadas ao search_similar: {call_counter['count']}")
        if call_counter['count'] == 1:
            print("   ✅ Otimização funcionando! (1 chamada apenas)")
        else:
            print(f"   ⚠️  Possível duplicação ({call_counter['count']} chamadas)")
        
        if result["status"] == "success":
            print(f"   ✅ Query funcionou: {result['sql_response'][:50]}...")
        else:
            print(f"   ❌ Erro na query: {result['error']}")
        
        system.close()
        
    except Exception as e:
        print(f"❌ Erro no teste real: {e}")


if __name__ == "__main__":
    # Teste com mocks
    test_no_duplicate_retrieval()
    
    # Teste com sistema real
    test_real_system_performance()
