from fastmcp import FastMCP

from openstack_mcp_server.tools.response.compute import Server

from .base import get_openstack_conn


class ComputeTools:
    """
    A class to encapsulate Compute-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Compute-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_compute_servers)
        mcp.tool()(self.get_compute_server)

    def get_compute_servers(self) -> list[Server]:
        """
        Get the list of Compute servers by invoking the registered tool.

        :return: A list of Server objects representing the Compute servers.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the servers
        server_list = []
        for server in conn.compute.servers():
            server_list.append(
                Server(name=server.name, id=server.id, status=server.status),
            )

        return server_list

    def get_compute_server(self, id: str) -> Server:
        """
        Get a specific Compute server by invoking the registered tool.

        :param id: The ID of the server to retrieve.
        :return: A Server object representing the Compute server.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # Get a specific server (for example, the first one)
        server = conn.compute.get_server(id)
        return Server(name=server.name, id=server.id, status=server.status)
