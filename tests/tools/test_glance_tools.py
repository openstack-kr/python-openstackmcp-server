import pytest
from unittest.mock import Mock
from openstack_mcp_server.tools.glance_tools import GlanceTools


class TestGlanceTools:
    """Test cases for GlanceTools class."""

    def test_get_glance_images_success(self, mock_get_openstack_conn_glance):
        """Test getting glance images successfully."""
        mock_conn = mock_get_openstack_conn_glance

        # Create mock image objects
        mock_image1 = Mock()
        mock_image1.name = "ubuntu-20.04-server"
        mock_image1.id = "img-123-abc-def"
        mock_image1.status = "active"

        mock_image2 = Mock()
        mock_image2.name = "centos-8-stream"
        mock_image2.id = "img-456-ghi-jkl"
        mock_image2.status = "active"

        # Configure mock image.images()
        mock_conn.image.images.return_value = [mock_image1, mock_image2]

        # Test GlanceTools
        glance_tools = GlanceTools()
        result = glance_tools.get_glance_images()

        # Verify results
        expected_output = (
            "ubuntu-20.04-server (img-123-abc-def) - Status: active\n"
            "centos-8-stream (img-456-ghi-jkl) - Status: active"
        )
        assert result == expected_output

        # Verify mock calls
        mock_conn.image.images.assert_called_once()

    def test_get_glance_images_empty_list(self, mock_get_openstack_conn_glance):
        """Test getting glance images when no images exist."""
        mock_conn = mock_get_openstack_conn_glance

        # Empty image list
        mock_conn.image.images.return_value = []

        glance_tools = GlanceTools()
        result = glance_tools.get_glance_images()

        # Verify empty string
        assert result == ""

        mock_conn.image.images.assert_called_once()

    def test_get_glance_images_with_empty_name(self, mock_get_openstack_conn_glance):
        """Test images with empty or None names."""
        mock_conn = mock_get_openstack_conn_glance

        # Images with empty name (edge case)
        mock_image1 = Mock()
        mock_image1.name = "normal-image"
        mock_image1.id = "img-normal"
        mock_image1.status = "active"

        mock_image2 = Mock()
        mock_image2.name = ""  # Empty name
        mock_image2.id = "img-empty-name"
        mock_image2.status = "active"

        mock_conn.image.images.return_value = [mock_image1, mock_image2]

        glance_tools = GlanceTools()
        result = glance_tools.get_glance_images()

        assert "normal-image (img-normal) - Status: active" in result
        assert " (img-empty-name) - Status: active" in result  # Empty name

        mock_conn.image.images.assert_called_once()