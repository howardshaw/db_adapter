# DB Adapter

A flexible database adapter with async/sync support built with FastAPI, SQLAlchemy, and dependency injection.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🔄 **Async/Sync Support** - Flexible database operations with both async and sync patterns
- 🗄️ **Multi-Database Support** - SQLite, PostgreSQL, MySQL support
- 🏗️ **Clean Architecture** - Repository pattern with dependency injection
- 🧪 **Comprehensive Testing** - Unit and integration tests with high coverage
- 📦 **Docker Ready** - Containerized application with Docker Compose
- 🔧 **Development Tools** - Pre-commit hooks, linting, formatting, and type checking
- 📚 **Documentation** - Auto-generated API documentation
- ⚡ **UV Package Manager** - Fast Python package management with uv

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- Docker and Docker Compose (optional)

### Installation

1. **Install uv**
   ```bash
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Or with pip
   pip install uv
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/db-adapter.git
   cd db-adapter
   ```

3. **Set up environment**
   ```bash
   # Copy environment file
   cp env.example .env
   
   # Install dependencies
   uv sync --dev
   
   # Set up pre-commit hooks
   uv run pre-commit install
   ```

4. **Run the application**
   ```bash
   # Development mode
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Or with make
   make dev
   
   # Or with Docker
   make docker-dev
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Project Structure

```
db_adapter/
├── api/                    # API layer
│   └── v1/
│       ├── controllers/    # FastAPI route handlers
│       └── schemas/        # Pydantic models for API
├── config.py              # Application configuration
├── container.py           # Dependency injection container
├── infras/               # Infrastructure layer
│   └── repositories/      # Database repositories
├── models/               # Domain models
├── ports/                # Interface definitions
├── repositories/         # Repository implementations
├── services/             # Business logic layer
├── tests/                # Test suite
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── Makefile              # Development commands
├── pyproject.toml        # Project configuration (uv)
└── uv.lock              # Dependency lock file
```

## Configuration

The application uses environment variables for configuration. Copy `env.example` to `.env` and adjust the settings:

```bash
# Database Configuration
USE_ASYNC_DB=true                    # Use async database operations
REPO_DRIVER=async_db                 # Repository driver type
USE_ASYNC_ROUTER=true               # Use async API routes

# Database URLs
DB_URL_SYNC=sqlite:///./example.db  # Sync database URL
DB_URL_ASYNC=sqlite+aiosqlite:///./example.db  # Async database URL

# SQLAlchemy Configuration
ECHO=false                           # SQL query logging
POOL_SIZE=20                        # Connection pool size
MAX_OVERFLOW=10                     # Max overflow connections
POOL_RECYCLE=1800                   # Connection recycle time
POOL_TIMEOUT=5                      # Connection timeout
```

## Database Support

### SQLite (Default)
```bash
DB_URL_SYNC=sqlite:///./example.db
DB_URL_ASYNC=sqlite+aiosqlite:///./example.db
```

### PostgreSQL
```bash
# Install PostgreSQL dependencies
uv add psycopg2-binary asyncpg

# Update environment
DB_URL_SYNC=postgresql://user:password@localhost:5432/dbname
DB_URL_ASYNC=postgresql+asyncpg://user:password@localhost:5432/dbname
```

### MySQL
```bash
# Install MySQL dependencies
uv add pymysql asyncmy

# Update environment
DB_URL_SYNC=mysql+pymysql://user:password@localhost:3306/dbname
DB_URL_ASYNC=mysql+asyncmy://user:password@localhost:3306/dbname
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/items/` | List all items |
| GET | `/items/{id}` | Get item by ID |
| POST | `/items/` | Create new item |
| PUT | `/items/{id}` | Update item |
| DELETE | `/items/{id}` | Delete item |

### Example API Usage

```bash
# Create an item
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Item",
    "description": "A sample item",
    "price": 99.99,
    "category": "electronics"
  }'

# List all items
curl -X GET "http://localhost:8000/items/"

# Get specific item
curl -X GET "http://localhost:8000/items/{id}"

# Update item
curl -X PUT "http://localhost:8000/items/{id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Item",
    "description": "Updated description",
    "price": 149.99,
    "category": "premium"
  }'

# Delete item
curl -X DELETE "http://localhost:8000/items/{id}"
```

## Development

### Available Commands

```bash
# Installation
make install          # Install production dependencies
make install-dev      # Install development dependencies
make install-all      # Install all dependencies including optional groups

# Testing
make test             # Run tests
make test-cov         # Run tests with coverage
make test-fast        # Run tests in parallel

# Code Quality
make lint             # Run linting
make format           # Format code
make format-check     # Check code formatting
make type-check       # Run type checking

# Security
make security         # Run security checks

# Docker
make docker-build     # Build Docker image
make docker-run       # Run Docker container
make docker-dev       # Run development environment
make docker-clean     # Clean up Docker resources

# Development
make dev              # Run development server
make run              # Run production server

# Database
make db-migrate       # Run database migrations
make db-revision      # Create new migration

# Documentation
make docs             # Build documentation
make docs-serve       # Serve documentation locally

# UV specific commands
make uv-init          # Initialize uv project
make uv-lock          # Generate lock file
make uv-sync          # Sync dependencies
make uv-add           # Add a dependency (use: make uv-add package=package_name)
make uv-add-dev       # Add a development dependency
make uv-remove        # Remove a dependency
make uv-upgrade       # Upgrade dependencies

# Setup
make setup            # Complete development setup
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test categories
uv run pytest -m unit        # Unit tests only
uv run pytest -m integration # Integration tests only
uv run pytest -m "not slow"  # Exclude slow tests

# Run async tests
uv run pytest -m async_test

# Run tests in parallel
uv run pytest -n auto
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **bandit** - Security analysis
- **pre-commit** - Git hooks

```bash
# Format code
uv run black .
uv run isort .

# Check formatting
uv run black . --check
uv run isort . --check-only

# Run all quality checks
make ci
```

## Docker

### Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# Access the application
# API: http://localhost:8000
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### Production Environment

```bash
# Start production environment
docker-compose up --build

# Or build and run manually
docker build -t db-adapter .
docker run -p 8000:8000 db-adapter
```

## Testing

The project includes comprehensive tests:

- **Unit Tests** - Test individual components
- **Integration Tests** - Test component interactions
- **API Tests** - Test HTTP endpoints
- **Async Tests** - Test async functionality

### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── test_api.py          # API endpoint tests
├── test_services.py     # Service layer tests
├── test_repositories.py # Repository tests
└── test_models.py       # Model tests
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_api.py

# Run with verbose output
uv run pytest -v

# Run and generate coverage report
uv run pytest --cov=. --cov-report=html --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/db-adapter.git
cd db-adapter

# Set up development environment
make setup

# Run tests to ensure everything works
make test

# Start development server
make dev
```

### Code Style

The project follows strict code style guidelines:

- Use **Black** for code formatting
- Use **isort** for import sorting
- Follow **PEP 8** for style guidelines
- Use **type hints** for all functions
- Write **docstrings** for all public functions

```bash
# Format code before committing
uv run black .
uv run isort .

# Check code quality
uv run flake8 .
uv run mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database toolkit
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Dependency Injector](https://python-dependency-injector.ets-labs.org/) - Dependency injection
- [UV](https://github.com/astral-sh/uv) - Fast Python package manager

## Support

If you have any questions or need help, please:

1. Check the [documentation](https://db-adapter.readthedocs.io)
2. Search [existing issues](https://github.com/yourusername/db-adapter/issues)
3. Create a [new issue](https://github.com/yourusername/db-adapter/issues/new)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history. 