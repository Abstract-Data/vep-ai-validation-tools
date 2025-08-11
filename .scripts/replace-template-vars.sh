#!/bin/bash

# UV Template Variable Replacement Script
# This script helps you replace all template variables in the project

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

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        eval "$var_name=\${input:-$default}"
    else
        read -p "$prompt: " input
        eval "$var_name=\"$input\""
    fi
}

# Function to validate email format
validate_email() {
    local email="$1"
    if [[ "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate project name format
validate_project_name() {
    local name="$1"
    if [[ "$name" =~ ^[a-z][a-z0-9-]*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate package name format
validate_package_name() {
    local name="$1"
    if [[ "$name" =~ ^[a-z][a-z0-9_]*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate version format
validate_version() {
    local version="$1"
    if [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to convert project name to package name
project_to_package_name() {
    local project_name="$1"
    echo "$project_name" | sed 's/-/_/g'
}

# Function to convert project name to GitHub username (guess)
project_to_github_username() {
    local project_name="$1"
    echo "$project_name" | sed 's/-//g'
}

print_status "🚀 UV Template Variable Replacement Script"
echo ""
print_status "This script will help you replace all template variables in your project."
echo ""

# Get project information
prompt_with_default "Enter your project name (e.g., my-awesome-project)" "" PROJECT_NAME

# Validate project name
while ! validate_project_name "$PROJECT_NAME"; do
    print_error "Invalid project name. Use lowercase letters, numbers, and hyphens only."
    prompt_with_default "Enter your project name" "" PROJECT_NAME
done

# Auto-generate package name
PACKAGE_NAME=$(project_to_package_name "$PROJECT_NAME")
prompt_with_default "Enter your package name" "$PACKAGE_NAME" PACKAGE_NAME

# Validate package name
while ! validate_package_name "$PACKAGE_NAME"; do
    print_error "Invalid package name. Use lowercase letters, numbers, and underscores only."
    prompt_with_default "Enter your package name" "$PACKAGE_NAME" PACKAGE_NAME
done

# Get version
prompt_with_default "Enter initial version" "0.1.0" VERSION

# Validate version
while ! validate_version "$VERSION"; do
    print_error "Invalid version format. Use semantic versioning (e.g., 0.1.0)."
    prompt_with_default "Enter initial version" "0.1.0" VERSION
done

# Get description
prompt_with_default "Enter project description" "A Python package built with UV" DESCRIPTION

# Get author information
prompt_with_default "Enter your name" "" AUTHOR_NAME
prompt_with_default "Enter your email" "" AUTHOR_EMAIL

# Validate email
while ! validate_email "$AUTHOR_EMAIL"; do
    print_error "Invalid email format."
    prompt_with_default "Enter your email" "" AUTHOR_EMAIL
done

# Get GitHub username
GITHUB_USERNAME=$(project_to_github_username "$PROJECT_NAME")
prompt_with_default "Enter your GitHub username" "$GITHUB_USERNAME" GITHUB_USERNAME

# Get keywords
prompt_with_default "Enter keywords (comma-separated)" "python,package" KEYWORDS

# Get security email
prompt_with_default "Enter security contact email" "$AUTHOR_EMAIL" SECURITY_EMAIL

# Validate security email
while ! validate_email "$SECURITY_EMAIL"; do
    print_error "Invalid email format."
    prompt_with_default "Enter security contact email" "$AUTHOR_EMAIL" SECURITY_EMAIL
done

echo ""
print_status "📋 Summary of your configuration:"
echo "  Project Name: $PROJECT_NAME"
echo "  Package Name: $PACKAGE_NAME"
echo "  Version: $VERSION"
echo "  Description: $DESCRIPTION"
echo "  Author: $AUTHOR_NAME <$AUTHOR_EMAIL>"
echo "  GitHub Username: $GITHUB_USERNAME"
echo "  Keywords: $KEYWORDS"
echo "  Security Email: $SECURITY_EMAIL"
echo ""

# Confirm before proceeding
read -p "Proceed with these values? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    print_warning "Aborted. Run the script again to reconfigure."
    exit 1
fi

print_status "🔄 Replacing template variables..."

# Replace variables in all relevant files
find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.sh" \) -not -path "./.git/*" -exec sed -i '' \
    -e "s/{{ project_name }}/$PROJECT_NAME/g" \
    -e "s/{{ package_name }}/$PACKAGE_NAME/g" \
    -e "s/{{ version }}/$VERSION/g" \
    -e "s/{{ description }}/$DESCRIPTION/g" \
    -e "s/{{ author_name }}/$AUTHOR_NAME/g" \
    -e "s/{{ author_email }}/$AUTHOR_EMAIL/g" \
    -e "s/{{ github_username }}/$GITHUB_USERNAME/g" \
    -e "s/{{ keywords }}/$KEYWORDS/g" \
    -e "s/{{ security_email }}/$SECURITY_EMAIL/g" {} \;

# Handle pyproject.toml.template if it exists
if [ -f "pyproject.toml.template" ]; then
    print_status "Processing pyproject.toml.template..."
    sed -e "s/{{ project_name }}/$PROJECT_NAME/g" \
        -e "s/{{ package_name }}/$PACKAGE_NAME/g" \
        -e "s/{{ version }}/$VERSION/g" \
        -e "s/{{ description }}/$DESCRIPTION/g" \
        -e "s/{{ author_name }}/$AUTHOR_NAME/g" \
        -e "s/{{ author_email }}/$AUTHOR_EMAIL/g" \
        -e "s/{{ github_username }}/$GITHUB_USERNAME/g" \
        -e "s/{{ keywords }}/$KEYWORDS/g" \
        -e "s/{{ security_email }}/$SECURITY_EMAIL/g" \
        pyproject.toml.template > pyproject.toml
    print_success "✅ pyproject.toml generated from template"
fi

print_success "✅ Template variables replaced successfully!"

# Rename package directory if needed
if [ -d "src/{{ package_name }}" ]; then
    mv "src/{{ package_name }}" "src/$PACKAGE_NAME"
    print_success "✅ Package directory renamed to src/$PACKAGE_NAME"
fi

# Update __init__.py imports if needed
if [ -f "src/$PACKAGE_NAME/__init__.py" ]; then
    sed -i '' "s/from \.core import/from .core import/" "src/$PACKAGE_NAME/__init__.py"
fi

# Update test imports if needed
if [ -f ".tests/test_core.py" ]; then
    sed -i '' "s/from {{ package_name }}/from $PACKAGE_NAME/" ".tests/test_core.py"
fi

print_success "🎉 Template setup complete!"
echo ""
print_status "Next steps:"
echo "  1. Run: chmod +x scripts/setup-uv-project.sh"
echo "  2. Run: ./scripts/setup-uv-project.sh"
echo "  3. Run: uv sync"
echo "  4. Run: uv run pre-commit install"
echo "  5. Initialize git repository"
echo ""
print_status "See TEMPLATE.md for detailed instructions."
