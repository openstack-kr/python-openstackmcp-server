import pytest
from openstack_mcp_server.resources.cinder import (
    Volume,
    VolumeAttachment,
)
from openstack_mcp_server.tools.cinder_tools import CinderTools
from unittest.mock import Mock


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
        mock_volume1.size = 10
        mock_volume1.volume_type = "ssd"
        mock_volume1.availability_zone = "nova"
        mock_volume1.created_at = "2024-01-01T12:00:00Z"
        mock_volume1.is_bootable = False
        mock_volume1.is_encrypted = False
        mock_volume1.description = "Web data volume"
        mock_volume1.attachments = []

        mock_volume2 = Mock()
        mock_volume2.name = "db-backup-volume"
        mock_volume2.id = "xyz789-uvw456-rst123"
        mock_volume2.status = "in-use"
        mock_volume2.size = 20
        mock_volume2.volume_type = "hdd"
        mock_volume2.availability_zone = "nova"
        mock_volume2.created_at = "2024-01-02T12:00:00Z"
        mock_volume2.is_bootable = True
        mock_volume2.is_encrypted = True
        mock_volume2.description = "DB backup volume"
        mock_volume2.attachments = []

        # Configure mock block_storage.volumes()
        mock_conn.block_storage.volumes.return_value = [
            mock_volume1,
            mock_volume2,
        ]

        # Test CinderTools
        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        # Verify results
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(vol, Volume) for vol in result)

        # Check first volume
        vol1 = result[0]
        assert vol1.id == "abc123-def456-ghi789"
        assert vol1.name == "web-data-volume"
        assert vol1.status == "available"
        assert vol1.size == 10

        # Check second volume
        vol2 = result[1]
        assert vol2.id == "xyz789-uvw456-rst123"
        assert vol2.name == "db-backup-volume"
        assert vol2.status == "in-use"
        assert vol2.size == 20

        # Verify mock calls
        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_empty_list(
        self, mock_get_openstack_conn_cinder
    ):
        """Test getting cinder volumes when no volumes exist."""
        mock_conn = mock_get_openstack_conn_cinder

        # Empty volume list
        mock_conn.block_storage.volumes.return_value = []

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        # Verify empty list
        assert isinstance(result, list)
        assert len(result) == 0

        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_single_volume(
        self, mock_get_openstack_conn_cinder
    ):
        """Test getting cinder volumes with a single volume."""
        mock_conn = mock_get_openstack_conn_cinder

        # Single volume
        mock_volume = Mock()
        mock_volume.name = "test-volume"
        mock_volume.id = "single-123"
        mock_volume.status = "creating"
        mock_volume.size = 5
        mock_volume.volume_type = None
        mock_volume.availability_zone = "nova"
        mock_volume.created_at = None
        mock_volume.is_bootable = False
        mock_volume.is_encrypted = False
        mock_volume.description = None
        mock_volume.attachments = []

        mock_conn.block_storage.volumes.return_value = [mock_volume]

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].name == "test-volume"
        assert result[0].id == "single-123"
        assert result[0].status == "creating"

        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_multiple_statuses(
        self, mock_get_openstack_conn_cinder
    ):
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
            mock_volume.size = 10
            mock_volume.volume_type = "standard"
            mock_volume.availability_zone = "nova"
            mock_volume.created_at = "2024-01-01T12:00:00Z"
            mock_volume.is_bootable = False
            mock_volume.is_encrypted = False
            mock_volume.description = f"Description for {name}"
            mock_volume.attachments = []
            mock_volumes.append(mock_volume)

        mock_conn.block_storage.volumes.return_value = mock_volumes

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        # Verify result is a list with correct length
        assert isinstance(result, list)
        assert len(result) == 5

        # Verify each volume is included in the result
        result_by_id = {vol.id: vol for vol in result}
        for name, volume_id, status in volumes_data:
            assert volume_id in result_by_id
            vol = result_by_id[volume_id]
            assert vol.name == name
            assert vol.status == status

        mock_conn.block_storage.volumes.assert_called_once()

    def test_get_cinder_volumes_with_special_characters(
        self, mock_get_openstack_conn_cinder
    ):
        """Test volumes with special characters in names."""
        mock_conn = mock_get_openstack_conn_cinder

        # Volume names with special characters
        mock_volume1 = Mock()
        mock_volume1.name = "web-volume_test-01"
        mock_volume1.id = "id-with-dashes"
        mock_volume1.status = "available"
        mock_volume1.size = 15
        mock_volume1.volume_type = "ssd"
        mock_volume1.availability_zone = "nova"
        mock_volume1.created_at = "2024-01-01T12:00:00Z"
        mock_volume1.is_bootable = False
        mock_volume1.is_encrypted = False
        mock_volume1.description = None
        mock_volume1.attachments = []

        mock_volume2 = Mock()
        mock_volume2.name = "db.volume.prod"
        mock_volume2.id = "id.with.dots"
        mock_volume2.status = "in-use"
        mock_volume2.size = 25
        mock_volume2.volume_type = "hdd"
        mock_volume2.availability_zone = "nova"
        mock_volume2.created_at = "2024-01-02T12:00:00Z"
        mock_volume2.is_bootable = True
        mock_volume2.is_encrypted = True
        mock_volume2.description = "Production DB volume"
        mock_volume2.attachments = []

        mock_conn.block_storage.volumes.return_value = [
            mock_volume1,
            mock_volume2,
        ]

        cinder_tools = CinderTools()
        result = cinder_tools.get_cinder_volumes()

        assert isinstance(result, list)
        assert len(result) == 2

        # Find volumes by name
        vol1 = next(vol for vol in result if vol.name == "web-volume_test-01")
        vol2 = next(vol for vol in result if vol.name == "db.volume.prod")

        assert vol1.id == "id-with-dashes"
        assert vol1.status == "available"
        assert vol2.id == "id.with.dots"
        assert vol2.status == "in-use"

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
        mock_volume.description = "Test volume description"
        mock_volume.attachments = []

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.get_volume_details("vol-123")

        # Verify result is a Volume object
        assert isinstance(result, Volume)
        assert result.name == "test-volume"
        assert result.id == "vol-123"
        assert result.status == "available"
        assert result.size == 20
        assert result.volume_type == "ssd"
        assert result.availability_zone == "nova"
        assert not result.is_bootable
        assert result.is_encrypted
        assert result.description == "Test volume description"
        assert len(result.attachments) == 0

        mock_conn.block_storage.get_volume.assert_called_once_with("vol-123")

    def test_get_volume_details_with_attachments(
        self, mock_get_openstack_conn_cinder
    ):
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
        mock_volume.description = "Attached volume"
        mock_volume.attachments = [
            {
                "server_id": "server-123",
                "device": "/dev/vdb",
                "id": "attach-1",
            },
            {
                "server_id": "server-456",
                "device": "/dev/vdc",
                "id": "attach-2",
            },
        ]

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.get_volume_details("vol-attached")

        # Verify result is a Volume object
        assert isinstance(result, Volume)
        assert result.name == "attached-volume"
        assert result.status == "in-use"
        assert len(result.attachments) == 2

        # Verify attachment details
        attach1 = result.attachments[0]
        attach2 = result.attachments[1]

        assert isinstance(attach1, VolumeAttachment)
        assert attach1.server_id == "server-123"
        assert attach1.device == "/dev/vdb"
        assert attach1.attachment_id == "attach-1"

        assert isinstance(attach2, VolumeAttachment)
        assert attach2.server_id == "server-456"
        assert attach2.device == "/dev/vdc"
        assert attach2.attachment_id == "attach-2"

    def test_get_volume_details_error(self, mock_get_openstack_conn_cinder):
        """Test getting volume details with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.get_volume.side_effect = Exception(
            "Volume not found"
        )

        cinder_tools = CinderTools()

        # Should raise exception directly
        with pytest.raises(Exception, match="Volume not found"):
            cinder_tools.get_volume_details("nonexistent-vol")

    def test_create_volume_success(self, mock_get_openstack_conn_cinder):
        """Test creating volume successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        # Mock created volume
        mock_volume = Mock()
        mock_volume.name = "new-volume"
        mock_volume.id = "vol-new-123"
        mock_volume.size = 10
        mock_volume.status = "creating"
        mock_volume.volume_type = "ssd"
        mock_volume.availability_zone = "nova"
        mock_volume.created_at = "2024-01-01T12:00:00Z"
        mock_volume.is_bootable = False
        mock_volume.is_encrypted = False
        mock_volume.description = "Test volume"
        mock_volume.attachments = []

        mock_conn.block_storage.create_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.create_volume(
            "new-volume", 10, "Test volume", "ssd", "nova"
        )

        # Verify result is a Volume object
        assert isinstance(result, Volume)
        assert result.name == "new-volume"
        assert result.id == "vol-new-123"
        assert result.size == 10
        assert result.status == "creating"
        assert result.volume_type == "ssd"
        assert result.availability_zone == "nova"

        mock_conn.block_storage.create_volume.assert_called_once_with(
            size=10,
            image=None,
            bootable=None,
            name="new-volume",
            description="Test volume",
            volume_type="ssd",
            availability_zone="nova",
        )

    def test_create_volume_minimal_params(
        self, mock_get_openstack_conn_cinder
    ):
        """Test creating volume with minimal parameters."""
        mock_conn = mock_get_openstack_conn_cinder

        mock_volume = Mock()
        mock_volume.name = "minimal-volume"
        mock_volume.id = "vol-minimal"
        mock_volume.size = 5
        mock_volume.status = "creating"
        mock_volume.volume_type = None
        mock_volume.availability_zone = None
        mock_volume.created_at = "2024-01-01T12:00:00Z"
        mock_volume.is_bootable = False
        mock_volume.is_encrypted = False
        mock_volume.description = None
        mock_volume.attachments = []

        mock_conn.block_storage.create_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.create_volume("minimal-volume", 5)

        # Verify result structure
        assert isinstance(result, Volume)
        assert result.name == "minimal-volume"
        assert result.size == 5

        mock_conn.block_storage.create_volume.assert_called_once_with(
            size=5, image=None, bootable=None, name="minimal-volume"
        )

    def test_create_volume_with_image_and_bootable(
        self, mock_get_openstack_conn_cinder
    ):
        """Test creating volume with image and bootable parameters."""
        mock_conn = mock_get_openstack_conn_cinder

        mock_volume = Mock()
        mock_volume.name = "bootable-volume"
        mock_volume.id = "vol-bootable"
        mock_volume.size = 20
        mock_volume.status = "creating"
        mock_volume.volume_type = "ssd"
        mock_volume.availability_zone = "nova"
        mock_volume.created_at = "2024-01-01T12:00:00Z"
        mock_volume.is_bootable = True
        mock_volume.is_encrypted = False
        mock_volume.description = "Bootable volume from image"
        mock_volume.attachments = []

        mock_conn.block_storage.create_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.create_volume(
            "bootable-volume",
            20,
            "Bootable volume from image",
            "ssd",
            "nova",
            True,
            "ubuntu-20.04",
        )

        assert isinstance(result, Volume)
        assert result.name == "bootable-volume"
        assert result.id == "vol-bootable"
        assert result.size == 20
        assert result.is_bootable

        mock_conn.block_storage.create_volume.assert_called_once_with(
            size=20,
            image="ubuntu-20.04",
            bootable=True,
            name="bootable-volume",
            description="Bootable volume from image",
            volume_type="ssd",
            availability_zone="nova",
        )

    def test_create_volume_error(self, mock_get_openstack_conn_cinder):
        """Test creating volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.create_volume.side_effect = Exception(
            "Quota exceeded"
        )

        cinder_tools = CinderTools()

        with pytest.raises(Exception, match="Quota exceeded"):
            cinder_tools.create_volume("fail-volume", 100)

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

        # Verify result is None
        assert result is None
        mock_conn.block_storage.delete_volume.assert_called_once_with(
            "vol-delete", force=False
        )

    def test_delete_volume_force(self, mock_get_openstack_conn_cinder):
        """Test force deleting volume."""
        mock_conn = mock_get_openstack_conn_cinder

        mock_volume = Mock()
        mock_volume.name = None  # Test unnamed volume
        mock_volume.id = "vol-force-delete"

        mock_conn.block_storage.get_volume.return_value = mock_volume

        cinder_tools = CinderTools()
        result = cinder_tools.delete_volume("vol-force-delete", True)

        # Verify result is None
        assert result is None

        mock_conn.block_storage.delete_volume.assert_called_once_with(
            "vol-force-delete", force=True
        )

    def test_delete_volume_error(self, mock_get_openstack_conn_cinder):
        """Test deleting volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.delete_volume.side_effect = Exception(
            "Volume not found"
        )

        cinder_tools = CinderTools()

        # Should raise exception directly
        with pytest.raises(Exception, match="Volume not found"):
            cinder_tools.delete_volume("nonexistent-vol")

    def test_extend_volume_success(self, mock_get_openstack_conn_cinder):
        """Test extending volume successfully."""
        mock_conn = mock_get_openstack_conn_cinder

        cinder_tools = CinderTools()
        result = cinder_tools.extend_volume("vol-extend", 20)

        # Verify result is None
        assert result is None

        mock_conn.block_storage.extend_volume.assert_called_once_with(
            "vol-extend", 20
        )

    def test_extend_volume_invalid_size(self, mock_get_openstack_conn_cinder):
        """Test extending volume with invalid size."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.extend_volume.side_effect = Exception(
            "Invalid size"
        )

        cinder_tools = CinderTools()

        with pytest.raises(Exception, match="Invalid size"):
            cinder_tools.extend_volume("vol-extend", 15)

    def test_extend_volume_error(self, mock_get_openstack_conn_cinder):
        """Test extending volume with error."""
        mock_conn = mock_get_openstack_conn_cinder
        mock_conn.block_storage.extend_volume.side_effect = Exception(
            "Volume busy"
        )

        cinder_tools = CinderTools()

        with pytest.raises(Exception, match="Volume busy"):
            cinder_tools.extend_volume("vol-busy", 30)

    def test_register_tools(self):
        """Test that tools are properly registered with FastMCP."""
        # Create FastMCP mock
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator

        cinder_tools = CinderTools()
        cinder_tools.register_tools(mock_mcp)

        # Verify mcp.tool() was called for each method
        assert mock_mcp.tool.call_count == 5

        # Verify all methods were registered
        registered_methods = [
            call[0][0] for call in mock_tool_decorator.call_args_list
        ]
        expected_methods = [
            cinder_tools.get_cinder_volumes,
            cinder_tools.get_volume_details,
            cinder_tools.create_volume,
            cinder_tools.delete_volume,
            cinder_tools.extend_volume,
        ]

        for method in expected_methods:
            assert method in registered_methods

    def test_cinder_tools_instantiation(self):
        """Test CinderTools can be instantiated."""
        cinder_tools = CinderTools()
        assert cinder_tools is not None
        assert hasattr(cinder_tools, "register_tools")
        assert hasattr(cinder_tools, "get_cinder_volumes")
        assert hasattr(cinder_tools, "get_volume_details")
        assert hasattr(cinder_tools, "create_volume")
        assert hasattr(cinder_tools, "delete_volume")
        assert hasattr(cinder_tools, "extend_volume")
        # Verify all methods are callable
        assert callable(cinder_tools.register_tools)
        assert callable(cinder_tools.get_cinder_volumes)
        assert callable(cinder_tools.get_volume_details)
        assert callable(cinder_tools.create_volume)
        assert callable(cinder_tools.delete_volume)
        assert callable(cinder_tools.extend_volume)

    def test_get_cinder_volumes_docstring(self):
        """Test that get_cinder_volumes has proper docstring."""
        cinder_tools = CinderTools()
        docstring = cinder_tools.get_cinder_volumes.__doc__

        assert docstring is not None
        assert "Get the list of Cinder volumes" in docstring
        assert "return" in docstring.lower() or "Return" in docstring
        assert (
            "list[Volume]" in docstring
            or "A list of Volume objects" in docstring
        )

    def test_all_cinder_methods_have_docstrings(self):
        """Test that all public CinderTools methods have proper docstrings."""
        cinder_tools = CinderTools()

        methods_to_check = [
            "get_cinder_volumes",
            "get_volume_details",
            "create_volume",
            "delete_volume",
            "extend_volume",
        ]

        for method_name in methods_to_check:
            method = getattr(cinder_tools, method_name)
            docstring = method.__doc__
            assert docstring is not None, (
                f"{method_name} should have a docstring"
            )
            assert len(docstring.strip()) > 0, (
                f"{method_name} docstring should not be empty"
            )
