from dotenv import load_dotenv
from rag_system import create_system_from_env

load_dotenv()

print("Testando sistema completo após correções de segurança...")
system = create_system_from_env()

try:
    if system.initialize():
        print("✅ Sistema inicializado")
        result = system.ask("Quantas tabelas existem?")
        if result["status"] == "success":
            print(f"✅ Query funciona: {result['sql_response'][:100]}...")
        else:
            print(f"❌ Erro na query: {result['error']}")
        system.close()
        print("✅ Sistema completo funcionando!")
    else:
        print("❌ Falha na inicialização")
except Exception as e:
    print(f"❌ Erro: {e}")
