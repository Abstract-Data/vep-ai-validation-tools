#!/bin/bash

# UV Template Setup Script
# This script handles the complete setup process for a new project from this template

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

print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  🚀 UV Template Setup${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

# Check if this is the first time running
SETUP_FLAG=".template-setup-complete"

if [ -f "$SETUP_FLAG" ]; then
    print_warning "Template setup has already been completed."
    read -p "Run setup again? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled."
        exit 0
    fi
    rm -f "$SETUP_FLAG"
fi

print_header

# Step 1: Check if we're in a template state
print_status "Step 1: Checking template state..."

if [ -d ".git" ]; then
    print_status "Detected git repository. Checking if this is a template clone..."

    if grep -q "vep-ai-validation-tools" pyproject.toml 2>/dev/null; then
        print_warning "Template variables detected. This appears to be a fresh template clone."

        # Step 2: Replace template variables
        print_status "Step 2: Replacing template variables..."

        if [ -f ".scripts/replace-template-vars.sh" ]; then
            chmod +x .scripts/replace-template-vars.sh
            ./.scripts/replace-template-vars.sh
        else
            print_error "Template replacement script not found!"
            print_error "Please run: ./.scripts/replace-template-vars.sh"
            exit 1
        fi

        # Step 3: Clean up git history
        print_status "Step 3: Setting up fresh git repository..."

        print_warning "Removing template git history..."
        rm -rf .git

        print_status "Initializing new git repository..."
        git init

        print_status "Adding all files to git..."
        git add .

        print_status "Creating initial commit..."
        git commit -m "🎉 Initial project setup from UV template"

        print_success "✅ Fresh git repository created!"

    else
        print_status "Template variables already replaced. Skipping template setup."
    fi
else
    print_status "No git repository found. Initializing new repository..."
    git init
    git add .
    git commit -m "🎉 Initial project setup"
    print_success "✅ Git repository initialized!"
fi

# Step 4: Run UV project setup
print_status "Step 4: Running UV project setup..."

if [ -f ".scripts/setup-uv-project.sh" ]; then
    chmod +x .scripts/setup-uv-project.sh
    ./.scripts/setup-uv-project.sh
else
    print_warning "UV project setup script not found."
fi

# Step 5: Install dependencies
print_status "Step 5: Installing dependencies..."

if command -v uv &> /dev/null; then
    print_status "Installing project dependencies..."
    uv sync

    print_status "Installing pre-commit hooks..."
    uv run pre-commit install

    print_success "✅ Dependencies installed!"
else
    print_error "UV not found. Please install UV first:"
    print_error "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Step 6: Run initial checks
print_status "Step 6: Running initial checks..."

if command -v uv &> /dev/null; then
    print_status "Running pre-commit hooks..."
    uv run pre-commit run --all-files || true

    print_status "Running tests..."
    uv run pytest || true
fi

# Step 7: Final setup
print_status "Step 7: Finalizing setup..."

# Create a .gitignore entry for the setup flag
if ! grep -q ".template-setup-complete" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Template setup flag" >> .gitignore
    echo ".template-setup-complete" >> .gitignore
fi

# Mark setup as complete
touch "$SETUP_FLAG"

# Success message
print_success "🎉 Template setup completed successfully!"
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
