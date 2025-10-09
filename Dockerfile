FROM python:3.11-slim as builder

WORKDIR /app

# Instala Poetry
RUN pip install poetry

# Copia arquivos de dependências
COPY pyproject.toml ./

# Instala apenas dependências de produção
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root


FROM python:3.11-slim

WORKDIR /app

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