#!/bin/bash

# Auto-generate README.md content based on project structure
# This script analyzes the source code and generates appropriate descriptions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect project type and features
detect_project_features() {
    local features=""

    # Check for common Python features
    if [ -f "pyproject.toml" ]; then
        features="$features- **📦 Modern Python Package** - Built with pyproject.toml and UV\n"
    fi

    if [ -f ".pre-commit-config.yaml" ]; then
        features="$features- **🔧 Pre-commit Hooks** - Automated code quality checks\n"
    fi

    if [ -d ".github/workflows" ]; then
        features="$features- **🤖 GitHub Actions** - Automated CI/CD pipeline\n"
    fi

    if [ -f "pyproject.toml" ] && grep -q "pytest" pyproject.toml; then
        features="$features- **🧪 Testing** - Comprehensive test suite with pytest\n"
    fi

    if [ -f "pyproject.toml" ] && grep -q "black" pyproject.toml; then
        features="$features- **🎨 Code Formatting** - Black and isort for consistent styling\n"
    fi

    if [ -f "pyproject.toml" ] && grep -q "mypy" pyproject.toml; then
        features="$features- **🔍 Type Checking** - MyPy for static type analysis\n"
    fi

    if [ -d "docs" ] || [ -d ".docs" ]; then
        features="$features- **📚 Documentation** - Comprehensive project documentation\n"
    fi

    if [ -f "SECURITY.md" ]; then
        features="$features- **🔒 Security** - Security policy and vulnerability reporting\n"
    fi

    echo -e "$features"
}

# Function to analyze source code structure
analyze_source_structure() {
    local description=""

    if [ -d "src" ]; then
        local package_dirs=$(find src -maxdepth 1 -type d | grep -v "^src$" | wc -l)
        if [ "$package_dirs" -gt 0 ]; then
            description="$description\n### 📁 Package Structure\n\n"
            description="$description\`\`\`\n"
            description="$description$(find src -type f -name "*.py" | head -10 | sed 's|^|├── |')\n"
            if [ "$(find src -type f -name "*.py" | wc -l)" -gt 10 ]; then
                description="$description└── ... (and more)\n"
            fi
            description="$description\`\`\`\n\n"
        fi
    fi

    # Check for CLI scripts
    if [ -f "pyproject.toml" ] && grep -q "scripts" pyproject.toml; then
        description="$description### 🖥️ Command Line Interface\n\n"
        description="$descriptionThis package provides command-line tools. See the project configuration for available commands.\n\n"
    fi

    echo -e "$description"
}

# Function to generate installation instructions based on project
generate_installation_instructions() {
    echo "## 🚀 Installation"
    echo ""
    echo "### Using UV (Recommended)"
    echo ""
    echo "\`\`\`bash"
    echo "# Install from source"
    echo "git clone https://github.com/Abstract-Data/vep-ai-validation-tools.git"
    echo "cd vep-ai-validation-tools"
    echo "uv sync"
    echo "\`\`\`"
    echo ""

    if grep -q "hatchling" pyproject.toml 2>/dev/null; then
        echo "### Using pip"
        echo ""
        echo "\`\`\`bash"
        echo "pip install vep-ai-validation-tools"
        echo "\`\`\`"
        echo ""
    fi
}

# Function to generate usage examples based on source code
generate_usage_examples() {
    echo "## 📖 Usage"
    echo ""

    # Look for main module or CLI entry points
    if [ -f "src/vep_ai_validation_tools/__main__.py" ]; then
        echo "### Command Line Usage"
        echo ""
        echo "\`\`\`bash"
        echo "python -m vep_ai_validation_tools"
        echo "\`\`\`"
        echo ""
    fi

    echo "### Python API"
    echo ""
    echo "\`\`\`python"
    echo "import vep_ai_validation_tools"
    echo ""
    echo "# Your usage examples here"
    echo "\`\`\`"
    echo ""
}

# Main function
main() {
    print_status "🔍 Analyzing project structure for README auto-generation..."

    # Check if this is a template project
    if grep -q "vep-ai-validation-tools" pyproject.toml 2>/dev/null; then
        print_warning "This appears to be a template project. Auto-generation will use template variables."
    fi

    print_status "Detecting project features..."
    local features=$(detect_project_features)

    print_status "Analyzing source code structure..."
    local structure=$(analyze_source_structure)

    print_status "Generating content sections..."

    # Create auto-generated content file
    cat > /tmp/auto-generated-readme-content.md << EOF
<!-- Auto-generated content sections -->
## ✨ Features

$features

$(generate_installation_instructions)

$(generate_usage_examples)

$structure
EOF

    print_success "✅ Auto-generated content saved to /tmp/auto-generated-readme-content.md"
    print_status "You can review and integrate this content into your README.md"

    # Show preview
    echo ""
    print_status "Preview of generated content:"
    echo "----------------------------------------"
    cat /tmp/auto-generated-readme-content.md
    echo "----------------------------------------"
}

# Check if we should run auto-generation
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Auto-generate README.md content based on project structure"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo "  --preview     Show preview without writing files"
    echo ""
    echo "This script analyzes your project structure and generates"
    echo "appropriate README.md content sections based on:"
    echo "  - Package structure and files"
    echo "  - Dependencies and tools in pyproject.toml"
    echo "  - GitHub Actions and CI/CD setup"
    echo "  - Documentation structure"
    echo ""
    exit 0
fi

if [ "$1" = "--preview" ]; then
    main
    exit 0
fi

# Ask user if they want to proceed
echo ""
print_status "This will analyze your project and generate README content."
read -p "Proceed with auto-generation? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    print_warning "Auto-generation cancelled."
    exit 0
fi

main
