# DB Adapter Documentation

Welcome to the DB Adapter documentation! This project provides a flexible database adapter with async/sync support built with FastAPI, SQLAlchemy, and dependency injection.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🔄 **Async/Sync Support** - Flexible database operations with both async and sync patterns
- 🗄️ **Multi-Database Support** - SQLite, PostgreSQL, MySQL support
- 🏗️ **Clean Architecture** - Repository pattern with dependency injection
- 🧪 **Comprehensive Testing** - Unit and integration tests with high coverage
- 📦 **Docker Ready** - Containerized application with Docker Compose
- 🔧 **Development Tools** - Pre-commit hooks, linting, formatting, and type checking
- 📚 **Documentation** - Auto-generated API documentation

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/db-adapter.git
cd db-adapter

# Set up environment
cp env.example .env
make install-dev
make pre-commit-install

# Run the application
make dev
```

## API Documentation

Once the application is running, you can access:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Getting Started

Check out our [installation guide](getting-started/installation.md) and [quick start tutorial](getting-started/quick-start.md) to get up and running quickly.

## Contributing

We welcome contributions! Please see our [contributing guide](development/contributing.md) for details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yourusername/db-adapter/blob/main/LICENSE) file for details. 