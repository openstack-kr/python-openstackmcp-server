import pytest
from unittest.mock import Mock
from openstack_mcp_server.tools.cinder_tools import CinderTools


class TestCinderTools:
    """Test cases for CinderTools class."""

    def test_get_cinder_volumes_success(self, mock_get_openstack_conn_cinder):
        """Test getting cinder volumes successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Create mock volume objects
        mock_volume1 = Mock()
        mock_volume1.name = "web-data-volume"
        mock_volume1.id = "abc123-def456-ghi789"
        mock_volume1.status = "available"

        mock_volume2 = Mock()
        mock_volume2.name = "db-backup-volume"
        mock_volume2.id = "xyz789-uvw456-rst123"
        mock_volume2.status = "in-use"

        # Configure mock block_storage.volumes()
        mock_conn.block_storage.volumes.return_value = [mock_volume1, mock_volume2]

        # Test CinderTools
        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        # Verify results
        expected_output = (
            "web-data-volume (abc123-def456-ghi789) - Status: available\n"
            "db-backup-volume (xyz789-uvw456-rst123) - Status: in-use"
        )
        assert result == expected_output

        # Verify mock calls
        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_empty_list(self, mock_get_openstack_conn_cinder):
        """Test getting cinder volumes when no volumes exist."""
        mock_conn = mock_get_openstack_conn_cinder

        # Empty volume list
        mock_conn.block_storage.volumes.return_value = []

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        # Verify empty string
        assert result == ""

        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_single_volume(self, mock_get_openstack_conn_cinder):
        """Test getting cinder volumes with a single volume."""
        mock_conn = mock_get_openstack_conn_cinder

        # Single volume
        mock_volume = Mock()
        mock_volume.name = "test-volume"
        mock_volume.id = "single-123"
        mock_volume.status = "creating"

        mock_conn.block_storage.volumes.return_value = [mock_volume]

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        expected_output = "test-volume (single-123) - Status: creating"
        assert result == expected_output

        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_multiple_statuses(self, mock_get_openstack_conn_cinder):
        """Test volumes with various statuses."""
        mock_conn = mock_get_openstack_conn_cinder

        # Volumes with different statuses
        volumes_data = [
            ("volume-available", "id-1", "available"),
            ("volume-in-use", "id-2", "in-use"),
            ("volume-error", "id-3", "error"),
            ("volume-creating", "id-4", "creating"),
            ("volume-deleting", "id-5", "deleting"),
        ]

        mock_volumes = []
        for name, volume_id, status in volumes_data:
            mock_volume = Mock()
            mock_volume.name = name
            mock_volume.id = volume_id
            mock_volume.status = status
            mock_volumes.append(mock_volume)

        mock_conn.block_storage.volumes.return_value = mock_volumes

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        # Verify each volume is included in the result
        for name, volume_id, status in volumes_data:
            expected_line = f"{name} ({volume_id}) - Status: {status}"
            assert expected_line in result

        # Verify line count (5 volumes)
        assert len(result.split('\n')) == 5

        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_with_special_characters(self, mock_get_openstack_conn_cinder):
        """Test volumes with special characters in names."""
        mock_conn = mock_get_openstack_conn_cinder

        # Volume names with special characters
        mock_volume1 = Mock()
        mock_volume1.name = "web-volume_test-01"
        mock_volume1.id = "id-with-dashes"
        mock_volume1.status = "available"

        mock_volume2 = Mock()
        mock_volume2.name = "db.volume.prod"
        mock_volume2.id = "id.with.dots"
        mock_volume2.status = "in-use"

        mock_conn.block_storage.volumes.return_value = [mock_volume1, mock_volume2]

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        assert "web-volume_test-01 (id-with-dashes) - Status: available" in result
        assert "db.volume.prod (id.with.dots) - Status: in-use" in result

        mock_conn.block_storage.volumes.assert_called_once()

    def test_register_tools(self):
        """Test that tools are properly registered with FastMCP."""
        # Create FastMCP mock
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator

        cinder_tools = CinderTools()
        cinder_tools.register_tools(mock_mcp)

        # Verify mcp.tool() was called
        mock_mcp.tool.assert_called_once()

        # Verify decorator was applied to get_cinder_volumes method
        mock_tool_decorator.assert_called_once_with(cinder_tools.get_cinder_volumes)

    def test_cinder_tools_instantiation(self):
        """Test CinderTools can be instantiated."""
        cinder_tools = CinderTools()
        assert cinder_tools is not None
        assert hasattr(cinder_tools, 'register_tools')
        assert hasattr(cinder_tools, 'get_cinder_volumes')
        assert callable(cinder_tools.register_tools)
        assert callable(cinder_tools.get_cinder_volumes)

    def test_get_cinder_volumes_docstring(self):
        """Test that get_cinder_volumes has proper docstring."""
        cinder_tools = CinderTools()
        docstring = cinder_tools.get_cinder_volumes.__doc__

        assert docstring is not None
        assert "Get the list of Cinder volumes" in docstring
        assert "return" in docstring.lower() or "Return" in docstring
