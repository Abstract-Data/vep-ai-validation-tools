#!/bin/bash

# Setup script for pre-commit hooks and security tools
# This script installs pre-commit hooks and gitignore-checker

set -e

echo "🔒 Setting up security and code quality tools..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Install gitignore-checker if not already installed
if ! command -v gitignore-checker &> /dev/null; then
    echo "📦 Installing gitignore-checker..."
    if command -v pip &> /dev/null; then
        pip install gitignore-checker
    elif command -v pip3 &> /dev/null; then
        pip3 install gitignore-checker
    else
        echo "❌ Error: pip not found. Please install Python and pip first."
        exit 1
    fi
else
    echo "✅ gitignore-checker already installed"
fi

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "📦 Installing pre-commit..."
    if command -v pip &> /dev/null; then
        pip install pre-commit
    elif command -v pip3 &> /dev/null; then
        pip3 install pre-commit
    else
        echo "❌ Error: pip not found. Please install Python and pip first."
        exit 1
    fi
else
    echo "✅ pre-commit already installed"
fi

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Create .secrets.baseline for detect-secrets
if [ ! -f .secrets.baseline ]; then
    echo "🔍 Creating secrets baseline..."
    detect-secrets scan --baseline .secrets.baseline
    echo "✅ Created .secrets.baseline"
else
    echo "✅ .secrets.baseline already exists"
fi

# Test the setup
echo "🧪 Testing setup..."

# Test gitignore-checker
echo "Testing gitignore-checker..."
if gitignore-checker --list-files | head -5; then
    echo "✅ gitignore-checker working"
else
    echo "❌ gitignore-checker test failed"
fi

# Test pre-commit
echo "Testing pre-commit..."
if pre-commit run --all-files; then
    echo "✅ pre-commit working"
else
    echo "⚠️  pre-commit found issues (this is normal for existing code)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 What was installed:"
echo "  • gitignore-checker - Checks for files that should be ignored"
echo "  • pre-commit hooks - Runs checks before commits"
echo "  • detect-secrets baseline - For secret detection"
echo ""
echo "🔒 Security features:"
echo "  • Files matching .gitignore patterns will be caught before commit"
echo "  • Secrets and credentials will be detected"
echo "  • Code quality checks will run automatically"
echo ""
echo "📝 Usage:"
echo "  • Pre-commit hooks run automatically on commit"
echo "  • Run 'pre-commit run --all-files' to check all files"
echo "  • Run 'gitignore-checker --list-files' to see ignored files"
echo ""
echo "🚀 Next steps:"
echo "  1. Commit these changes to enable the hooks"
echo "  2. The GitHub Actions workflow will run on push"
echo "  3. Review any issues found by the security tools"
