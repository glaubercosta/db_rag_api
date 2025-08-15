#!/usr/bin/env python3
"""
Teste demonstrativo de como converter testes de print() para assertions
"""
import os
import tempfile
import sys
import json
from unittest.mock import Mock
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from vector_store_manager import VectorStoreManager, SecurityError
    from config import RAGConfig
    from langchain_openai import OpenAIEmbeddings
    from langchain_core.documents import Document
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("💡 Execute: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()


def test_with_prints_old_style():
    """EXEMPLO ANTIGO: Teste com prints (problemático)"""
    print("=== TESTE ANTIGO COM PRINTS ===")
    
    try:
        config = RAGConfig()
        print("✅ Configuração criada")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False
    
    try:
        manager = VectorStoreManager(config)
        print("✅ Manager criado")
    except Exception as e:
        print(f"❌ Erro no manager: {e}")
        return False
    
    print("🎯 Teste antigo 'passou' (mas sem verificações reais)")
    return True


def test_with_assertions_new_style():
    """EXEMPLO NOVO: Teste com assertions explícitas (determinístico)"""
    print("=== TESTE NOVO COM ASSERTIONS ===")
    
    # Test 1: Configuração deve ser criada
    config = RAGConfig()
    assert config is not None, "Configuração deve ser criada"
    assert hasattr(config, 'vector_store_path'), "Config deve ter vector_store_path"
    print("✅ Configuração validada com assertions")
    
    # Test 2: Manager deve ser inicializado
    manager = VectorStoreManager(config)
    assert manager is not None, "Manager deve ser criado"
    assert manager.config == config, "Manager deve ter config correto"
    print("✅ Manager validado com assertions")
    
    # Test 3: Método de checksum deve funcionar
    test_file = "temp_test_file.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("test content")
        
        checksum = manager._calculate_file_checksum(test_file)
        assert isinstance(checksum, str), "Checksum deve ser string"
        assert len(checksum) > 0, "Checksum deve ter conteúdo"
        print("✅ Checksum validado com assertions")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
    
    # Test 4: Tratamento de erro deve funcionar
    try:
        manager._calculate_file_checksum("arquivo_inexistente.txt")
        assert False, "Deveria ter lançado exceção para arquivo inexistente"
    except FileNotFoundError:
        print("✅ Tratamento de erro validado com assertions")
    
    print("🎯 Teste novo PASSOU com verificações reais!")
    return True


def test_security_validations_deterministic():
    """Teste determinístico de validações de segurança"""
    print("=== TESTE DE SEGURANÇA DETERMINÍSTICO ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = RAGConfig()
        manager = VectorStoreManager(config)
        
        # Test: Diretório vazio não deve ser válido
        empty_dir = os.path.join(temp_dir, "empty")
        os.makedirs(empty_dir)
        
        try:
            mock_embeddings = Mock()
            manager.load_vector_store(empty_dir, mock_embeddings)
            assert False, "Diretório vazio deveria falhar"
        except (SecurityError, FileNotFoundError) as e:
            assert "Missing required files" in str(e) or "No such file" in str(e)
            print("✅ Diretório vazio corretamente rejeitado")
        
        # Test: Arquivo de metadados deve ser validado
        fake_store_dir = os.path.join(temp_dir, "fake_store")
        os.makedirs(fake_store_dir)
        
        # Criar arquivos necessários mas com metadados inválidos
        fake_files = ["index.faiss", "index.pkl"]
        for file_name in fake_files:
            fake_file = os.path.join(fake_store_dir, file_name)
            with open(fake_file, 'w') as f:
                f.write("fake content")
        
        # Metadados inválidos
        metadata_file = os.path.join(fake_store_dir, "metadata.json")
        with open(metadata_file, 'w') as f:
            f.write("invalid json content")
        
        try:
            mock_embeddings = Mock()
            manager.load_vector_store(fake_store_dir, mock_embeddings)
            assert False, "Metadados inválidos deveriam falhar"
        except (json.JSONDecodeError, SecurityError):
            print("✅ Metadados inválidos corretamente rejeitados")
    
    print("🎯 Validações de segurança PASSARAM!")
    return True


def run_comparison_tests():
    """Executa comparação entre testes antigos e novos"""
    print("🔄 COMPARANDO ESTILOS DE TESTE\n")
    
    # Executar teste antigo
    old_result = test_with_prints_old_style()
    print(f"Resultado teste antigo: {'PASSOU' if old_result else 'FALHOU'}")
    print("❌ Problema: Não sabemos SE REALMENTE funcionou\n")
    
    # Executar teste novo
    try:
        new_result = test_with_assertions_new_style()
        print(f"Resultado teste novo: {'PASSOU' if new_result else 'FALHOU'}")
        print("✅ Benefício: Sabemos EXATAMENTE o que foi validado\n")
    except AssertionError as e:
        print(f"❌ Teste novo FALHOU: {e}")
        print("✅ Benefício: Sabemos EXATAMENTE onde falhou\n")
    
    # Executar teste de segurança
    try:
        security_result = test_security_validations_deterministic()
        print(f"Resultado segurança: {'PASSOU' if security_result else 'FALHOU'}")
        print("✅ Benefício: Validações específicas e determinísticas\n")
    except Exception as e:
        print(f"❌ Teste segurança FALHOU: {e}")
        print("✅ Benefício: Erro específico identificado\n")


def show_refactoring_benefits():
    """Mostra benefícios da refatoração"""
    print("=" * 60)
    print("🎯 BENEFÍCIOS DA REFATORAÇÃO DE TESTES")
    print("=" * 60)
    
    benefits = [
        ("❌ ANTES", "✅ DEPOIS"),
        ("print() para mostrar resultados", "assert para validar condições"),
        ("Sucesso silencioso", "Falha explícita com mensagens"),
        ("Testes 'passam' sem validar", "Testes verificam comportamento real"),
        ("Debugging difícil", "Debugging preciso"),
        ("Não integra com CI/CD", "Integração perfeita com pytest"),
        ("Resultados ambíguos", "Resultados determinísticos"),
        ("Difícil automatizar", "Automação nativa"),
    ]
    
    for before, after in benefits:
        print(f"{before:<35} → {after}")
    
    print("\n📊 MÉTRICAS DE MELHORIA:")
    print("• Determinismo: 0% → 100%")
    print("• Detecção de falhas: Baixa → Alta") 
    print("• Facilidade de debugging: Baixa → Alta")
    print("• Automação: Impossível → Nativa")
    print("• Integração CI/CD: Não → Sim")


if __name__ == "__main__":
    try:
        run_comparison_tests()
        show_refactoring_benefits()
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO COMPLETA!")
        print("💡 Próximos passos:")
        print("   1. Refatorar test_vector_security.py")
        print("   2. Refatorar test_sql_injection.py") 
        print("   3. Refatorar outros testes com print()")
        print("   4. Configurar pytest como runner padrão")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro na execução: {e}")
        print("💡 Verifique se todas as dependências estão instaladas")
        sys.exit(1)
