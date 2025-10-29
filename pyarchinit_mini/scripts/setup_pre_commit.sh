#!/bin/bash
# Setup pre-commit hooks for PyArchInit-Mini

set -e

echo "🔧 Setting up pre-commit hooks for PyArchInit-Mini..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "⚠️  pre-commit is not installed. Installing..."
    pip install pre-commit
fi

# Install the git hooks
echo "📦 Installing pre-commit hooks..."
pre-commit install

echo "✅ Pre-commit hooks installed successfully!"
echo ""
echo "The following hooks are now active:"
echo "  • Documentation verification (versions, language)"
echo "  • Python code formatting (black, isort)"
echo "  • Python linting (flake8)"
echo "  • YAML/TOML/JSON validation"
echo "  • Markdown linting"
echo ""
echo "To run hooks manually: pre-commit run --all-files"
echo "To skip hooks: git commit --no-verify"
