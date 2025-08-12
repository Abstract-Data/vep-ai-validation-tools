#!/bin/bash

# UV Hook Script
# This script can be used as a post-install hook for UV
# It automatically runs the post-install setup when uv sync is called

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Run the post-install script
if [ -f "scripts/post-install.sh" ]; then
    echo "🔧 Running post-install setup..."
    ./scripts/post-install.sh
else
    echo "⚠️  Post-install script not found at scripts/post-install.sh"
fi
