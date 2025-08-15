#!/usr/bin/env python3
"""
Script de setup para ambiente de desenvolvimento
Suporta instalação local e Docker
"""
import subprocess
import sys
import shutil
import os


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
    """Verifica se Docker está disponível"""
    try:
        subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def setup_local():
    """Setup para desenvolvimento local"""
    print("🚀 Configurando ambiente LOCAL...")
    
    setup_commands = [
        (
            "pip install -r requirements-dev.txt",
            "Instalando dependências de desenvolvimento"
        ),
        (
            "python -m black .",
            "Formatando código com Black"
        ),
    ]
    
    for command, description in setup_commands:
        if not run_command(command, description):
            return False
    
    return True


def setup_docker():
    """Setup para desenvolvimento com Docker"""
    print("🐳 Configurando ambiente DOCKER...")
    
    # Copiar arquivo de exemplo se não existir
    if not os.path.exists(".env"):
        if os.path.exists(".env.docker"):
            shutil.copy(".env.docker", ".env")
            print("📋 Copiado .env.docker para .env")
        else:
            print("❌ Arquivo .env.docker não encontrado!")
            return False
    
    docker_commands = [
        (
            "docker-compose build",
            "Construindo imagens Docker"
        ),
        (
            "docker-compose up -d postgres mysql",
            "Iniciando bancos de dados"
        ),
    ]
    
    for command, description in docker_commands:
        if not run_command(command, description):
            return False
    
    return True


def main():
    """Configura ambiente de desenvolvimento"""
    print("🚀 Setup do Ambiente de Desenvolvimento DB RAG")
    print("=" * 50)
    
    # Verifica argumentos
    use_docker = "--docker" in sys.argv
    
    if not use_docker:
        print("📋 Escolha o tipo de ambiente:")
        print("1. Local (instala dependências localmente)")
        print("2. Docker (usa containers)")
        
        choice = input("\nEscolha (1 ou 2): ").strip()
        use_docker = choice == "2"
    
    success = False
    
    if use_docker:
        if not check_docker():
            print("❌ Docker não encontrado!")
            print("📋 Instale Docker Desktop")
            sys.exit(1)
        success = setup_docker()
    else:
        success = setup_local()
    
    if success:
        print("\n" + "="*50)
        print("🎉 Ambiente configurado com sucesso!")
        print("="*50)
        
        if use_docker:
            print("📋 Para usar Docker:")
            print("1. Edite .env com sua chave OpenAI")
            print("2. Execute: python docker/docker_helper.py up")
            print("3. Execute: python docker/docker_helper.py logs")
        else:
            print("📋 Para desenvolvimento local:")
            print("1. Copie .env.example para .env e configure")
            print("2. Execute: python check_quality.py")
            print("3. Execute: python examples.py")
    else:
        print("❌ Setup falhou!")
        sys.exit(1)


if __name__ == "__main__":
    main()
