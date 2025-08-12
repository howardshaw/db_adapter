#!/bin/bash

# UV initialization script for db-adapter project

set -e

echo "🚀 Initializing UV for db-adapter project..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or"
    echo "   pip install uv"
    exit 1
fi

echo "✅ UV is installed"

# Initialize uv project if not already initialized
if [ ! -f "pyproject.toml" ]; then
    echo "📝 Initializing UV project..."
    uv init
fi

# Sync dependencies
echo "📦 Installing dependencies..."
uv sync --dev

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
uv run pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please review and update .env file with your configuration"
fi

echo "✅ UV initialization completed!"
echo ""
echo "🎉 You can now run:"
echo "   make dev          # Start development server"
echo "   make test         # Run tests"
echo "   make format       # Format code"
echo "   make lint         # Run linting"
echo ""
echo "📚 For more commands, run: make help" 