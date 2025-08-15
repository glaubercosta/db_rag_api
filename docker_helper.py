#!/usr/bin/env python3
"""
Script para facilitar uso do Docker no projeto
"""
import subprocess
import sys
import os
import shutil


def run_command(command, description):
    """Executa comando e mostra resultado"""
    print(f"🔧 {description}...")
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f"❌ Falhou: {description}")
        return False
    else:
        print(f"✅ Sucesso: {description}")
        return True


def check_docker():
    """Verifica se Docker está instalado e rodando"""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def setup_env_file():
    """Configura arquivo .env para Docker"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.docker"):
            print("📋 Copiando .env.docker para .env...")
            shutil.copy(".env.docker", ".env")
            print("⚠️  IMPORTANTE: Edite o arquivo .env com sua chave OpenAI!")
        else:
            print("❌ Arquivo .env.docker não encontrado!")
            return False
    else:
        print("✅ Arquivo .env já existe")
    return True


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("""
🐳 Docker Helper para DB RAG

Uso: python docker_helper.py <comando>

Comandos:
  setup     - Configura ambiente Docker
  build     - Constrói as imagens Docker
  up        - Inicia todos os serviços
  down      - Para todos os serviços
  logs      - Mostra logs dos serviços
  test      - Executa testes no container
  shell     - Abre shell no container da aplicação
  clean     - Remove containers e volumes
  
Exemplos:
  python docker_helper.py setup
  python docker_helper.py up
  python docker_helper.py logs
        """)
        return

    command = sys.argv[1]
    
    # Verifica Docker
    if not check_docker():
        print("❌ Docker ou docker-compose não encontrado!")
        print("📋 Instale Docker Desktop: https://www.docker.com/products/docker-desktop")
        return

    if command == "setup":
        print("🚀 Configurando ambiente Docker...")
        if setup_env_file():
            print("\n✅ Setup concluído!")
            print("📋 Próximos passos:")
            print("1. Edite .env com sua chave OpenAI")
            print("2. Execute: python docker_helper.py up")
    
    elif command == "build":
        run_command("docker-compose build", "Construindo imagens Docker")
    
    elif command == "up":
        if not os.path.exists(".env"):
            print("❌ Arquivo .env não encontrado! Execute 'setup' primeiro.")
            return
        run_command("docker-compose up -d", "Iniciando serviços")
        print("\n🌐 Serviços disponíveis:")
        print("- Aplicação: Container db_rag_app")
        print("- PostgreSQL: localhost:5432")
        print("- MySQL: localhost:3307") 
        print("- Adminer: http://localhost:8081")
    
    elif command == "down":
        run_command("docker-compose down", "Parando serviços")
    
    elif command == "logs":
        service = sys.argv[2] if len(sys.argv) > 2 else ""
        cmd = f"docker-compose logs -f {service}"
        run_command(cmd, f"Mostrando logs {service or 'de todos os serviços'}")
    
    elif command == "test":
        run_command("docker-compose exec db_rag python -m pytest", "Executando testes")
    
    elif command == "shell":
        print("🐚 Abrindo shell no container...")
        subprocess.run(["docker-compose", "exec", "db_rag", "/bin/bash"])
    
    elif command == "clean":
        print("🧹 Limpando containers e volumes...")
        run_command("docker-compose down -v", "Parando e removendo volumes")
        run_command("docker system prune -f", "Limpando sistema Docker")
    
    else:
        print(f"❌ Comando desconhecido: {command}")


if __name__ == "__main__":
    main()
