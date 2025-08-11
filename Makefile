.PHONY: help install test lint format clean build release

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting and type checking"
	@echo "  format     - Format code with black and isort"
	@echo "  clean      - Clean build artifacts"
	@echo "  build      - Build the package"
	@echo "  release    - Create a new release"

# Install dependencies
install:
	uv sync
	uv run pre-commit install

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Run linting and type checking
lint:
	uv run pre-commit run --all-files

# Format code
format:
	uv run black .
	uv run isort .

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build the package
build:
	uv run build

# Create a new release
release:
	@echo "Creating a new release..."
	@echo "1. Update version in pyproject.toml"
	@echo "2. Commit changes"
	@echo "3. Create and push a tag"
	@echo "4. GitHub Actions will handle the rest"

# Development server (if applicable)
dev:
	@echo "Starting development server..."
	# Add your development server command here
	# uv run python -m {{ package_name }}.core

# Check for security issues
security:
	uv run bandit -r src/

# Update dependencies
update:
	uv lock --upgrade

# Show dependency tree
deps:
	uv tree

# Run all checks
check: lint test
	@echo "All checks passed! ✅"
