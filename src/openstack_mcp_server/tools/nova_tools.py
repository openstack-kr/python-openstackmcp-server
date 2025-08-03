from .base import get_openstack_conn
from mcp.server.fastmcp import FastMCP


class NovaTools:
    """
    A class to encapsulate Nova-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Nova-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_nova_servers)

    def get_nova_servers(self) -> str:
        """
        Get the list of Nova servers by invoking the registered tool.

        :return: A string containing the names, IDs, and statuses of the servers.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the servers
        server_list = []
        for server in conn.compute.list_servers():
            server_list.append(
                f"{server.name} ({server.id}) - Status: {server.status}"
            )

        return "\n".join(server_list)
