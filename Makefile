.PHONY: help install install-dev test test-cov lint format type-check clean build run dev docker-build docker-run docker-dev docker-clean docs

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	uv sync

install-dev: ## Install development dependencies
	uv sync --dev

install-all: ## Install all dependencies including optional groups
	uv sync --all-extras

# Testing
test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

test-fast: ## Run tests in parallel
	uv run pytest tests/ -n auto

# Code Quality
lint: ## Run linting checks
	uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format: ## Format code with black and isort
	uv run black .
	uv run isort .

format-check: ## Check code formatting
	uv run black . --check
	uv run isort . --check-only

type-check: ## Run type checking
	uv run mypy .

# Security
security: ## Run security checks
	uv run bandit -r . -f json -o bandit-report.json
	uv run safety check

# Docker
docker-build: ## Build Docker image
	docker build -t db-adapter .

docker-run: ## Run Docker container
	docker run -p 8000:8000 db-adapter

docker-dev: ## Run development environment with Docker Compose
	docker-compose -f docker-compose.dev.yml up --build

docker-prod: ## Run production environment with Docker Compose
	docker-compose up --build

docker-clean: ## Clean up Docker containers and images
	docker-compose down -v
	docker system prune -f

# Development
dev: ## Run development server
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

run: ## Run production server
	uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Database
db-migrate: ## Run database migrations
	uv run alembic upgrade head

db-revision: ## Create new migration
	uv run alembic revision --autogenerate -m "$(message)"

# Documentation
docs: ## Build documentation
	uv run mkdocs build

docs-serve: ## Serve documentation locally
	uv run mkdocs serve

# Cleanup
clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .uv/

# Pre-commit
pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	uv run pre-commit run --all-files

# CI/CD
ci: format-check lint type-check test security ## Run all CI checks

# Performance
benchmark: ## Run performance benchmarks
	uv run pytest tests/ --benchmark-only

# Database setup
setup-db: ## Setup database with sample data
	uv run python scripts/setup_db.py

# Environment
env-example: ## Copy environment example
	cp env.example .env

# UV specific commands
uv-init: ## Initialize uv project
	uv init

uv-lock: ## Generate lock file
	uv lock

uv-sync: ## Sync dependencies
	uv sync

uv-add: ## Add a dependency
	uv add $(package)

uv-add-dev: ## Add a development dependency
	uv add --dev $(package)

uv-remove: ## Remove a dependency
	uv remove $(package)

uv-upgrade: ## Upgrade dependencies
	uv lock --upgrade

# All-in-one development setup
setup: env-example install-dev pre-commit-install ## Complete development setup 