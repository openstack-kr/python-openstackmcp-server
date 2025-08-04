from .base import get_openstack_conn
from fastmcp import FastMCP
from pydantic import BaseModel


class Server(BaseModel):
    """A model to represent a Nova server."""

    name: str
    id: str
    status: str


class NovaTools:
    """
    A class to encapsulate Nova-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Nova-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_nova_servers)
        mcp.tool()(self.get_nova_server)

    def get_nova_servers(self) -> list[Server]:
        """
        Get the list of Nova servers by invoking the registered tool.

        :return: A list of Server objects representing the Nova servers.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the servers
        server_list = []
        for server in conn.compute.servers():
            server_list.append(
                Server(name=server.name, id=server.id, status=server.status)
            )

        return server_list

    def get_nova_server(self, id: str) -> Server:
        """
        Get a specific Nova server by invoking the registered tool.
        
        :param id: The ID of the server to retrieve.
        :return: A Server object representing the Nova server.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # Get a specific server (for example, the first one)
        server = conn.compute.get_server(id)
        return Server(name=server.name, id=server.id, status=server.status)
