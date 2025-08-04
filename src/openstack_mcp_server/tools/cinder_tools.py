from .base import get_openstack_conn
from fastmcp import FastMCP


class CinderTools:
    """
    A class to encapsulate Cinder-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Cinder-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_cinder_volumes)

    def get_cinder_volumes(self) -> str:
        """
        Get the list of Cinder volumes by invoking the registered tool.

        :return: A string containing the names, IDs, and statuses of the volumes.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the volumes
        volume_list = []
        for volume in conn.block_storage.volumes():
            volume_list.append(
                f"{volume.name} ({volume.id}) - Status: {volume.status}"
            )

        return "\n".join(volume_list)
