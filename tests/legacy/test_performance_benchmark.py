#!/usr/bin/env python3
"""
Benchmark da otimização: comparar performance antes vs depois
"""
import time
from unittest.mock import Mock
from dotenv import load_dotenv
from sql_agent import RAGQueryProcessor

load_dotenv()


def simulate_old_behavior():
    """Simula o comportamento antigo (com duplicação)"""
    print("=== SIMULAÇÃO: COMPORTAMENTO ANTIGO (COM DUPLICAÇÃO) ===")
    
    # Mock que conta quantas vezes search_similar é chamado
    mock_vector_manager = Mock()
    
    # Simular delay na busca de documentos (como se fosse caro)
    def slow_search_similar(*args, **kwargs):
        time.sleep(0.1)  # 100ms delay para simular busca cara
        mock_doc = Mock()
        mock_doc.page_content = "Schema info"
        mock_doc.metadata = {"type": "schema"}
        return [mock_doc]
    
    mock_vector_manager.search_similar = slow_search_similar
    
    # Simular o comportamento antigo: duas chamadas separadas
    start_time = time.time()
    
    # 1ª chamada: em process_question
    mock_vector_manager.search_similar("test question")
    
    # 2ª chamada: em query_with_rag (simulando comportamento antigo)
    mock_vector_manager.search_similar("test question")
    
    # Simular processamento
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   📊 Tempo total: {duration:.3f}s")
    print("   📊 Chamadas ao search_similar: 2 (duplicadas)")
    print(f"   📊 Overhead da duplicação: ~{duration - 0.1:.3f}s")
    
    return duration


def test_optimized_behavior():
    """Testa o comportamento otimizado (sem duplicação)"""
    print("\n=== TESTE: COMPORTAMENTO OTIMIZADO (SEM DUPLICAÇÃO) ===")
    
    # Mock que conta quantas vezes search_similar é chamado
    mock_vector_manager = Mock()
    mock_sql_agent = Mock()
    mock_scanner = Mock()
    
    # Simular delay na busca de documentos
    def slow_search_similar(*args, **kwargs):
        time.sleep(0.1)  # 100ms delay
        mock_doc = Mock()
        mock_doc.page_content = "Schema info"
        mock_doc.metadata = {"type": "schema"}
        return [mock_doc]
    
    mock_vector_manager.search_similar.side_effect = slow_search_similar
    mock_sql_agent.query_with_rag.return_value = "Query result"
    
    # Usar a versão otimizada
    processor = RAGQueryProcessor(
        scanner=mock_scanner,
        vector_store_manager=mock_vector_manager,
        sql_agent=mock_sql_agent
    )
    
    start_time = time.time()
    
    # Uma única chamada otimizada
    result = processor.process_question("test question")
    
    end_time = time.time()
    duration = end_time - start_time
    
    call_count = mock_vector_manager.search_similar.call_count
    
    print(f"   📊 Tempo total: {duration:.3f}s")
    print(f"   📊 Chamadas ao search_similar: {call_count}")
    print(f"   📊 Status: {result['status']}")
    
    return duration, call_count


def performance_comparison():
    """Compara a performance antes vs depois"""
    print("=== COMPARAÇÃO DE PERFORMANCE ===\n")
    
    # Teste com simulação do comportamento antigo
    old_duration = simulate_old_behavior()
    
    # Teste com comportamento otimizado
    new_duration, call_count = test_optimized_behavior()
    
    # Cálculo da melhoria
    improvement = ((old_duration - new_duration) / old_duration) * 100
    
    print("\n📈 RESULTADOS DA OTIMIZAÇÃO:")
    print(f"   ⏱️  Antes (duplicado): {old_duration:.3f}s")
    print(f"   ⏱️  Depois (otimizado): {new_duration:.3f}s")
    print(f"   🚀 Melhoria: {improvement:.1f}%")
    print(f"   📉 Chamadas reduzidas: 2 → {call_count}")
    
    if call_count == 1 and improvement > 0:
        print("   ✅ OTIMIZAÇÃO CONFIRMADA!")
    else:
        print("   ❌ Algo pode estar errado na otimização")
    
    # Estimativa de economia em cenários reais
    print("\n💡 ESTIMATIVA DE ECONOMIA:")
    print(f"   - 100 queries/hora: {(old_duration - new_duration) * 100:.1f}s economizados")
    print(f"   - 1000 queries/dia: {(old_duration - new_duration) * 1000:.1f}s economizados")
    print(f"   - Em sistema com embedding lento (500ms): {improvement * 5:.0f}s economizados por query")


def test_with_different_k_values():
    """Testa com diferentes valores de k para recuperação"""
    print("\n=== TESTE COM DIFERENTES VALORES DE K ===")
    
    k_values = [3, 5, 10, 20]
    
    for k in k_values:
        mock_vector_manager = Mock()
        mock_sql_agent = Mock()
        mock_scanner = Mock()
        
        # Mock que simula diferentes custos baseados em k
        def variable_cost_search(*args, **kwargs):
            cost = k * 0.02  # Simula custo proporcional ao k
            time.sleep(cost)
            return [Mock() for _ in range(k)]
        
        mock_vector_manager.search_similar.side_effect = variable_cost_search
        mock_sql_agent.query_with_rag.return_value = "Result"
        
        processor = RAGQueryProcessor(
            scanner=mock_scanner,
            vector_store_manager=mock_vector_manager,
            sql_agent=mock_sql_agent
        )
        
        start_time = time.time()
        processor.process_question("test question")
        duration = time.time() - start_time
        
        call_count = mock_vector_manager.search_similar.call_count
        
        print(f"   k={k:2d}: {duration:.3f}s, {call_count} chamada(s)")


if __name__ == "__main__":
    performance_comparison()
    test_with_different_k_values()
