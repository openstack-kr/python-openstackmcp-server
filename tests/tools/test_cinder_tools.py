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

    def test_get_volume_details_success(self, mock_get_openstack_conn_cinder):
        """Test getting volume details successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Create mock volume with detailed info
        mock_volume = Mock()
        mock_volume.name = "test-volume"
        mock_volume.id = "vol-123"
        mock_volume.status = "available"
        mock_volume.size = 20
        mock_volume.volume_type = "ssd"
        mock_volume.availability_zone = "nova"
        mock_volume.created_at = "2024-01-01T12:00:00Z"
        mock_volume.is_bootable = False
        mock_volume.is_encrypted = True
        mock_volume.attachments = []

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.get_volume_details("vol-123")

        # Verify key information is present
        assert "Volume Details:" in result
        assert "Name: test-volume" in result
        assert "ID: vol-123" in result
        assert "Status: available" in result
        assert "Size: 20 GB" in result
        assert "Volume Type: ssd" in result
        assert "Bootable: False" in result
        assert "Encrypted: True" in result

        mock_conn.block_storage.get_volume.assert_called_once_with("vol-123")

    def test_get_volume_details_with_attachments(self, mock_get_openstack_conn_cinder):
        """Test getting volume details with attachments."""
        mock_conn = mock_get_openstack_conn_cinder

        # Create mock volume with attachments
        mock_volume = Mock()
        mock_volume.name = "attached-volume"
        mock_volume.id = "vol-attached"
        mock_volume.status = "in-use"
        mock_volume.size = 10
        mock_volume.volume_type = None
        mock_volume.availability_zone = "nova"
        mock_volume.created_at = "2024-01-01T12:00:00Z"
        mock_volume.is_bootable = True
        mock_volume.is_encrypted = False
        mock_volume.attachments = [
            {"server_id": "server-123", "device": "/dev/vdb"},
            {"server_id": "server-456", "device": "/dev/vdc"}
        ]

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.get_volume_details("vol-attached")

        assert "Attachments: 2 attachment(s)" in result
        assert "Attachment Details:" in result
        assert "Server ID: server-123" in result
        assert "Device: /dev/vdb" in result
        assert "Server ID: server-456" in result
        assert "Device: /dev/vdc" in result

    def test_get_volume_details_error(self, mock_get_openstack_conn_cinder):
        """Test getting volume details with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.get_volume.side_effect = Exception("Volume not found")

        cinder_tools = CinderTools()
        result = cinder_tools.get_volume_details("nonexistent-vol")

        assert "Error retrieving volume details: Volume not found" in result

    def test_create_volume_success(self, mock_get_openstack_conn_cinder):
        """Test creating volume successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Mock created volume
        mock_volume = Mock()
        mock_volume.name = "new-volume"
        mock_volume.id = "vol-new-123"
        mock_volume.size = 10
        mock_volume.status = "creating"

        mock_conn.block_storage.create_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.create_volume("new-volume", 10, "Test volume", "ssd", "nova")

        assert "Volume creation initiated:" in result
        assert "Name: new-volume" in result
        assert "ID: vol-new-123" in result
        assert "Size: 10 GB" in result
        assert "Status: creating" in result

        mock_conn.block_storage.create_volume.assert_called_once_with(
            name="new-volume",
            size=10,
            description="Test volume",
            volume_type="ssd",
            availability_zone="nova"
        )

    def test_create_volume_minimal_params(self, mock_get_openstack_conn_cinder):
        """Test creating volume with minimal parameters."""
        mock_conn = mock_get_openstack_conn_cinder

        mock_volume = Mock()
        mock_volume.name = "minimal-volume"
        mock_volume.id = "vol-minimal"
        mock_volume.size = 5
        mock_volume.status = "creating"

        mock_conn.block_storage.create_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.create_volume("minimal-volume", 5)

        mock_conn.block_storage.create_volume.assert_called_once_with(
            name="minimal-volume",
            size=5
        )

    def test_create_volume_error(self, mock_get_openstack_conn_cinder):
        """Test creating volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.create_volume.side_effect = Exception("Quota exceeded")

        cinder_tools = CinderTools()
        result = cinder_tools.create_volume("fail-volume", 100)

        assert "Error creating volume: Quota exceeded" in result

    def test_delete_volume_success(self, mock_get_openstack_conn_cinder):
        """Test deleting volume successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Mock volume to be deleted
        mock_volume = Mock()
        mock_volume.name = "delete-me"
        mock_volume.id = "vol-delete"

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.delete_volume("vol-delete", False)

        assert "Volume deletion initiated:" in result
        assert "Name: delete-me" in result
        assert "ID: vol-delete" in result
        assert "Force: False" in result

        mock_conn.block_storage.get_volume.assert_called_once_with("vol-delete")
        mock_conn.block_storage.delete_volume.assert_called_once_with("vol-delete", force=False)

    def test_delete_volume_force(self, mock_get_openstack_conn_cinder):
        """Test force deleting volume."""
        mock_conn = mock_get_openstack_conn_cinder

        mock_volume = Mock()
        mock_volume.name = None  # Test unnamed volume
        mock_volume.id = "vol-force-delete"

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.delete_volume("vol-force-delete", True)

        assert "Name: Unnamed" in result
        assert "Force: True" in result

        mock_conn.block_storage.delete_volume.assert_called_once_with("vol-force-delete", force=True)

    def test_delete_volume_error(self, mock_get_openstack_conn_cinder):
        """Test deleting volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.get_volume.side_effect = Exception("Volume not found")

        cinder_tools = CinderTools()
        result = cinder_tools.delete_volume("nonexistent-vol")

        assert "Error deleting volume: Volume not found" in result

    def test_extend_volume_success(self, mock_get_openstack_conn_cinder):
        """Test extending volume successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Mock current volume
        mock_volume = Mock()
        mock_volume.name = "extend-me"
        mock_volume.id = "vol-extend"
        mock_volume.size = 10

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.extend_volume("vol-extend", 20)

        assert "Volume extension initiated:" in result
        assert "Name: extend-me" in result
        assert "Current Size: 10 GB" in result
        assert "New Size: 20 GB" in result

        mock_conn.block_storage.get_volume.assert_called_once_with("vol-extend")
        mock_conn.block_storage.extend_volume.assert_called_once_with("vol-extend", 20)

    def test_extend_volume_invalid_size(self, mock_get_openstack_conn_cinder):
        """Test extending volume with invalid size."""
        mock_conn = mock_get_openstack_conn_cinder

        mock_volume = Mock()
        mock_volume.size = 20

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.extend_volume("vol-extend", 15)

        assert "Error: New size (15 GB) must be larger than current size (20 GB)" in result
        mock_conn.block_storage.extend_volume.assert_not_called()

    def test_extend_volume_error(self, mock_get_openstack_conn_cinder):
        """Test extending volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.get_volume.side_effect = Exception("Volume busy")

        cinder_tools = CinderTools()
        result = cinder_tools.extend_volume("vol-busy", 30)

        assert "Error extending volume: Volume busy" in result

    def test_attach_volume_success(self, mock_get_openstack_conn_cinder):
        """Test attaching volume successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Mock server and volume
        mock_server = Mock()
        mock_server.name = "test-server"
        mock_server.id = "server-123"

        mock_volume = Mock()
        mock_volume.name = "attach-vol"
        mock_volume.id = "vol-attach"

        mock_attachment = Mock()
        mock_attachment.id = "attachment-123"

        mock_conn.compute.get_server.return_value = mock_server
        mock_conn.block_storage.get_volume.return_value = mock_volume
        mock_conn.compute.create_volume_attachment.return_value = mock_attachment

        cinder_tools = CinderTools()
        result = cinder_tools.attach_volume_to_server("server-123", "vol-attach", "/dev/vdb")

        assert "Volume attachment initiated:" in result
        assert "Server: test-server (server-123)" in result
        assert "Volume: attach-vol (vol-attach)" in result
        assert "Device: /dev/vdb" in result
        assert "Attachment ID: attachment-123" in result

        mock_conn.compute.create_volume_attachment.assert_called_once_with(
            server="server-123",
            volume="vol-attach",
            device="/dev/vdb"
        )

    def test_attach_volume_auto_device(self, mock_get_openstack_conn_cinder):
        """Test attaching volume with auto-assigned device."""
        mock_conn = mock_get_openstack_conn_cinder

        mock_server = Mock()
        mock_server.name = "auto-server"
        mock_volume = Mock()
        mock_volume.name = None  # Test unnamed volume
        mock_attachment = Mock()
        mock_attachment.id = "auto-attachment"

        mock_conn.compute.get_server.return_value = mock_server
        mock_conn.block_storage.get_volume.return_value = mock_volume
        mock_conn.compute.create_volume_attachment.return_value = mock_attachment

        cinder_tools = CinderTools()
        result = cinder_tools.attach_volume_to_server("server-123", "vol-attach")

        assert "Volume: Unnamed (vol-attach)" in result
        assert "Device: Auto-assigned" in result

        mock_conn.compute.create_volume_attachment.assert_called_once_with(
            server="server-123",
            volume="vol-attach"
        )

    def test_attach_volume_error(self, mock_get_openstack_conn_cinder):
        """Test attaching volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.compute.get_server.side_effect = Exception("Server not found")

        cinder_tools = CinderTools()
        result = cinder_tools.attach_volume_to_server("nonexistent-server", "vol-attach")

        assert "Error attaching volume: Server not found" in result

    def test_detach_volume_success(self, mock_get_openstack_conn_cinder):
        """Test detaching volume successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Mock server and volume
        mock_server = Mock()
        mock_server.name = "detach-server"
        mock_server.id = "server-456"

        mock_volume = Mock()
        mock_volume.name = "detach-vol"
        mock_volume.id = "vol-detach"

        mock_conn.compute.get_server.return_value = mock_server
        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.detach_volume_from_server("server-456", "vol-detach")

        assert "Volume detachment initiated:" in result
        assert "Server: detach-server (server-456)" in result
        assert "Volume: detach-vol (vol-detach)" in result

        mock_conn.compute.delete_volume_attachment.assert_called_once_with("vol-detach", "server-456")

    def test_detach_volume_error(self, mock_get_openstack_conn_cinder):
        """Test detaching volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.compute.get_server.side_effect = Exception("Server not found")

        cinder_tools = CinderTools()
        result = cinder_tools.detach_volume_from_server("nonexistent-server", "vol-detach")

        assert "Error detaching volume: Server not found" in result

    def test_register_tools(self):
        """Test that tools are properly registered with FastMCP."""
        # Create FastMCP mock
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator

        cinder_tools = CinderTools()
        cinder_tools.register_tools(mock_mcp)

        # Verify mcp.tool() was called for each method
        assert mock_mcp.tool.call_count == 7

        # Verify all methods were registered
        registered_methods = [call[0][0] for call in mock_tool_decorator.call_args_list]
        expected_methods = [
            cinder_tools.get_cinder_volumes,
            cinder_tools.get_volume_details,
            cinder_tools.create_volume,
            cinder_tools.delete_volume,
            cinder_tools.extend_volume,
            cinder_tools.attach_volume_to_server,
            cinder_tools.detach_volume_from_server,
        ]

        for method in expected_methods:
            assert method in registered_methods

    def test_cinder_tools_instantiation(self):
        """Test CinderTools can be instantiated."""
        cinder_tools = CinderTools()
        assert cinder_tools is not None
        assert hasattr(cinder_tools, 'register_tools')
        assert hasattr(cinder_tools, 'get_cinder_volumes')
        assert hasattr(cinder_tools, 'get_volume_details')
        assert hasattr(cinder_tools, 'create_volume')
        assert hasattr(cinder_tools, 'delete_volume')
        assert hasattr(cinder_tools, 'extend_volume')
        assert hasattr(cinder_tools, 'attach_volume_to_server')
        assert hasattr(cinder_tools, 'detach_volume_from_server')

        # Verify all methods are callable
        assert callable(cinder_tools.register_tools)
        assert callable(cinder_tools.get_cinder_volumes)
        assert callable(cinder_tools.get_volume_details)
        assert callable(cinder_tools.create_volume)
        assert callable(cinder_tools.delete_volume)
        assert callable(cinder_tools.extend_volume)
        assert callable(cinder_tools.attach_volume_to_server)
        assert callable(cinder_tools.detach_volume_from_server)

    def test_get_cinder_volumes_docstring(self):
        """Test that get_cinder_volumes has proper docstring."""
        cinder_tools = CinderTools()
        docstring = cinder_tools.get_cinder_volumes.__doc__

        assert docstring is not None
        assert "Get the list of Cinder volumes" in docstring
        assert "return" in docstring.lower() or "Return" in docstring

    def test_all_methods_have_docstrings(self):
        """Test that all public methods have proper docstrings."""
        cinder_tools = CinderTools()
        
        methods_to_check = [
            'get_cinder_volumes',
            'get_volume_details', 
            'create_volume',
            'delete_volume',
            'extend_volume',
            'attach_volume_to_server',
            'detach_volume_from_server'
        ]
        
        for method_name in methods_to_check:
            method = getattr(cinder_tools, method_name)
            docstring = method.__doc__
            assert docstring is not None, f"{method_name} should have a docstring"
            assert len(docstring.strip()) > 0, f"{method_name} docstring should not be empty"
