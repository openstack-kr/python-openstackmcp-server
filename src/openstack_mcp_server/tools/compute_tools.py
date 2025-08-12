from typing import Any

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

        mcp.tool()(self.get_servers)
        mcp.tool()(self.get_server)
        mcp.tool()(self.create_server)

    def get_servers(self) -> list[Server]:
        """
        Get the list of Compute servers.

        :return: A list of Server objects.
        """
        conn = get_openstack_conn()
        server_list = []
        for server in conn.compute.servers():
            server_list.append(Server(**server))

        return server_list

    def get_server(self, id: str) -> Server:
        """
        Get a specific Compute server.

        :param id: The ID of the server to retrieve.
        :return: A Server object.
        """
        conn = get_openstack_conn()
        server = conn.compute.get_server(id)
        return Server(**server)

    def create_server(
        self,
        name: str,
        image: str,
        flavor: int,
        network: str,
        key_name: str | None = None,
        security_groups: list[str] | None = None,
        user_data: str | None = None,
    ) -> Server:
        """
        Create a new Compute server.

        :param name: The name of the server.
        :param image: The ID of the image to use.
        :param flavor: The (integer) ID of the flavor to use.
        :param network: The ID of the network to attach.
        :param key_name: The name of the key pair to use.
        :param security_groups: A list of security group names to attach.
        :param user_data: User data to pass to the server.
        :return: A Server object
        """
        conn = get_openstack_conn()
        server_params: dict[str, Any] = {
            "name": name,
            "flavorRef": flavor,
            "imageRef": image,
            "networks": [{"uuid": network}],
            "key_name": key_name,
            "security_groups": security_groups,
            "user_data": user_data,
        }
        server_params = {
            k: v for k, v in server_params.items() if v is not None
        }

        resp = conn.compute.create_server(**server_params)
        # NOTE: The create_server method returns a server object with minimal information.
        # To get the full server details, we need to fetch it again.
        server = conn.compute.get_server(resp.id)

        return Server(**server)
