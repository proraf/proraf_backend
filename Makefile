.PHONY: help install dev test lint format migrate docker-dev docker-prod clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instala dependências com Poetry"
	@echo "  make dev          - Inicia servidor de desenvolvimento"
	@echo "  make test         - Executa testes"
	@echo "  make lint         - Executa linter"
	@echo "  make format       - Formata código"
	@echo "  make migrate      - Aplica migrations"
	@echo "  make docker-dev   - Inicia com Docker (desenvolvimento)"
	@echo "  make docker-prod  - Inicia com Docker (produção)"
	@echo "  make clean        - Remove arquivos temporários"

install:
	poetry install

dev:
	poetry run task dev

test:
	poetry run task test

lint:
	poetry run task lint

format:
	poetry run task format

migrate:
	poetry run task migrate

makemigrations:
	@read -p "Nome da migration: " name; \
	poetry run task makemigrations "$$name"

docker-dev:
	docker-compose --profile development up --build

docker-prod:
	docker-compose --profile production up -d --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	rm -rf dist build