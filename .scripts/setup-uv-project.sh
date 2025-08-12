#!/bin/bash

# Generic UV Project Setup Script
# This script sets up a new UV project with standard configurations

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

# Function to get project name from pyproject.toml
get_project_name() {
    if [ -f "pyproject.toml" ]; then
        grep '^name =' pyproject.toml | cut -d'"' -f2 2>/dev/null || echo "my-project"
    else
        echo "my-project"
    fi
}

# Function to get project version from pyproject.toml
get_project_version() {
    if [ -f "pyproject.toml" ]; then
        grep '^version =' pyproject.toml | cut -d'"' -f2 2>/dev/null || echo "0.1.0"
    else
        echo "0.1.0"
    fi
}

# Function to get Python version requirement
get_python_version() {
    if [ -f "pyproject.toml" ]; then
        grep 'requires-python' pyproject.toml | cut -d'"' -f2 2>/dev/null || echo ">=3.8"
    else
        echo ">=3.8"
    fi
}

# Function to setup project structure
setup_project_structure() {
    local project_name=$1

    print_status "Setting up project structure..."

    # Create standard directories
    mkdir -p src/"$project_name"
    mkdir -p tests
    mkdir -p docs
    mkdir -p scripts
    mkdir -p .github/workflows
    mkdir -p .github/ISSUE_TEMPLATE

    # Create __init__.py files
    touch src/"$project_name"/__init__.py
    touch .tests/__init__.py

    print_success "Project structure created"
}

# Function to setup git repository
setup_git() {
    print_status "Setting up Git repository..."

    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        print_status "Git repository initialized"
    else
        print_status "Git repository already exists"
    fi

    # Add all files
    git add .

    # Initial commit
    if git diff --cached --quiet; then
        print_status "No changes to commit"
    else
        git commit -m "🎉 Initial project setup with standard configurations"
        print_success "Initial commit created"
    fi
}

# Function to setup pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."

    # Check if pre-commit is installed
    if ! command -v pre-commit &> /dev/null; then
        print_warning "pre-commit not found. Installing..."
        uv add --dev pre-commit
    fi

    # Install pre-commit hooks
    if [ -f ".pre-commit-config.yaml" ]; then
        pre-commit install
        pre-commit install --hook-type commit-msg
        print_success "Pre-commit hooks installed"
    else
        print_warning "No .pre-commit-config.yaml found. Skipping pre-commit setup."
    fi
}

# Function to setup GitHub Actions
setup_github_actions() {
    print_status "Setting up GitHub Actions workflows..."

    # Check if workflows directory exists
    if [ ! -d ".github/workflows" ]; then
        print_error ".github/workflows directory not found. Please ensure GitHub Actions files are present."
        return 1
    fi

    # List available workflows
    local workflow_count=$(find .github/workflows -name "*.yml" | wc -l)
    print_success "Found $workflow_count GitHub Actions workflows"

    # Show available workflows
    if [ "$workflow_count" -gt 0 ]; then
        print_status "Available workflows:"
        find .github/workflows -name "*.yml" -exec basename {} \;
    fi
}

# Function to validate setup
validate_setup() {
    print_status "Validating project setup..."

    local project_name=$(get_project_name)
    local project_version=$(get_project_version)
    local python_version=$(get_python_version)

    echo "Project Name: $project_name"
    echo "Project Version: $project_version"
    echo "Python Version: $python_version"

    # Check for required files
    local required_files=("pyproject.toml" ".gitignore" "README.md")
    local missing_files=()

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "All required files present"
    else
        print_warning "Missing files: ${missing_files[*]}"
    fi

    # Check for workflows
    if [ -d ".github/workflows" ] && [ "$(find .github/workflows -name "*.yml" | wc -l)" -gt 0 ]; then
        print_success "GitHub Actions workflows present"
    else
        print_warning "No GitHub Actions workflows found"
    fi

    # Check for pre-commit config
    if [ -f ".pre-commit-config.yaml" ]; then
        print_success "Pre-commit configuration present"
    else
        print_warning "No pre-commit configuration found"
    fi
}

# Function to show next steps
show_next_steps() {
    local project_name=$(get_project_name)

    echo ""
    echo "🎉 Project setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Review and customize project configuration"
    echo "2. Add your source code to src/$project_name/"
    echo "3. Write tests in .tests/"
    echo "4. Update README.md with project documentation"
    echo "5. Configure GitHub repository settings"
    echo ""
    echo "🔧 Available commands:"
    echo "  uv sync                    # Install dependencies"
    echo "  uv run pytest             # Run tests"
    echo "  uv run pre-commit run --all-files  # Run pre-commit hooks"
    echo "  ./scripts/create-release.sh create patch  # Create a release"
    echo ""
    echo "📚 Documentation:"
    echo "  - docs/auto-labeling.md   # Auto-labeling system"
    echo "  - .github/                # GitHub Actions and templates"
    echo "  - .pre-commit-config.yaml # Code quality hooks"
    echo ""
    echo "🚀 Happy coding!"
}

# Main setup function
main() {
    print_status "Starting UV project setup..."

    # Get project information
    local project_name=$(get_project_name)
    local project_version=$(get_project_version)

    echo "Project: $project_name"
    echo "Version: $project_version"
    echo ""

    # Setup project structure
    setup_project_structure "$project_name"

    # Setup git repository
    setup_git

    # Setup pre-commit hooks
    setup_pre_commit

    # Setup GitHub Actions
    setup_github_actions

    # Validate setup
    validate_setup

    # Show next steps
    show_next_steps
}

# Run main function
main "$@"
