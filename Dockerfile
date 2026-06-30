FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para compilar pacotes (como asyncpg)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Instala o uv para um gerenciamento de pacotes mais rápido
RUN pip install uv

# Copia os arquivos de manifesto e o README (o * no final evita erro caso o README não exista)
COPY pyproject.toml uv.lock* README.md* ./

# Instala as dependências diretamente no sistema do container usando o uv
# O argumento --system garante que os pacotes fiquem disponíveis globalmente no container
RUN uv pip install --system -r pyproject.toml

# Adiciona o minio explicitamente caso ele ainda não esteja no pyproject.toml
RUN uv pip install --system minio

# Copia o código-fonte da aplicação
COPY ./app ./app

#Copia seed.py
COPY ./seed.py ./seed.py
# Expõe a porta e inicia o servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]