from fastmcp import FastMCP

from openstack_mcp_server.tools.request.image import CreateImage
from openstack_mcp_server.tools.response.image import Image

from .base import get_openstack_conn


class ImageTools:
    """
    A class to encapsulate Image-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Image-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_images)
        mcp.tool()(self.create_image)

    def get_images(
        self,
        name: str | None = None,
        status: str | None = None,
        visibility: str | None = None,
    ) -> list[Image]:
        """
        Get the list of OpenStack images with optional filtering.

        The filtering behavior is as follows:
        - By default, all available images are returned without any filtering applied.
        - Filters are only applied when specific values are provided by the user.

        :param name: Filter by image name
        :param status: Filter by status
        :param visibility: Filter by visibility
        :return: A list of Image objects.
        """
        conn = get_openstack_conn()

        # Build filters for the image query
        filters = {}
        if name and name.strip():
            filters["name"] = name.strip()
        if status and status.strip():
            filters["status"] = status.strip()
        if visibility and visibility.strip():
            filters["visibility"] = visibility.strip()

        image_list = []
        for image in conn.image.images(**filters):
            image_list.append(Image(**image))

        return image_list

    def create_image(self, image_data: CreateImage) -> Image:
        """Create a new Openstack image.
        This method handles both cases of image creation:
        1. If a volume is provided, it creates an image from the volume.
        2. If no volume is provided, it creates an image using the Image imports method
            import_options field is required for this method.
        Following import methods are supported:
        - glance-direct: The image data is made available to the Image service via the Stage binary
        - web-download: The image data is made available to the Image service by being posted to an accessible location with a URL that you know.
            - must provide a URI to the image data.
        - copy-image: The image data is made available to the Image service by copying existing image
        - glance-download: The image data is made available to the Image service by fetching an image accessible from another glance service specified by a region name and an image id that you know.
            - must provide a glance_region and glance_image_id.

        :param image_data: An instance of CreateImage containing the image details.
        :return: An Image object representing the created image.
        """
        conn = get_openstack_conn()

        if image_data.volume:
            created_image = conn.block_storage.create_image(
                name=image_data.name,
                volume=image_data.volume,
                allow_duplicates=image_data.allow_duplicates,
                container_format=image_data.container_format,
                disk_format=image_data.disk_format,
                wait=False,
                timeout=3600,
            )
        else:
            # Create an image with Image imports
            # First, Creates a catalog record for an operating system disk image.
            created_image = conn.image.create_image(
                name=image_data.name,
                container=image_data.container,
                container_format=image_data.container_format,
                disk_format=image_data.disk_format,
                min_disk=image_data.min_disk,
                min_ram=image_data.min_ram,
                tags=image_data.tags,
                protected=image_data.protected,
                visibility=image_data.visibility,
                allow_duplicates=image_data.allow_duplicates,
            )

            # Then, import the image data
            conn.image.import_image(
                image=created_image,
                method=image_data.import_options.import_method,
                uri=image_data.import_options.uri,
                stores=image_data.import_options.stores,
                remote_region=image_data.import_options.glance_region,
                remote_image_id=image_data.import_options.glance_image_id,
                remote_service_interface=image_data.import_options.glance_service_interface,
            )

        image = conn.get_image(created_image.id)
        return Image(**image)
