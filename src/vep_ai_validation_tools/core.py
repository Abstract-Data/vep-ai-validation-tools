"""
Core functionality for vep-ai-validation-tools.

This module contains the main business logic for the package.
"""

from typing import Any, Dict, Optional


def hello_world(name: Optional[str] = None) -> str:
    """
    Return a greeting message.

    Args:
        name: Optional name to include in the greeting

    Returns:
        A greeting string

    Examples:
        >>> hello_world()
        'Hello, World!'
        >>> hello_world("Alice")
        'Hello, Alice!'
    """
    if name is None:
        return "Hello, World!"
    return f"Hello, {name}!"


def get_version_info() -> Dict[str, Any]:
    """
    Get version information about the package.

    Returns:
        Dictionary containing version information
    """
    from . import __author__, __email__, __version__

    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
    }


def main() -> None:
    """Main entry point for the package."""
    print(hello_world())
    print(f"Version: {get_version_info()['version']}")


if __name__ == "__main__":
    main()
