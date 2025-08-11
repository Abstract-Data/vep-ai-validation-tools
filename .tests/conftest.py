"""
Pytest configuration and fixtures for {{ project_name }} tests.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to Python path
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "version": "1.0.0",
    }


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")
    return file_path


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def src_path(project_root):
    """Get the src directory path."""
    return project_root / "src"


@pytest.fixture
def package_path(src_path):
    """Get the package directory path."""
    return src_path / "uv_template_project"
