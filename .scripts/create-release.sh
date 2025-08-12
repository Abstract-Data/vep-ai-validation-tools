#!/bin/bash

# Release Management Script
# This script helps with manual release creation and version bumping

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

# Function to get current version from pyproject.toml
get_current_version() {
    grep '^version = ' pyproject.toml | cut -d'"' -f2
}

# Function to bump version
bump_version() {
    local version_type=$1
    local current_version=$(get_current_version)
    local major minor patch

    IFS='.' read -r major minor patch <<< "$current_version"

    case $version_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid version type. Use: major, minor, or patch"
            exit 1
            ;;
    esac

    echo "${major}.${minor}.${patch}"
}

# Function to create a release
create_release() {
    local version_type=$1
    local new_version=$(bump_version $version_type)
    local tag_name="v${new_version}"

    print_status "Creating release: $tag_name"

    # Check if we're on main/master branch
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" && "$current_branch" != "master" ]]; then
        print_error "You must be on main or master branch to create a release"
        exit 1
    fi

    # Check if working directory is clean
    if [[ -n $(git status --porcelain) ]]; then
        print_error "Working directory is not clean. Please commit or stash changes first."
        exit 1
    fi

    # Update version in pyproject.toml
    print_status "Updating version in pyproject.toml to $new_version"
    sed -i.bak "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml
    rm pyproject.toml.bak

    # Commit version bump
    git add pyproject.toml
    git commit -m "📦 Bump version to $new_version"

    # Create and push tag
    print_status "Creating tag: $tag_name"
    git tag -a "$tag_name" -m "Release $tag_name"
    git push origin "$current_branch"
    git push origin "$tag_name"

    print_success "Release $tag_name created successfully!"
    print_status "GitHub Actions will automatically generate release notes and publish the release."
}

# Function to show help
show_help() {
    echo "Release Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  create <type>    Create a new release"
    echo "  version          Show current version"
    echo "  help             Show this help message"
    echo ""
    echo "Release Types:"
    echo "  major           Bump major version (x.0.0)"
    echo "  minor           Bump minor version (0.x.0)"
    echo "  patch           Bump patch version (0.0.x)"
    echo ""
    echo "Examples:"
    echo "  $0 create patch    # Create a patch release"
    echo "  $0 create minor    # Create a minor release"
    echo "  $0 create major    # Create a major release"
    echo "  $0 version         # Show current version"
}

# Main script logic
case "${1:-help}" in
    create)
        if [[ -z "$2" ]]; then
            print_error "Please specify release type: major, minor, or patch"
            exit 1
        fi
        create_release "$2"
        ;;
    version)
        current_version=$(get_current_version)
        print_status "Current version: $current_version"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
