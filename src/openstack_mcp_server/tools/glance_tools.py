from .base import get_openstack_conn
from fastmcp import FastMCP


class GlanceTools:
    """
    A class to encapsulate Nova-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Glance-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_glance_images)

    def get_glance_images(self) -> str:
        """
        Get the list of Glance images by invoking the registered tool.

        :return: A string containing the names, IDs, and statuses of the images.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the servers
        image_list = []
        for image in conn.image.images():
            image_list.append(
                f"{image.name} ({image.id}) - Status: {image.status}"
            )

        return "\n".join(image_list)
