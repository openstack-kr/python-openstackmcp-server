from fastmcp import FastMCP

from .base import get_openstack_conn


class ImageTools:
    """
    A class to encapsulate Compute-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Image-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_image_images)

    def get_image_images(self) -> str:
        """
        Get the list of Image images by invoking the registered tool.

        :return: A string containing the names, IDs, and statuses of the images.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the servers
        image_list = []
        for image in conn.image.images():
            image_list.append(
                f"{image.name} ({image.id}) - Status: {image.status}",
            )

        return "\n".join(image_list)
