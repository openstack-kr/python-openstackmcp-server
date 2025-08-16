import uuid

from unittest.mock import Mock

from openstack_mcp_server.tools.image_tools import ImageTools
from openstack_mcp_server.tools.request.image import CreateImage
from openstack_mcp_server.tools.response.image import Image


class ImageMockFactory:
    @staticmethod
    def image(**overrides):
        defaults = {
            "id": str(uuid.uuid4()),
            "name": "test-image",
            "checksum": "abc123",
            "container_format": "bare",
            "disk_format": "qcow2",
            "file": None,
            "min_disk": 1,
            "min_ram": 512,
            "os_hash_algo": "sha512",
            "os_hash_value": "hash123",
            "size": 1073741824,
            "virtual_size": None,
            "owner": str(uuid.uuid4()),
            "visibility": "public",
            "hw_rng_model": None,
            "status": "active",
            "schema": "/v2/schemas/image",
            "protected": False,
            "os_hidden": False,
            "tags": [],
            "properties": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z",
            "owner_specified.openstack.md5": "a1b2c3d4e5f6",
            "owner_specified.openstack.sha256": "a1b2c3d",
            "owner_specified.openstack.object": "image",
        }
        for key, value in overrides.items():
            if value is not None:
                defaults[key] = value

        return defaults


class TestImageTools:
    """Test cases for ImageTools class."""

    def test_get_image_images_success(self, mock_get_openstack_conn_image):
        """Test getting image images successfully."""
        mock_conn = mock_get_openstack_conn_image

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

        # Test ImageTools
        image_tools = ImageTools()
        result = image_tools.get_image_images()

        # Verify results
        expected_output = (
            "ubuntu-20.04-server (img-123-abc-def) - Status: active\n"
            "centos-8-stream (img-456-ghi-jkl) - Status: active"
        )
        assert result == expected_output

        # Verify mock calls
        mock_conn.image.images.assert_called_once()

    def test_get_image_images_empty_list(self, mock_get_openstack_conn_image):
        """Test getting image images when no images exist."""
        mock_conn = mock_get_openstack_conn_image

        # Empty image list
        mock_conn.image.images.return_value = []

        image_tools = ImageTools()
        result = image_tools.get_image_images()

        # Verify empty string
        assert result == ""

        mock_conn.image.images.assert_called_once()

    def test_get_image_images_with_empty_name(
        self,
        mock_get_openstack_conn_image,
    ):
        """Test images with empty or None names."""
        mock_conn = mock_get_openstack_conn_image

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

        image_tools = ImageTools()
        result = image_tools.get_image_images()

        assert "normal-image (img-normal) - Status: active" in result
        assert " (img-empty-name) - Status: active" in result  # Empty name

        mock_conn.image.images.assert_called_once()

    def test_create_image_success_with_volume_id(
        self,
        mock_get_openstack_conn_image,
    ):
        """Test creating an image from a volume ID."""
        volume_id = "6cf57d8d-00ca-43ff-ae6f-56912b69528a"  # Example volume ID

        mock_image = ImageMockFactory.image()
        mock_get_openstack_conn_image.block_storage.create_image.return_value = Mock(
            id=mock_image["id"],
        )
        mock_get_openstack_conn_image.get_image.return_value = mock_image

        # Create an instance with volume ID
        image_tools = ImageTools()
        image_data = CreateImage(
            name=mock_image["name"],
            volume=volume_id,
            allow_duplicates=False,
            container=mock_image["container_format"],
            disk_format=mock_image["disk_format"],
            container_format=mock_image["container_format"],
            min_disk=mock_image["min_disk"],
        )

        expected_output = Image(**mock_image)

        created_image = image_tools.create_image(image_data)

        # Verify the created image
        assert created_image == expected_output
        assert mock_get_openstack_conn_image.block_storage.create_image.called_once_with(
            name=mock_image["name"],
            volume=volume_id,
            allow_duplicates=False,
            container=mock_image["container_format"],
            disk_format=mock_image["disk_format"],
            wait=False,
            timeout=3600,
        )

        assert mock_get_openstack_conn_image.get_image.called_once_with(
            mock_image["id"],
        )

    def test_create_image_success_with_import_options(
        self,
        mock_get_openstack_conn_image,
    ):
        """Test creating an image with import options."""
        create_image_data = CreateImage(
            name="example_image",
            container="bare",
            disk_format="qcow2",
            container_format="bare",
            min_disk=10,
            min_ram=512,
            tags=["example", "test"],
            import_options=CreateImage.ImportOptions(
                import_method="web-download",
                uri="https://example.com/image.qcow2",
            ),
            allow_duplicates=False,
        )

        mock_image = ImageMockFactory.image(**create_image_data.__dict__)
        mock_create_image = Mock(id=mock_image["id"])

        mock_get_openstack_conn_image.image.create_image.return_value = (
            mock_create_image
        )
        mock_get_openstack_conn_image.image.import_image.return_value = None
        mock_get_openstack_conn_image.get_image.return_value = mock_image

        # Create an instance with import options
        image_tools = ImageTools()

        expected_output = Image(**mock_image)

        created_image = image_tools.create_image(create_image_data)

        # Verify the created image
        assert created_image == expected_output
        assert (
            mock_get_openstack_conn_image.image.create_image.called_once_with(
                name=create_image_data.name,
                container=create_image_data.container,
                container_format=create_image_data.container_format,
                disk_format=create_image_data.disk_format,
                min_disk=create_image_data.min_disk,
                min_ram=create_image_data.min_ram,
                tags=create_image_data.tags,
                protected=create_image_data.protected,
                visibility=create_image_data.visibility,
                allow_duplicates=create_image_data.allow_duplicates,
            )
        )
        assert mock_get_openstack_conn_image.image.import_image.called_once_with(
            image=mock_create_image,
            method=create_image_data.import_options.import_method,
            uri=create_image_data.import_options.uri,
            stores=create_image_data.import_options.stores,
            remote_region=create_image_data.import_options.glance_region,
            remote_image_id=create_image_data.import_options.glance_image_id,
            remote_service_interface=create_image_data.import_options.glance_service_interface,
        )
        assert mock_get_openstack_conn_image.get_image.called_once_with(
            mock_image["id"],
        )
