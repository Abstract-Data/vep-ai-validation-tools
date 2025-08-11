"""
Tests for the core module.
"""

from uv_template_project.core import get_version_info, hello_world


class TestHelloWorld:
    """Test cases for the hello_world function."""

    def test_hello_world_default(self):
        """Test hello_world with no arguments."""
        result = hello_world()
        assert result == "Hello, World!"

    def test_hello_world_with_name(self):
        """Test hello_world with a name argument."""
        result = hello_world("Alice")
        assert result == "Hello, Alice!"

    def test_hello_world_with_empty_string(self):
        """Test hello_world with an empty string."""
        result = hello_world("")
        assert result == "Hello, !"

    def test_hello_world_with_none(self):
        """Test hello_world with None explicitly passed."""
        result = hello_world(None)
        assert result == "Hello, World!"


class TestGetVersionInfo:
    """Test cases for the get_version_info function."""

    def test_get_version_info_structure(self):
        """Test that get_version_info returns the expected structure."""
        result = get_version_info()

        assert isinstance(result, dict)
        assert "version" in result
        assert "author" in result
        assert "email" in result

    def test_get_version_info_values(self):
        """Test that get_version_info returns non-empty values."""
        result = get_version_info()

        assert result["version"] is not None
        assert result["author"] is not None
        assert result["email"] is not None

        # Version should be a string
        assert isinstance(result["version"], str)
        assert len(result["version"]) > 0


class TestIntegration:
    """Integration tests."""

    def test_import_package(self):
        """Test that the package can be imported."""
        import uv_template_project

        assert hasattr(uv_template_project, "__version__")
        assert hasattr(uv_template_project, "__author__")
        assert hasattr(uv_template_project, "__email__")

    def test_version_consistency(self):
        """Test that version is consistent across modules."""
        import uv_template_project
        from uv_template_project.core import get_version_info

        assert uv_template_project.__version__ == get_version_info()["version"]
