FROM python:3.11-slim as builder

WORKDIR /app

# Instala dependências de build para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN pip install poetry

# Copia arquivos de dependências
COPY pyproject.toml poetry.lock* ./

# Atualiza o lock file e instala dependências de produção
RUN poetry config virtualenvs.create false \
    && poetry lock \
    && poetry install --only=main --no-root


FROM python:3.11-slim

WORKDIR /app

# Instala libpq para psycopg2 em runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN useradd -m -u 1000 proraf && \
    chown -R proraf:proraf /app

# Copia dependências do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código da aplicação
COPY --chown=proraf:proraf . .

# Muda para usuário não-root
USER proraf

# Expõe porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando para produção
CMD ["uvicorn", "proraf.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]