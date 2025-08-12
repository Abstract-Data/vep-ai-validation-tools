# 🚀 vep-ai-validation-tools

A Python package built with UV

<!-- AUTO_GENERATED_CONTENT_START -->
<!-- Auto-generated content sections -->

## ✨ Features

- **📦 Modern Python Package** - Built with pyproject.toml and UV
- **🔧 Pre-commit Hooks** - Automated code quality checks
- **🤖 GitHub Actions** - Automated CI/CD pipeline
- **🧪 Testing** - Comprehensive test suite with pytest
- **🎨 Code Formatting** - Black and isort for consistent styling
- **🔍 Type Checking** - MyPy for static type analysis
- **📚 Documentation** - Comprehensive project documentation
- **🔒 Security** - Security policy and vulnerability reporting

## 🚀 Installation

### Using UV (Recommended)

```bash
# Install from source
git clone https://github.com/Abstract-Data/vep-ai-validation-tools.git
cd vep-ai-validation-tools
uv sync
```

### Using pip

```bash
pip install vep-ai-validation-tools
```

## 📖 Usage

### Python API

```python
import vep_ai_validation_tools

# Your usage examples here
```

### 📁 Package Structure

```
├── src/vep_ai_validation_tools/__init__.py
├── src/vep_ai_validation_tools/core.py
```

<!-- AUTO_GENERATED_CONTENT_END -->

## 📁 Project Structure

```
vep-ai-validation-tools/
├── src/
│   └── vep_ai_validation_tools/     # Your package source code
├── .tests/                     # Test files
├── .docs/                      # Documentation
├── .scripts/                   # Utility scripts
├── .github/                    # GitHub Actions and templates
│   ├── workflows/              # CI/CD workflows
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── pyproject.toml             # Project configuration
├── README.md                  # This file
└── .gitignore                 # Git ignore rules
```

## 🛠️ Development

### Available Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run pre-commit run --all-files

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy src/

# Build package
uv run build
```

### Pre-commit Hooks

This template includes pre-commit hooks for:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking
- **pytest** - Test running

## 🤖 GitHub Actions

### Automated Workflows

1. **CI/CD Pipeline** - Runs on every push and PR
   - Linting and formatting checks
   - Type checking
   - Test execution
   - Coverage reporting

2. **Release Automation** - Automated releases on version tags
   - Version bumping
   - Release notes generation
   - Package publishing

3. **Issue Management** - Automated labeling and triaging
   - Issue categorization
   - PR labeling
   - Release note drafting

## 📝 Issue Templates

### Available Templates

- **🐛 Bug Report** - For reporting bugs and issues
- **✨ Feature Request** - For requesting new features
- **📝 General Issue** - For questions and discussions

### Using Templates

1. Go to the Issues tab
2. Click "New Issue"
3. Select the appropriate template
4. Fill in the required information
5. Submit the issue

## 🔄 Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the coding standards
3. **Run tests locally** to ensure everything works
4. **Submit a PR** using the provided template
5. **Wait for CI checks** to pass
6. **Get code review** from maintainers
7. **Merge when approved**

## 📚 Documentation

- **[UV Template Guide](docs/uv-template-guide.md)** - Comprehensive setup and usage guide
- **[Auto-labeling Guide](docs/auto-labeling.md)** - Understanding automated labeling
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🔧 Configuration

### Project Settings

Update the following files with your project details:

- `pyproject.toml` - Project metadata and dependencies
- `README.md` - Project description and documentation
- `.github/` - GitHub-specific configurations

### Customization

- **Add dependencies** in `pyproject.toml`
- **Modify workflows** in `.github/workflows/`
- **Update templates** in `.github/ISSUE_TEMPLATE/`
- **Customize scripts** in `.scripts/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure all checks pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation** - Check the [docs/](docs/) directory
- **Issues** - Use the 🐛 Bug Report template
- **Discussions** - Use the 📝 General Issue template

## 🙏 Acknowledgments

- [UV](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- [GitHub Actions](https://github.com/features/actions) - CI/CD automation
- [Pre-commit](https://pre-commit.com/) - Git hooks framework
- [Hatch](https://hatch.pypa.io/) - Modern Python project manager

---

**Happy coding! 🎉**
