# Usar imagem Python otimizada
FROM python:3.11-slim-bullseye

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONUTF8=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libblas-dev \
    liblapack-dev \
    gfortran \
    locales \
    && sed -i 's/# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar e instalar dependências primeiro (para cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte (como root primeiro)
COPY . .

# Copiar entrypoint e dar permissão de execução
RUN chmod +x /app/docker/docker_entrypoint.sh

# Ajustar ownership para appuser após preparar arquivos
RUN chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta (se necessário para APIs futuras)
EXPOSE 8000

ENTRYPOINT ["/app/docker/docker_entrypoint.sh"]
