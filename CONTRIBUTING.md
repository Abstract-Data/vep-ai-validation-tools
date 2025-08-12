# Contributing to vep-ai-validation-tools

Thank you for your interest in contributing to vep-ai-validation-tools! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

- Use the 🐛 Bug Report template when creating an issue
- Include detailed steps to reproduce the bug
- Provide information about your environment (OS, Python version, etc.)
- Include error messages and stack traces if applicable

### Suggesting Features

- Use the ✨ Feature Request template when creating an issue
- Clearly describe the feature you'd like to see
- Explain why this feature would be useful
- Consider if this feature aligns with the project's goals

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the coding standards
4. **Add tests** for new functionality
5. **Run the test suite** to ensure everything works
   ```bash
   uv run pytest
   ```
6. **Run pre-commit hooks** to ensure code quality
   ```bash
   uv run pre-commit run --all-files
   ```
7. **Commit your changes** with a clear commit message
8. **Push to your fork** and submit a pull request

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive

### Pull Request Template

Use the provided pull request template when creating a PR. It includes:

- Description of changes
- Type of change (bug fix, feature, documentation, etc.)
- Testing instructions
- Checklist for reviewers

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- UV package manager
- Git

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/Abstract-Data/vep-ai-validation-tools.git
   cd vep-ai-validation-tools
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Install pre-commit hooks**

   ```bash
   uv run pre-commit install
   ```

4. **Run tests**
   ```bash
   uv run pytest
   ```

### Code Style

This project uses several tools to maintain code quality:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **pytest** - Testing

Run all checks with:

```bash
uv run pre-commit run --all-files
```

## 📝 Documentation

### Writing Documentation

- Use clear, concise language
- Include code examples where appropriate
- Follow the existing documentation style
- Update the README.md if you add new features

### Documentation Structure

- `README.md` - Project overview and quick start
- `docs/` - Detailed documentation
- `CONTRIBUTING.md` - This file
- `SECURITY.md` - Security policy

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest .tests/test_specific.py

# Run tests with verbose output
uv run pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow the existing test patterns
- Aim for good test coverage

### Test Structure

```
.tests/
├── test_unit/          # Unit tests
├── test_integration/   # Integration tests
└── conftest.py         # Pytest configuration
```

## 🚀 Release Process

### Version Bumping

This project uses semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### Creating a Release

1. **Update version** in `pyproject.toml`
2. **Create a tag** with the new version
3. **Push the tag** to trigger the release workflow
4. **Review the automated release** on GitHub

## 📞 Getting Help

- **Issues** - Use the appropriate issue template
- **Discussions** - Use the 📝 General Issue template
- **Documentation** - Check the `docs/` directory

## 🙏 Acknowledgments

Thank you to all contributors who help make vep-ai-validation-tools better!

## 📄 License

By contributing to vep-ai-validation-tools, you agree that your contributions will be licensed under the MIT License.
