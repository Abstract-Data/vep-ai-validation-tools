#!/bin/bash

# Post-install script for UV template
# This script runs automatically after uv sync to clean up template files
# and set up a fresh git repository

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

# Check if this is the first time running
POST_INSTALL_FLAG=".post-install-complete"

if [ -f "$POST_INSTALL_FLAG" ]; then
    # Already completed, just exit silently
    exit 0
fi

# Check if we're in a template state (has template variables)
if ! grep -q "vep-ai-validation-tools" pyproject.toml 2>/dev/null; then
    # Not a template, just mark as complete and exit
    touch "$POST_INSTALL_FLAG"
    exit 0
fi

print_status "🚀 UV Template detected! Running automatic setup..."

# Check if we're in a git repository (template clone)
if [ -d ".git" ]; then
    print_status "Detected template clone. Setting up fresh project..."

    # Run the template variable replacement script if it exists
    if [ -f "scripts/replace-template-vars.sh" ]; then
        print_status "Running template variable replacement..."
        chmod +x scripts/replace-template-vars.sh
        ./scripts/replace-template-vars.sh
    else
        print_error "Template replacement script not found. Please run manually:"
        print_error "  ./scripts/replace-template-vars.sh"
        exit 1
    fi

    # Remove the template's git history
    print_status "Removing template git history..."
    rm -rf .git

    # Initialize new git repository
    print_status "Initializing new git repository..."
    git init

    # Add all files
    git add .

    # Create initial commit
    git commit -m "🎉 Initial project setup from UV template"

    print_success "✅ Fresh git repository created!"

else
    print_status "No git repository found. Initializing new repository..."
    git init
    git add .
    git commit -m "🎉 Initial project setup"
    print_success "✅ Git repository initialized!"
fi

# Run the UV project setup script if it exists
if [ -f "scripts/setup-uv-project.sh" ]; then
    print_status "Running UV project setup..."
    chmod +x scripts/setup-uv-project.sh
    ./scripts/setup-uv-project.sh
else
    print_warning "UV project setup script not found."
fi

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
if command -v uv &> /dev/null; then
    uv run pre-commit install
    print_success "✅ Pre-commit hooks installed!"
else
    print_warning "UV not found. Please install pre-commit hooks manually:"
    print_warning "  uv run pre-commit install"
fi

# Mark as complete
touch "$POST_INSTALL_FLAG"

# Success message
print_success "🎉 UV Template setup completed automatically!"
echo ""
print_status "Your project is now ready for development!"
echo ""
print_status "Next steps:"
echo "  1. Review and customize your project files"
echo "  2. Add your project dependencies to pyproject.toml"
echo "  3. Write your code in src/vep_ai_validation_tools/"
echo "  4. Add tests in .tests/"
echo "  5. Update documentation in docs/"
echo "  6. Push to GitHub: git remote add origin <your-repo-url> && git push -u origin main"
echo ""
print_status "Available commands:"
echo "  uv sync                    # Install dependencies"
echo "  uv run pytest             # Run tests"
echo "  uv run pre-commit run --all-files  # Run linting"
echo "  make help                 # Show all available commands"
echo ""
print_status "Happy coding! 🚀"
